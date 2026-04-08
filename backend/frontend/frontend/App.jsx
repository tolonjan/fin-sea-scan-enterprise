import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const API = "https://RENDER-URL-TÄHÄN";

export default function App() {
  const [ships, setShips] = useState([]);

  useEffect(() => {
    fetch(`${API}/enterprise/intelligence`, {
      headers: { "x-api-key": "demo_key_123" }
    })
      .then(res => res.json())
      .then(setShips);
  }, []);

  return (
    <MapContainer center={[60,24]} zoom={6} style={{ height:"100vh" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {ships.map((s,i)=>(
        <Marker key={i} position={[s.lat, s.lon]}>
          <Popup>
            {s.mmsi}<br/>
            {s.speed}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
