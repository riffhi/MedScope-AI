from flask import Blueprint, request, jsonify
import numpy as np
import tempfile
import os
from pathlib import Path
from werkzeug.utils import secure_filename

visualization_bp = Blueprint('visualization', __name__)

# Import medical imaging libraries
try:
    import monai
    from monai.transforms import (
        LoadImage, EnsureChannelFirst, Orientation, Spacing, 
        ScaleIntensity, SpatialPad, CenterSpatialCrop, Compose
    )
    from monai.data import MetaTensor
    from monai.utils import first
    import torch
    HAS_MONAI = True
    print(f"MONAI version: {monai.__version__}")
except ImportError as e:
    HAS_MONAI = False
    print(f"MONAI not available: {e}")

try:
    import nibabel as nib
    HAS_NIBABEL = True
    print(f"NiBabel available: version {nib.__version__}")
except ImportError as e:
    HAS_NIBABEL = False
    print(f"NiBabel not available: {e}")

try:
    import pydicom
    HAS_PYDICOM = True
    print(f"PyDICOM available: version {pydicom.__version__}")
except ImportError as e:
    HAS_PYDICOM = False
    print(f"PyDICOM not available: {e}")

try:
    import SimpleITK as sitk
    HAS_SITK = True
    print(f"SimpleITK available: version {sitk.Version_VersionString()}")
except ImportError as e:
    HAS_SITK = False
    print(f"SimpleITK not available: {e}")

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'uploads')
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
ALLOWED_EXTENSIONS = {'.nii', '.nii.gz', '.dcm', '.mhd', '.mha', '.nrrd', '.img', '.hdr'}

# Make sure the uploads directory exists with proper permissions
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    print(f"Created upload directory: {UPLOAD_FOLDER}")
    # Test if we can write to it
    test_file = os.path.join(UPLOAD_FOLDER, '.test_write_permissions')
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
    print(f"Upload directory is writable: {UPLOAD_FOLDER}")
except Exception as e:
    print(f"Warning: Issue with upload directory {UPLOAD_FOLDER}: {e}")

def allowed_file(filename):
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

def process_volume_for_plotly(volume, spacing=(1.0, 1.0, 1.0)):
    """Process volume data for Plotly 3D visualization"""
    # Normalize the image data for better visualization
    img = volume.astype(np.float32)
    
    # Remove extreme outliers and enhance contrast
    if img.max() > img.min():
        p2, p98 = np.percentile(img[img > 0], [2, 98])
        img = np.clip(img, p2, p98)
        # Normalize to 0-255 range
        img = ((img - img.min()) / (img.max() - img.min())) * 255
    
    # Smart downsampling for performance while maintaining quality
    max_dim = 100
    if max(img.shape) > max_dim:
        factor = max(img.shape) // max_dim + 1
        img = img[::factor, ::factor, ::factor]
        spacing = tuple(s * factor for s in spacing)
    
    # Create coordinate grids
    x, y, z = np.mgrid[0:img.shape[0]:1, 0:img.shape[1]:1, 0:img.shape[2]:1]
    
    # Scale coordinates by spacing for accurate proportions
    x_coords = (x.flatten() * spacing[0]).tolist()
    y_coords = (y.flatten() * spacing[1]).tolist()
    z_coords = (z.flatten() * spacing[2]).tolist()
    values = img.flatten().tolist()
    
    # Enhanced thresholding for better visualization
    non_zero = [v for v in values if v > 0]
    if len(non_zero) > 0:
        isomin = float(np.percentile(non_zero, 15))
        isomax = float(np.percentile(non_zero, 90))
    else:
        isomin = float(min(values)) if values else 0.0
        isomax = float(max(values)) if values else 1.0
    
    # Convert numpy values to standard Python types for JSON serialization
    shape_list = [int(dim) for dim in img.shape]
    spacing_list = [float(s) for s in spacing]
    
    return {
        'x': x_coords,
        'y': y_coords,
        'z': z_coords,
        'values': values,
        'isomin': isomin,
        'isomax': isomax,
        'shape': shape_list,
        'spacing': spacing_list
    }

