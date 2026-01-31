"use client"

import type React from "react"
import { useEffect, useState, useCallback } from "react"
import dynamic from "next/dynamic"
import Link from "next/link"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Phone,
  MapPin,
  Clock,
  AlertTriangle,
  Flame,
  Truck,
  Shield,
  Navigation,
  CheckCircle2,
  ChevronRight,
  Radio,
  ExternalLink,
  FileText,
  RefreshCw,
} from "lucide-react"
import { toast } from "sonner"

const EmergencyMap = dynamic(() => import("@/components/emergency-map"), {
  ssr: false,
  loading: () => (
    <div className="flex h-[500px] w-full items-center justify-center rounded-2xl bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="text-center">
        <RefreshCw className="mx-auto h-8 w-8 animate-spin text-gray-400" />
        <p className="text-sm text-gray-500">Loading map...</p>
      </div>
    </div>
  ),
})

interface Emergency {
  id: number
  phone_number: string
  transcript: string
  emergency_type: string
  priority: string
  keywords: string | string[]
  location_text: string
  latitude: number | null
  longitude: number | null
  confidence: number
  status: string
  timestamp: string
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080"

const getLocationDisplay = (emergency: Emergency): string => {
  if (emergency.location_text && emergency.location_text.trim() !== "") {
    return emergency.location_text
  }

  const transcript = emergency.transcript || ""
  const patterns = [
    /near\s+([A-Za-z][A-Za-z0-9\s]+(?:Bangalore|Delhi|Mumbai|Chennai|Road|Street|Lane|Colony|Nagar|Park|Building|Tower|Apartment|Society|Complex|Illuminar)?)/gi,
    /at\s+([A-Za-z][A-Za-z0-9\s]+(?:Bangalore|Delhi|Mumbai|Chennai|Road|Street|Lane|Colony|Nagar|Park|Building|Tower|Apartment|Society|Complex|Illuminar)?)/gi,
    /in\s+([A-Za-z][A-Za-z0-9\s]+(?:Bangalore|Delhi|Mumbai|Chennai|Road|Street|Lane|Colony|Nagar|Park|Building|Tower|Apartment|Society|Complex|Illuminar)?)/gi,
  ]

  for (const pattern of patterns) {
    const matches = transcript.matchAll(pattern)
    for (const match of matches) {
      if (match[1] && match[1].trim().length > 3) {
        return match[1].trim()
      }
    }
  }

  return ""
}

const getGoogleMapsUrl = (emergency: Emergency): string | null => {
  if (emergency.latitude && emergency.longitude) {
    return `https://www.google.com/maps/search/?api=1&query=${emergency.latitude},${emergency.longitude}`
  }

  const locationText = getLocationDisplay(emergency)
  if (locationText) {
    return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(locationText)}`
  }

  return null
}

export default function StationDashboard() {
  const [emergencies, setEmergencies] = useState<Emergency[]>([])
  const [loading, setLoading] = useState(true)
  const [resolving, setResolving] = useState<number | null>(null)
  const [activeView, setActiveView] = useState<"list" | "map">("list")

  const fetchDispatchedEmergencies = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/calls?status=dispatched`)
      if (!response.ok) throw new Error("Failed to fetch dispatched emergencies")
      const data = await response.json()

