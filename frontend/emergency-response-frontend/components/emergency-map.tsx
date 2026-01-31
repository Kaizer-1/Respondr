"use client"

import { useEffect, useRef } from "react"
import L from "leaflet"
import "leaflet/dist/leaflet.css"

delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
})

interface Emergency {
  id: number
  phone_number: string
  emergency_type: string
  priority: string
  transcript: string
  location_text: string
  latitude: number
  longitude: number
  timestamp: string
}

interface EmergencyMapProps {
  emergencies: Emergency[]
  onSelectEmergency?: (emergency: Emergency) => void
}

export default function EmergencyMap({
  emergencies,
  onSelectEmergency,
}: EmergencyMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null)
  const mapInstance = useRef<L.Map | null>(null)
  const markersLayer = useRef<L.LayerGroup | null>(null)

  useEffect(() => {
    if (!mapContainer.current || mapInstance.current) return

    const map = L.map(mapContainer.current).setView([12.9716, 77.5946], 12)

    L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
      maxZoom: 19,
    }).addTo(map)

    mapInstance.current = map
    markersLayer.current = L.layerGroup().addTo(map)

    return () => {
      map.remove()
      mapInstance.current = null
    }
  }, [])

  useEffect(() => {
    if (!mapInstance.current || !markersLayer.current) return

    markersLayer.current.clearLayers()
    if (emergencies.length === 0) return

    const valid = emergencies.filter((e) => e.latitude && e.longitude)
    if (valid.length === 0) return

    const getColor = (p: string) => {
      switch (p?.toLowerCase()) {
        case "critical":
          return "#ef4444"
        case "high":
          return "#f97316"
        case "medium":
          return "#f59e0b"
        case "low":
          return "#3b82f6"
        default:
          return "#6b7280"
      }
    }

    valid.forEach((e) => {
      const marker = L.marker([e.latitude, e.longitude])

      const icon = L.divIcon({
        className: "",
        iconSize: [40, 40],
        iconAnchor: [20, 20],
        html: `
          <div style="
            width:40px;height:40px;border-radius:50%;
            background:${getColor(e.priority)};
            border:3px solid white;
            display:flex;align-items:center;justify-content:center;
            box-shadow:0 6px 20px rgba(0,0,0,.3)">
            <span style="color:white;font-weight:700;font-size:12px">
              !
            </span>
          </div>
        `,
      })

      marker.setIcon(icon)

      marker.on("click", () => onSelectEmergency?.(e))
      marker.addTo(markersLayer.current!)
    })

    if (valid.length === 1) {
      mapInstance.current.setView([valid[0].latitude, valid[0].longitude], 15)
    } else {
      const group = L.featureGroup(valid.map((e) => L.marker([e.latitude, e.longitude])))
      mapInstance.current.fitBounds(group.getBounds().pad(0.15))
    }
  }, [emergencies, onSelectEmergency])

  return <div ref={mapContainer} className="h-[500px] w-full rounded-xl" />
}