def load_medical_image_with_monai(file_path):
    """Load medical image using MONAI transforms with comprehensive preprocessing"""
    try:
        if not HAS_MONAI:
            raise ImportError("MONAI not available")
            
        print(f"Loading medical image: {file_path}")
        
        # Create MONAI transform pipeline
        transforms = Compose([
            LoadImage(image_only=False, ensure_channel_first=True, reader="ITKReader"),
            EnsureChannelFirst(),
            Orientation(axcodes="RAS"),  # Standard orientation
            Spacing(pixdim=(1.0, 1.0, 1.0), mode="bilinear"),  # Resample to 1mm spacing
            ScaleIntensity(minv=0.0, maxv=1.0),  # Normalize intensity
        ])
        
        # Load and transform the image
        data = transforms(file_path)
        
        if isinstance(data, (tuple, list)):
            img_tensor, meta_dict = data
        else:
            img_tensor = data
            meta_dict = data.meta if hasattr(data, 'meta') else {}
        
        print(f"Image tensor shape: {img_tensor.shape}")
        print(f"Image tensor type: {type(img_tensor)}")
        
        # Convert to numpy array
        if torch.is_tensor(img_tensor):
            img_array = img_tensor.cpu().numpy()
        else:
            img_array = np.array(img_tensor)
        
        # Remove channel dimension if it's the first dimension
        if len(img_array.shape) == 4 and img_array.shape[0] == 1:
            img_array = img_array.squeeze(0)
        elif len(img_array.shape) == 4:
            # If multiple channels, take the first one
            img_array = img_array[0]
        
        # Ensure we have a 3D array
        if len(img_array.shape) == 2:
            img_array = np.expand_dims(img_array, axis=2)
        elif len(img_array.shape) > 3:
            # Take first 3 dimensions
            img_array = img_array[:, :, :, 0] if len(img_array.shape) == 4 else img_array
        
        print(f"Final array shape: {img_array.shape}")
        
        # Extract spacing from metadata
        if hasattr(img_tensor, 'meta') and 'pixdim' in img_tensor.meta:
            spacing = img_tensor.meta['pixdim'][1:4].tolist()  # Skip first element (usually temporal)
        elif isinstance(meta_dict, dict) and 'pixdim' in meta_dict:
            pixdim = meta_dict['pixdim']
            if torch.is_tensor(pixdim):
                spacing = pixdim[1:4].cpu().numpy().tolist()
            else:
                spacing = list(pixdim[1:4])
        else:
            spacing = [1.0, 1.0, 1.0]  # Default spacing
            
        # Ensure positive spacing values
        spacing = [abs(s) if s != 0 else 1.0 for s in spacing[:3]]
        
        print(f"Extracted spacing: {spacing}")
        
        # Scale intensity back to reasonable range for visualization
        img_array = img_array * 255.0
        
        return img_array.astype(np.float32), tuple(spacing)
        
    except Exception as e:
        print(f"MONAI loading failed: {e}")
        # Fallback to nibabel or SimpleITK
        return load_medical_image_fallback(file_path)

def load_medical_image_fallback(file_path):
    """Fallback image loading without MONAI"""
    file_ext = Path(file_path).suffix.lower()
    error_messages = []
    
    # Debug information
    print(f"Attempting to load file: {file_path}")
    print(f"File extension: {file_ext}")
    print(f"Library availability: NiBabel: {HAS_NIBABEL}, PyDICOM: {HAS_PYDICOM}, SimpleITK: {HAS_SITK}")
    
    # For .nii.gz files, we need to check for .gz in the path, not just as an extension
    is_nifti = file_ext in ['.nii'] or file_path.lower().endswith('.nii.gz')
    
    if is_nifti and HAS_NIBABEL:
        try:
            print(f"Trying to load NIfTI file with NiBabel: {file_path}")
            img = nib.load(file_path)
            img_array = np.asarray(img.get_fdata())
            spacing = tuple(abs(x) for x in img.header.get_zooms()[:3])
            print(f"Successfully loaded with NiBabel. Shape: {img_array.shape}, Spacing: {spacing}")
            return img_array, spacing
        except Exception as e:
            error_msg = f"NiBabel failed: {str(e)}"
            print(error_msg)
            error_messages.append(error_msg)
        
    elif file_ext == '.dcm' and HAS_PYDICOM:
        try:
            print(f"Trying to load DICOM file with PyDICOM: {file_path}")
            ds = pydicom.dcmread(file_path, force=True)
            img_array = ds.pixel_array
            
            # Try to get spacing
            try:
                pixel_spacing = ds.PixelSpacing
                slice_thickness = getattr(ds, 'SliceThickness', 1.0)
                spacing = (float(pixel_spacing[0]), float(pixel_spacing[1]), float(slice_thickness))
            except Exception as spacing_error:
                print(f"Could not get spacing from DICOM, using default. Error: {spacing_error}")
                spacing = (1.0, 1.0, 1.0)
            
            # Ensure 3D
            if len(img_array.shape) == 2:
                img_array = np.expand_dims(img_array, axis=2)
                
            print(f"Successfully loaded with PyDICOM. Shape: {img_array.shape}, Spacing: {spacing}")
            return img_array, spacing
        except Exception as e:
            error_msg = f"PyDICOM failed: {str(e)}"
            print(error_msg)
            error_messages.append(error_msg)
        
    # Try SimpleITK as a last resort for all formats
    if HAS_SITK:
        try:
            print(f"Trying to load file with SimpleITK: {file_path}")
            img = sitk.ReadImage(file_path)
            img_array = sitk.GetArrayFromImage(img)
            spacing = img.GetSpacing()
            
            # SimpleITK returns (z,y,x) array, so transpose if needed
            if len(img_array.shape) == 3:
                img_array = np.transpose(img_array, (2, 1, 0))
            
            print(f"Successfully loaded with SimpleITK. Shape: {img_array.shape}, Spacing: {spacing}")
            return img_array, tuple(reversed(spacing))
        except Exception as e:
            error_msg = f"SimpleITK failed: {str(e)}"
            print(error_msg)
            error_messages.append(error_msg)
    
    # If we get here, all methods failed
    detailed_error = "; ".join(error_messages)
    error_msg = f"Cannot load file {file_path}. No compatible libraries available or all loading methods failed. Details: {detailed_error}"
    print(error_msg)
    raise ValueError(error_msg)

