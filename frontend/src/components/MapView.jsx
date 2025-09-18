// src/components/MapView.jsx
import React, { useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

// Ensure marker icons work with bundlers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const toNum = v => (v === null || v === undefined || v === '' ? NaN : Number(v));

const MapView = ({ geoData }) => {
  const points = useMemo(() => (
    (geoData || [])
      .map(r => ({
        ...r,
        latitude: toNum(r?.latitude ?? r?.lat),
        longitude: toNum(r?.longitude ?? r?.lng ?? r?.lon),
      }))
      .filter(p => Number.isFinite(p.latitude) && Number.isFinite(p.longitude))
  ), [geoData]);

  if (!points.length) {
    return <div className="text-gray-400">No valid latitude/longitude to plot.</div>;
  }

  const center = [points[0].latitude, points[0].longitude];

  return (
    <div style={{ height: 420, width: '100%' }}>
      <MapContainer center={center} zoom={2} style={{ height: '100%', width: '100%' }} scrollWheelZoom>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />
        {points.map((p, i) => (
          <Marker key={p.profile_id ?? i} position={[p.latitude, p.longitude]}>
            <Popup>
              <div>
                <div>profile_id: {String(p.profile_id ?? '')}</div>
                <div>wmo: {String(p.float_wmo_id ?? '')}</div>
                <div>lat: {p.latitude}, lon: {p.longitude}</div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default MapView;