      if (data.success && data.calls) {
        setEmergencies(data.calls)
      } else {
        setEmergencies([])
      }
      setLoading(false)
    } catch (error) {
      console.error("Error fetching dispatched emergencies:", error)
      setLoading(false)
    }
  }, [])

  const handleResolve = async (callId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    setResolving(callId)
    try {
      const response = await fetch(`${API_BASE}/api/calls/${callId}/resolve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      })

      const data = await response.json()

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Failed to resolve")
      }

      toast.success("Emergency resolved")
      setEmergencies((prev) => prev.filter((e) => e.id !== callId))
    } catch (error) {
      toast.error("Failed to resolve")
    } finally {
      setResolving(null)
    }
  }

  const openGoogleMaps = (emergency: Emergency, e: React.MouseEvent) => {
    e.stopPropagation()
    const url = getGoogleMapsUrl(emergency)
    if (url) {
      window.open(url, "_blank")
    } else {
      toast.error("No location available for this emergency")
    }
  }

  useEffect(() => {
    fetchDispatchedEmergencies()
    const interval = setInterval(fetchDispatchedEmergencies, 3000)
    return () => clearInterval(interval)
  }, [fetchDispatchedEmergencies])

  const getPriorityConfig = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case "critical":
        return { bg: "bg-red-600", text: "text-white" }
      case "high":
        return { bg: "bg-orange-500", text: "text-white" }
      case "medium":
        return { bg: "bg-yellow-500", text: "text-white" }
      default:
        return { bg: "bg-blue-600", text: "text-white" }
    }
  }

  const getEmergencyBgColor = (type: string) => {
    switch (type?.toLowerCase()) {
      case "fire":
        return "border-l-4 border-l-orange-500 bg-orange-50"
      case "ambulance":
      case "medical":
        return "border-l-4 border-l-red-600 bg-red-50"
      case "police":
        return "border-l-4 border-l-blue-600 bg-blue-50"
      default:
        return "border-l-4 border-l-gray-400 bg-gray-50"
    }
  }

  const getTypeConfig = (type: string) => {
    switch (type?.toLowerCase()) {
      case "fire":
        return { icon: Flame, label: "Fire Emergency", color: "text-white", bg: "bg-orange-500" }
      case "ambulance":
      case "medical":
        return { icon: Truck, label: "Medical Emergency", color: "text-white", bg: "bg-red-600" }
      case "police":
        return { icon: Shield, label: "Police Emergency", color: "text-white", bg: "bg-blue-600" }
      default:
        return { icon: AlertTriangle, label: "Emergency", color: "text-white", bg: "bg-gray-600" }
    }
  }

  const parseKeywords = (keywords: string | string[]): string[] => {
    if (!keywords) return []
    if (Array.isArray(keywords)) return keywords
    try {
      const parsed = JSON.parse(keywords)
      return Array.isArray(parsed) ? parsed : [keywords]
    } catch {
      return keywords
        .split(",")
        .map((k) => k.trim())
        .filter(Boolean)
    }
  }

  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp)
      return date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: true })
    } catch {
      return "Unknown"
    }
  }

  const formatDate = (timestamp: string) => {
    try {
      const date = new Date(timestamp)
      return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
    } catch {
      return ""
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-gray-50 to-gray-100">
      <header className="sticky top-0 z-50 border-b border-white/40 bg-white/80 backdrop-blur-2xl shadow-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 via-emerald-600 to-emerald-700 shadow-lg shadow-emerald-500/30">
              <Radio className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-gray-900">Station Console</h1>
              <p className="text-sm text-gray-500">Dispatch Management</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 rounded-full bg-white/60 border border-emerald-200/40 backdrop-blur-xl px-4 py-2 shadow-sm">
              <span className="relative flex h-2.5 w-2.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-500 opacity-75"></span>
                <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-600 shadow-lg shadow-emerald-500/50"></span>
              </span>
              <span className="text-sm font-semibold text-emerald-700">Live</span>
            </div>

            <div className="flex items-center gap-2 rounded-full bg-white/60 border border-blue-200/40 backdrop-blur-xl px-4 py-2 shadow-sm">
              <Truck className="h-4 w-4 text-blue-600" />
              <span className="text-lg font-bold text-blue-600">{emergencies.length}</span>
              <span className="text-sm font-medium text-blue-700">Dispatched</span>
            </div>

            <Link href="/operator">
              <Button className="font-semibold gap-2 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white shadow-lg shadow-red-500/30 transition-all duration-300 hover:shadow-red-500/50">
                <ChevronRight className="h-4 w-4" />
                Operator
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        <div className="mb-8 flex items-center gap-2">
          <div className="inline-flex rounded-lg bg-white/60 border border-gray-200/40 backdrop-blur-xl p-1 shadow-sm">
            <button
              onClick={() => setActiveView("list")}
              className={`rounded-md px-5 py-2.5 text-sm font-semibold transition-all duration-200 ${
                activeView === "list"
                  ? "bg-white/80 text-gray-900 shadow-sm border border-gray-200/60"
                  : "text-gray-600 hover:text-gray-900 hover:bg-white/40"
              }`}
            >
              List View
            </button>
            <button
              onClick={() => setActiveView("map")}
              className={`rounded-md px-5 py-2.5 text-sm font-semibold transition-all duration-200 ${
                activeView === "map"
                  ? "bg-white/80 text-gray-900 shadow-sm border border-gray-200/60"
                  : "text-gray-600 hover:text-gray-900 hover:bg-white/40"
              }`}
            >
              Map View
            </button>
          </div>
        </div>

        {activeView === "list" ? (
          <div className="space-y-5">
            {loading ? (
              <div className="space-y-5">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className="rounded-2xl border border-white/40 bg-white/60 backdrop-blur-xl p-6 shadow-sm animate-pulse"
                  >
                    <div className="flex gap-5">
                      <div className="h-14 w-14 rounded-xl bg-gray-300" />
                      <div className="flex-1 space-y-3">
                        <div className="h-5 w-48 rounded bg-gray-300" />
                        <div className="h-4 w-32 rounded bg-gray-300" />
                      </div>
                      <div className="h-11 w-32 rounded-xl bg-gray-300" />
                    </div>
                  </div>
                ))}
              </div>
            ) : emergencies.length === 0 ? (
              <Card className="border border-white/40 bg-white/60 backdrop-blur-xl shadow-lg rounded-2xl">
                <CardContent className="flex flex-col items-center justify-center py-20">
                  <div className="mb-5 flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-blue-100 to-blue-200 border border-blue-200/40">
                    <Truck className="h-10 w-10 text-blue-600" />
                  </div>
                  <h3 className="mb-2 text-xl font-bold text-gray-900">No Active Dispatches</h3>
                  <p className="text-gray-500">All units are available</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-5 animate-in fade-in duration-500">
                {emergencies.map((emergency, idx) => {
                  const priorityConfig = getPriorityConfig(emergency.priority)
                  const typeConfig = getTypeConfig(emergency.emergency_type)
                  const TypeIcon = typeConfig.icon
                  const locationDisplay = getLocationDisplay(emergency)
                  const mapsUrl = getGoogleMapsUrl(emergency)
                  const keywords = parseKeywords(emergency.keywords)

                  return (
                    <div
                      key={emergency.id}
                      className="animate-in fade-in slide-in-from-bottom-4 duration-500"
                      style={{ animationDelay: `${idx * 50}ms` }}
                    >
                      <Card
                        className={`border border-white/40 transition-all duration-300 hover:shadow-xl hover:scale-[1.01] rounded-2xl overflow-hidden bg-white/60 backdrop-blur-xl ${getEmergencyBgColor(emergency.emergency_type)}`}
                      >
                        <CardContent className="p-0">
                          <div className="p-6">
                            <div className="flex items-start gap-6 mb-4">
                              <div className="flex gap-4 flex-1">
                                <div
                                  className={`flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-xl ${typeConfig.bg} shadow-lg transition-all duration-300`}
                                >
                                  <TypeIcon className={`h-7 w-7 ${typeConfig.color}`} />
                                </div>

                                <div className="flex-1">
                                  <div className="mb-2 flex items-center gap-3">
                                    <h3 className="text-lg font-bold tracking-tight text-gray-900">
                                      {typeConfig.label}
                                    </h3>
                                    <Badge
                                      className={`${priorityConfig.bg} ${priorityConfig.text} text-xs font-bold px-3 py-1 shadow-lg`}
                                    >
                                      {emergency.priority?.toUpperCase()}
                                    </Badge>
                                    <Badge className="bg-emerald-100/80 text-emerald-700 text-xs font-bold px-3 py-1 border border-emerald-300/60 backdrop-blur-sm">
                                      DISPATCHED
                                    </Badge>
                                  </div>

                                  {emergency.phone_number ? (
                                    <a
                                      href={`tel:${emergency.phone_number}`}
                                      className="inline-flex items-center gap-2 rounded-lg bg-white/60 border border-blue-300/40 backdrop-blur-sm px-3 py-1.5 text-sm font-bold text-blue-700 transition-all duration-200 hover:bg-white/80 hover:border-blue-400/60 shadow-sm mb-2"
                                    >
                                      <Phone className="h-4 w-4" />
                                      {emergency.phone_number}
                                    </a>
                                  ) : (
                                    <span className="inline-flex items-center gap-2 rounded-lg bg-white/60 border border-gray-200/60 backdrop-blur-sm px-3 py-1.5 text-sm font-medium text-gray-600 mb-2">
                                      <Phone className="h-4 w-4" />
                                      No Caller ID
                                    </span>
                                  )}

                                  <div className="flex items-center gap-4 text-sm text-gray-600">
                                    <span className="flex items-center gap-1.5 font-medium">
                                      <Clock className="h-4 w-4" />
                                      {formatTime(emergency.timestamp)}
                                    </span>
                                    <span className="text-gray-400">|</span>
                                    <span>{formatDate(emergency.timestamp)}</span>
                                  </div>
                                </div>
                              </div>

                              <Button
                                onClick={(e) => handleResolve(emergency.id, e)}
                                disabled={resolving === emergency.id}
                                className="bg-gradient-to-r from-emerald-500 via-emerald-600 to-emerald-700 hover:from-emerald-600 hover:via-emerald-700 hover:to-emerald-800 px-6 py-5 text-base font-bold text-white disabled:opacity-50 disabled:cursor-not-allowed rounded-lg shadow-lg shadow-emerald-500/30 hover:shadow-emerald-500/50 transition-all duration-300"
                              >
                                {resolving === emergency.id ? (
                                  <>
                                    <RefreshCw className="h-5 w-5 animate-spin mr-2" />
                                    Resolving...
                                  </>
                                ) : (
                                  <>
                                    <CheckCircle2 className="h-5 w-5 mr-2" />
                                    Resolve
                                  </>
                                )}
                              </Button>
                            </div>

                            <div className="space-y-4 border-t border-white/40 pt-4">
                              {/* Transcript */}
                              <div className="group">
                                <h4 className="text-xs font-bold text-gray-700 uppercase tracking-widest mb-2 flex items-center gap-2">
                                  <FileText className="h-4 w-4" />
                                  Call Transcript
                                </h4>
                                <div className="rounded-xl bg-white/80 p-4 border border-gray-200/60 group-hover:border-gray-300/80 transition-all duration-200">
                                  <p className="text-gray-700 text-sm leading-relaxed line-clamp-2 font-medium">
                                    {emergency.transcript || "No transcript available"}
                                  </p>
                                </div>
                              </div>

                              {/* Location */}
                              <div className="group">
                                <h4 className="text-xs font-bold text-gray-700 uppercase tracking-widest mb-2 flex items-center gap-2">
                                  <MapPin className="h-4 w-4" />
                                  Location
                                </h4>
                                <div className="rounded-xl bg-white/80 p-4 border border-gray-200/60 group-hover:border-gray-300/80 transition-all duration-200 flex items-center justify-between">
                                  <div>
                                    <p className="font-semibold text-gray-900">
                                      {locationDisplay || "Location not identified"}
                                    </p>
                                    {emergency.latitude && emergency.longitude && (
                                      <p className="text-xs text-gray-500 mt-2">
                                        {emergency.latitude.toFixed(6)}, {emergency.longitude.toFixed(6)}
                                      </p>
                                    )}
                                  </div>

                                  {mapsUrl && (
                                    <Button
                                      onClick={(e) => openGoogleMaps(emergency, e)}
                                      className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold gap-2 shadow-lg transition-all duration-300"
                                    >
                                      <Navigation className="h-4 w-4" />
                                      <ExternalLink className="h-3 w-3" />
                                    </Button>
                                  )}
                                </div>
                              </div>

                              {/* Keywords */}
                              {keywords.length > 0 && (
                                <div>
                                  <h4 className="text-xs font-bold text-gray-700 uppercase tracking-widest mb-2">
                                    Detected Keywords
                                  </h4>
                                  <div className="flex flex-wrap gap-2">
                                    {keywords.map((keyword, i) => (
                                      <Badge
                                        key={i}
                                        variant="secondary"
                                        className="bg-gray-200/80 text-gray-700 border border-gray-300/60 font-medium transition-all duration-200 hover:bg-gray-300/80"
                                      >
                                        {keyword}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        ) : (
          <div className="rounded-2xl overflow-hidden border border-white/40 shadow-lg bg-white/60 backdrop-blur-xl">
            <EmergencyMap emergencies={emergencies} />
          </div>
        )}
      </main>
    </div>
  )
}