def generate_demo_volume(volume_type):
    """Generate demo volumes for different medical structures"""
    if volume_type == 'brain':
        # Create brain-like structure
        size = (64, 64, 48)
        x, y, z = np.mgrid[0:size[0], 0:size[1], 0:size[2]]
        
        # Brain shape (ellipsoid)
        brain = ((x - size[0]/2)**2 / (size[0]/2.2)**2 + 
                (y - size[1]/2)**2 / (size[1]/2.2)**2 + 
                (z - size[2]/2)**2 / (size[2]/2.5)**2) < 1
        
        # Add some internal structures
        ventricles = ((x - size[0]/2)**2 / (size[0]/8)**2 + 
                     (y - size[1]/2)**2 / (size[1]/6)**2 + 
                     (z - size[2]/2)**2 / (size[2]/4)**2) < 1
        
        volume = brain.astype(float) * 100
        volume[ventricles] = 200
        
        # Add noise and structures
        noise = np.random.normal(0, 10, size)
        volume = volume + noise
        volume[volume < 0] = 0
        
        return volume.astype(np.float32), (1.0, 1.0, 1.0)
    
    elif volume_type == 'heart':
        # Create heart-like structure
        size = (48, 48, 64)
        x, y, z = np.mgrid[0:size[0], 0:size[1], 0:size[2]]
        
        # Heart shape approximation
        heart = ((x - size[0]/2)**2 / (size[0]/3)**2 + 
                (y - size[1]/2)**2 / (size[1]/3)**2 + 
                (z - size[2]/2.5)**2 / (size[2]/3)**2) < 1
        
        # Chambers
        chamber1 = ((x - size[0]/2.5)**2 / (size[0]/8)**2 + 
                   (y - size[1]/2)**2 / (size[1]/8)**2 + 
                   (z - size[2]/2.2)**2 / (size[2]/6)**2) < 1
        
        chamber2 = ((x - size[0]/1.5)**2 / (size[0]/8)**2 + 
                   (y - size[1]/2)**2 / (size[1]/8)**2 + 
                   (z - size[2]/2.8)**2 / (size[2]/6)**2) < 1
        
        volume = heart.astype(float) * 120
        volume[chamber1 | chamber2] = 50
        
        # Add noise
        noise = np.random.normal(0, 8, size)
        volume = volume + noise
        volume[volume < 0] = 0
        
        return volume.astype(np.float32), (1.2, 1.2, 1.0)
    
    elif volume_type == 'lung':
        # Create lung-like structure
        size = (64, 48, 64)
        x, y, z = np.mgrid[0:size[0], 0:size[1], 0:size[2]]
        
        # Two lung lobes
        lung1 = ((x - size[0]/3)**2 / (size[0]/4)**2 + 
                (y - size[1]/2)**2 / (size[1]/2.5)**2 + 
                (z - size[2]/2)**2 / (size[2]/2.5)**2) < 1
        
        lung2 = ((x - 2*size[0]/3)**2 / (size[0]/4)**2 + 
                (y - size[1]/2)**2 / (size[1]/2.5)**2 + 
                (z - size[2]/2)**2 / (size[2]/2.5)**2) < 1
        
        # Airways (bronchi)
        airways = ((x - size[0]/2)**2 / (size[0]/20)**2 + 
                  (y - size[1]/2)**2 / (size[1]/20)**2) < 1
        
        volume = (lung1 | lung2).astype(float) * 80
        volume[airways] = 200
        
        # Add alveolar structure
        noise = np.random.normal(0, 15, size)
        volume = volume + noise
        volume[volume < 0] = 0
        
        return volume.astype(np.float32), (0.8, 1.0, 0.8)
    
    else:
        raise ValueError(f"Unknown volume type: {volume_type}")

