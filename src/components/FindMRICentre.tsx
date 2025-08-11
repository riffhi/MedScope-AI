import React, { useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Search, Navigation, Loader } from "lucide-react";

// --- Step 1: Import Leaflet's CSS ---
import 'leaflet/dist/leaflet.css';

// --- Step 2: Import marker icons for Vite ---
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// --- Step 3: Fix the default icon path for bundlers like Vite ---
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// --- Static Data (can be replaced by an API call) ---
const mriCentresData = [
  { name: "Sonoclinic Diagnostic Center", address: "Opp. Vishwaraj Hospital, Loni Kalbhor", coords: { lat: 18.4556, lng: 74.0219 } },
  { name: "VishwaRaj Hospital", address: "Near Loni Railway Station, Loni Kalbhor", coords: { lat: 18.4571, lng: 74.0253 } },
  { name: "Advanced Imaging Pune", address: "456 FC Road, Pune", coords: { lat: 18.5244, lng: 73.8413 } },
  { name: "Sahyadri Super Speciality Hospital", address: "Deccan Gymkhana, Pune", coords: { lat: 18.5196, lng: 73.8407 } },
  { name: "Noble Hospital", address: "Hadapsar, Pune", coords: { lat: 18.5093, lng: 73.9248 } },
];

// --- Haversine formula to calculate distance ---
const getDistance = (p1: { lat: number, lng: number }, p2: { lat: number, lng: number }) => {
  const R = 6371; // Radius of the Earth in km
  const dLat = (p2.lat - p1.lat) * (Math.PI / 180);
  const dLon = (p2.lng - p1.lng) * (Math.PI / 180);
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(p1.lat * (Math.PI / 180)) * Math.cos(p2.lat * (Math.PI / 180)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c; // Distance in km
};

// --- Helper component to dynamically change the map's center ---
const ChangeView = ({ center, zoom }: { center: L.LatLngExpression, zoom: number }) => {
  const map = useMap();
  map.setView(center, zoom);
  return null;
}

// --- Default map settings ---
const defaultCenter: L.LatLngExpression = [18.5204, 73.8567]; // Pune

// --- The Main React Component ---
const FindMRICentre = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [centres, setCentres] = useState(mriCentresData);
  const [userLocation, setUserLocation] = useState<L.LatLngExpression | null>(null);
  const [mapCenter, setMapCenter] = useState<L.LatLngExpression>(defaultCenter);
  const [isLoading, setIsLoading] = useState(false);

  // Filter centres based on search term
  const filteredCentres = centres.filter(
    (centre) => centre.name.toLowerCase().includes(searchTerm.toLowerCase()) || centre.address.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Get user location, calculate distances, and sort
  const locateAndSort = () => {
    setIsLoading(true);
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser.");
      setIsLoading(false);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const currentUserLocation = { lat: position.coords.latitude, lng: position.coords.longitude };
        const centresWithDistance = mriCentresData.map((centre) => ({
          ...centre,
          distance: getDistance(currentUserLocation, centre.coords),
        }));
        const sortedCentres = centresWithDistance.sort((a, b) => a.distance - b.distance);

        setCentres(sortedCentres);
        setUserLocation([currentUserLocation.lat, currentUserLocation.lng]);
        setMapCenter([currentUserLocation.lat, currentUserLocation.lng]);
        setIsLoading(false);
      },
      () => {
        alert("Unable to retrieve your location.");
        setIsLoading(false);
      }
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Find Nearby MRI Centre</h2>
        <p className="text-slate-400">Search for a center or use your location to find the nearest one.</p>
      </div>
      {/* Main Content Card */}
      <div className="bg-slate-800/60 rounded-xl border border-slate-700/50 p-6">
        {/* Search Bar and Button */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input type="text" placeholder="Search by name or area..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-full bg-slate-700/50 border border-slate-600 rounded-lg pl-10 pr-4 py-2 text-white placeholder-slate-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none" />
          </div>
          <button onClick={locateAndSort} disabled={isLoading} className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors disabled:bg-slate-500 disabled:cursor-not-allowed">
            {isLoading ? <Loader className="w-4 h-4 animate-spin" /> : <Navigation className="w-4 h-4" />}
            <span>{isLoading ? "Locating..." : "Use My Location"}</span>
          </button>
        </div>
        {/* List and Map Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* List of Centres */}
          <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2">
            {filteredCentres.map((centre) => (
              <div key={centre.name} className="bg-slate-700/40 p-4 rounded-lg border border-slate-600/50">
                <h4 className="font-semibold text-white">{centre.name}</h4>
                <p className="text-sm text-slate-300">{centre.address}</p>
                {centre.distance && (
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-xs font-mono bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded">
                      ~ {centre.distance.toFixed(1)} km away
                    </span>
                    <button onClick={() => setMapCenter([centre.coords.lat, centre.coords.lng])} className="text-sm text-blue-400 hover:underline">
                      View on Map
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
          {/* Leaflet Map */}
          <div className="min-h-[400px] bg-slate-700/20 rounded-lg">
            <MapContainer center={mapCenter} zoom={12} style={{ height: "100%", width: "100%", borderRadius: "0.5rem" }}>
              <ChangeView center={mapCenter} zoom={userLocation ? 13 : 11} />
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {userLocation && ( <Marker position={userLocation}><Popup>Your Location</Popup></Marker> )}
              {filteredCentres.map((centre) => (
                <Marker key={centre.name} position={[centre.coords.lat, centre.coords.lng]}>
                  <Popup>{centre.name}</Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FindMRICentre;