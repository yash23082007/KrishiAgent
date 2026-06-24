"use client";

import { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import Link from "next/link";
import { Case } from "@/lib/types";

// Configure default leaflet marker icons to avoid missing assets issues on build
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

interface DiseaseMapProps {
  cases: Case[];
  height?: string;
  center?: [number, number];
  zoom?: number;
}

// Custom Marker Generator based on Severity
const getSeverityColor = (severity?: string) => {
  if (severity === "critical") return "#ef4444"; // red
  if (severity === "high") return "#f97316"; // orange
  if (severity === "medium") return "#eab308"; // yellow
  return "#22c55e"; // green
};

const createMarkerIcon = (color: string) => {
  return L.divIcon({
    className: "custom-marker-icon",
    html: `<div style="background-color: ${color}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 8px ${color};"></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
  });
};

function ChangeView({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
}

export default function DiseaseMap({
  cases,
  height = "600px",
  center = [27.7011, 74.4712], // Sujangarh/Churu Rajasthan center
  zoom = 8,
}: DiseaseMapProps) {
  
  // Filter cases with valid coordinates
  const validCases = cases.filter(c => c.location_lat && c.location_lon);

  return (
    <div 
      className="relative rounded-2xl overflow-hidden border border-zinc-800 shadow-xl"
      style={{ height }}
    >
      <MapContainer 
        center={center} 
        zoom={zoom} 
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        <ChangeView center={center} zoom={zoom} />
        
        {/* Dark Map Tiles */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {validCases.map((c) => {
          const color = getSeverityColor(c.severity);
          const icon = createMarkerIcon(color);
          
          return (
            <Marker 
              key={c.id} 
              position={[c.location_lat!, c.location_lon!]} 
              icon={icon}
            >
              <Popup>
                <div className="text-zinc-200">
                  <div className="font-bold capitalize text-sm border-b border-zinc-700 pb-1 mb-1">
                    {c.crop} Disease Alert
                  </div>
                  <div className="text-xs space-y-1">
                    <div>
                      <span className="text-zinc-400 font-semibold">Diagnosis: </span>
                      <span className="capitalize">{c.disease}</span>
                    </div>
                    <div>
                      <span className="text-zinc-400 font-semibold">Severity: </span>
                      <span 
                        style={{ color }} 
                        className="font-bold uppercase text-[10px]"
                      >
                        {c.severity}
                      </span>
                    </div>
                    <div>
                      <span className="text-zinc-400 font-semibold">District: </span>
                      <span>{c.district}</span>
                    </div>
                  </div>
                  <div className="mt-3 text-right">
                    <Link
                      href={`/cases/${c.id}`}
                      className="text-[10px] text-green-400 font-bold hover:underline"
                    >
                      View Details &rarr;
                    </Link>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {/* Floating Map Legend */}
      <div className="absolute bottom-6 left-6 z-[1000] bg-zinc-950/90 border border-zinc-800 p-4 rounded-xl backdrop-blur-md">
        <h4 className="text-xs font-bold text-white mb-2 uppercase tracking-wider">Outbreak Severity</h4>
        <div className="space-y-1.5 text-xs text-zinc-400">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-red-500 border border-white/20"></span>
            <span>Critical</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-orange-500 border border-white/20"></span>
            <span>High</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-yellow-500 border border-white/20"></span>
            <span>Medium</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-green-500 border border-white/20"></span>
            <span>Low</span>
          </div>
        </div>
      </div>
    </div>
  );
}