@visualization_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Save uploaded file
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            print(f"File saved to {file_path}. File exists: {os.path.exists(file_path)}")
            print(f"Available libraries - MONAI: {HAS_MONAI}, NiBabel: {HAS_NIBABEL}, PyDICOM: {HAS_PYDICOM}, SimpleITK: {HAS_SITK}")
            
            # Load and process the medical image
            img_array, spacing = load_medical_image_with_monai(file_path)
            
            # Process for visualization
            plot_data = process_volume_for_plotly(img_array, spacing)
            
            # Clean up uploaded file
            os.remove(file_path)
            
            # Calculate stats with proper conversion to Python native types
            dimensions = f"{int(img_array.shape[0])} × {int(img_array.shape[1])} × {int(img_array.shape[2])}"
            voxel_spacing = f"{float(spacing[0]):.2f}, {float(spacing[1]):.2f}, {float(spacing[2]):.2f}"
            data_range = f"[{float(img_array.min()):.1f}, {float(img_array.max()):.1f}]"
            volume_cm3 = f"{float(np.prod(img_array.shape) * np.prod(spacing) / 1000):.1f}"
            
            return jsonify({
                'success': True,
                'name': f"Uploaded: {filename}",
                'data': plot_data,
                'stats': {
                    'dimensions': dimensions,
                    'voxel_spacing': voxel_spacing,
                    'data_range': data_range,
                    'volume_cm3': volume_cm3,
                    'library_used': 'MONAI' if HAS_MONAI else 'Fallback'
                }
            })
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error details: {error_details}")
            
            # Clean up file if it exists
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
                
            # Return detailed error information
            return jsonify({
                'error': f'Error processing file: {str(e)}',
                'details': error_details,
                'libraries_available': {
                    'monai': HAS_MONAI,
                    'nibabel': HAS_NIBABEL,
                    'pydicom': HAS_PYDICOM,
                    'simpleitk': HAS_SITK
                }
            }), 500
    
    return jsonify({'error': 'Invalid file type. Supported: .nii, .nii.gz, .dcm, .mhd, .mha, .nrrd'}), 400

@visualization_bp.route('/generate_volume/<volume_type>', methods=['GET'])
def generate_volume(volume_type):
    """Generate demo volumes for visualization"""
    try:
        img_array, spacing = generate_demo_volume(volume_type)
        plot_data = process_volume_for_plotly(img_array, spacing)
        
        # Calculate stats with proper conversion to Python native types
        dimensions = f"{int(img_array.shape[0])} × {int(img_array.shape[1])} × {int(img_array.shape[2])}"
        voxel_spacing = f"{float(spacing[0]):.2f}, {float(spacing[1]):.2f}, {float(spacing[2]):.2f}"
        data_range = f"[{float(img_array.min()):.1f}, {float(img_array.max()):.1f}]"
        volume_cm3 = f"{float(np.prod(img_array.shape) * np.prod(spacing) / 1000):.1f}"
        
        return jsonify({
            'success': True,
            'name': f"Demo {volume_type.capitalize()} Volume",
            'data': plot_data,
            'stats': {
                'dimensions': dimensions,
                'voxel_spacing': voxel_spacing,
                'data_range': data_range,
                'volume_cm3': volume_cm3,
                'library_used': 'Demo Generator'
            }
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error details: {error_details}")
        return jsonify({'error': f'Error generating {volume_type} volume: {str(e)}', 'details': error_details}), 500

@visualization_bp.route('/status', methods=['GET'])
def get_status():
    """Get the status of available libraries"""
    return jsonify({
        'libraries': {
            'monai': HAS_MONAI,
            'nibabel': HAS_NIBABEL,
            'pydicom': HAS_PYDICOM,
            'simpleitk': HAS_SITK
        },
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': MAX_CONTENT_LENGTH // (1024 * 1024)
    })
