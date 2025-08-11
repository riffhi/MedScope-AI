from flask import Blueprint, request, jsonify, g
import os
import uuid
from app.core.config import settings
from app.models import Report, User
from app.services.ocr_service import OCRService
from app.services.analysis_service import AnalysisService
from app.api.dependencies import login_required
from app.schemas.report import ReportResponse, ReportList
from app.core.database import db
import asyncio

reports_bp = Blueprint('reports', __name__)
ocr_service = OCRService()
analysis_service = AnalysisService()

def process_report_sync(report_id: int, file_path: str):
    """Process report synchronously (OCR + parsing + analysis)"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        report = db.session.query(Report).filter(Report.id == report_id).first()
        if not report:
            return

        report.status = "processing"
        db.session.commit()

        ocr_result = loop.run_until_complete(ocr_service.extract_text_from_image(file_path))

        report.ocr_text = ocr_result.get("text", "")
        report.ocr_confidence = ocr_result.get("confidence", 0.0)

        parsed_data = analysis_service.parse_lab_results(ocr_result.get("text", ""))
        report.parsed_data = parsed_data

        if parsed_data and "tests" in parsed_data:
            patient_info = {
                "age": report.patient_age,
                "sex": report.patient_sex,
                "medications": [],
                "conditions": []
            }

            analysis_result = loop.run_until_complete(analysis_service.analyze_report(parsed_data, patient_info))
            report.analysis_result = analysis_result.dict()

        report.status = "completed"
        db.session.commit()

    except Exception as e:
        report = db.session.query(Report).filter(Report.id == report_id).first()
        if report:
            report.status = "error"
            db.session.commit()
        raise e
    finally:
        loop.close()

@reports_bp.route("/upload", methods=["POST"])
@login_required
def upload_report():
    """Upload and process a medical report"""
    if 'file' not in request.files:
        return jsonify({"detail": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"detail": "No selected file"}), 400

    title = request.form.get('title')
    patient_name = request.form.get('patient_name')
    patient_age = request.form.get('patient_age')
    patient_sex = request.form.get('patient_sex')

    allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.mimetype not in allowed_types:
        return jsonify({"detail": "Invalid file type."}), 400

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > settings.MAX_FILE_SIZE:
        return jsonify({"detail": f"File too large. Maximum size is {settings.MAX_FILE_SIZE // (1024*1024)}MB"}), 400

    try:
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

        file.save(file_path)

        report = Report(
            user_id=g.current_user.id,
            title=title,
            file_path=file_path,
            file_type=file.mimetype,
            file_size=file_size,
            patient_name=patient_name,
            patient_age=patient_age,
            patient_sex=patient_sex,
            report_type="blood",
            status="uploaded"
        )

        db.session.add(report)
        db.session.commit()
        db.session.refresh(report)

        process_report_sync(report.id, file_path)

        return jsonify(ReportResponse.from_orm(report).dict())

    except Exception as e:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"detail": f"Error uploading file: {str(e)}"}), 500

@reports_bp.route("/", methods=["GET"])
@login_required
def list_reports():
    """List user's reports"""
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 100))
    reports = db.session.query(Report).filter(
        Report.user_id == g.current_user.id
    ).offset(skip).limit(limit).all()

    return jsonify([ReportList.from_orm(report).dict() for report in reports])

@reports_bp.route("/<int:report_id>", methods=["GET"])
@login_required
def get_report(report_id: int):
    """Get a specific report"""
    report = db.session.query(Report).filter(
        Report.id == report_id,
        Report.user_id == g.current_user.id
    ).first()

    if not report:
        return jsonify({"detail": "Report not found"}), 404

    return jsonify(ReportResponse.from_orm(report).dict())

@reports_bp.route("/<int:report_id>", methods=["DELETE"])
@login_required
def delete_report(report_id: int):
    """Delete a report"""
    report = db.session.query(Report).filter(
        Report.id == report_id,
        Report.user_id == g.current_user.id
    ).first()

    if not report:
        return jsonify({"detail": "Report not found"}), 404

    if os.path.exists(report.file_path):
        os.remove(report.file_path)

    db.session.delete(report)
    db.session.commit()

    return jsonify({"message": "Report deleted successfully"})