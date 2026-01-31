"use client"

import type React from "react"
import { useState, useEffect, useCallback } from "react"
import dynamic from "next/dynamic"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"
import { toast, Toaster } from "sonner"
import {
  Phone,
  MapPin,
  Clock,
  AlertTriangle,
  Flame,
  Shield,
  Truck,
  RefreshCw,
  Navigation,
  FileText,
  Activity,
  Radio,
  Send,
} from "lucide-react"

const EmergencyMap = dynamic(() => import("./emergency-map"), {
  ssr: false,
  loading: () => (
    <div className="flex h-[500px] items-center justify-center rounded-2xl bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="text-center">
        <RefreshCw className="mx-auto h-8 w-8 animate-spin text-gray-400" />
        <p className="mt-2 text-sm text-gray-500">Loading map...</p>
      </div>
    </div>
  ),
})

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080"

interface Emergency {
  id: number
  timestamp: string
  phone_number: string
  audio_path: string
  language: string
  transcript: string
  emergency_type: string
  priority: string
  confidence: number
  keywords: string[] | string
  location_text: string
  latitude: number | null
  longitude: number | null
  status: string
}

const detectEmergencyTypeFromTranscript = (transcript: string, originalType: string): string => {
  if (!transcript) return originalType || "Emergency"

  const transcriptLower = transcript.toLowerCase()

  if (
    /police|robbery|theft|burglary|crime|assault|fight|shooting|gun|weapon|suspect|criminal|officer|dispatch police/i.test(
      transcriptLower,
    )
  ) {
    return "Police"
  }

  if (/fire|smoke|burning|burn|flames|explosion|evacuate|extinguisher|firefighter|blaze|arson/i.test(transcriptLower)) {
    return "Fire"
  }

  if (
    /ambulance|medical|doctor|hospital|injury|injured|accident|bleeding|unconscious|emergency room|er|urgent care|paramedic|oxygen|defibrillator|cpr/i.test(
      transcriptLower,
    )
  ) {
    return "Ambulance"
  }

  return originalType || "Emergency"
}

const determinePriority = (emergencyType: string, transcript: string): string => {
  const detectedType = detectEmergencyTypeFromTranscript(transcript, emergencyType)

  if (detectedType === "Fire") {
    return "CRITICAL"
  }

  if (detectedType === "Ambulance" || detectedType === "Police") {
    return "HIGH"
  }

  return "HIGH"
}

const getLocationDisplay = (emergency: Emergency): string => {
  if (emergency.location_text && emergency.location_text.trim() !== "") {
    return emergency.location_text
  }

  const transcript = emergency.transcript || ""
  const locationPatterns = [
    /near\s+([A-Z][a-zA-Z\s]+(?:Bangalore|Delhi|Mumbai|Chennai|Road|Street|Lane|Colony|Nagar|Park|Building|Tower|Apartment|Society|Complex)?)/gi,
    /at\s+([A-Z][a-zA-Z\s]+(?:Bangalore|Delhi|Mumbai|Chennai|Road|Street|Lane|Colony|Nagar|Park|Building|Tower|Apartment|Society|Complex)?)/gi,
    /in\s+([A-Z][a-zA-Z\s]+(?:Bangalore|Delhi|Mumbai|Chennai|Road|Street|Lane|Colony|Nagar|Park|Building|Tower|Apartment|Society|Complex)?)/gi,
  ]

  for (const pattern of locationPatterns) {
    const match = transcript.match(pattern)
    if (match && match[0]) {
      const location = match[0].replace(/^(near|at|in)\s+/i, "").trim()
      if (location.length > 3) {
        return location
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

export default function OperatorDashboard() {
  const [emergencies, setEmergencies] = useState<Emergency[]>([])
  const [loading, setLoading] = useState(true)
  const [view, setView] = useState<"list" | "map">("list")
  const [dispatching, setDispatching] = useState<number | null>(null)

  const fetchEmergencies = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/calls?status=new`)
      if (!response.ok) throw new Error("Failed to fetch")
      const data = await response.json()
      if (data.success) {
        const filtered = (data.calls || [])
          .filter((call: Emergency) => {
            const priority = determinePriority(call.emergency_type, call.transcript)
            return priority !== "LOW"
          })
          .map((call: Emergency) => ({
            ...call,
            emergency_type: detectEmergencyTypeFromTranscript(call.transcript, call.emergency_type),
            priority: determinePriority(call.emergency_type, call.transcript),
          }))
        setEmergencies(filtered)
      }
    } catch (error) {
      console.error("Fetch error:", error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchEmergencies()
    const interval = setInterval(fetchEmergencies, 3000)
    return () => clearInterval(interval)
  }, [fetchEmergencies])

  const handleDispatch = async (callId: number) => {
    setDispatching(callId)
    try {
      const response = await fetch(`${API_BASE}/api/calls/${callId}/dispatch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      })
      if (!response.ok) throw new Error("Failed to dispatch")
      toast.success("Emergency dispatched successfully")
      fetchEmergencies()
    } catch (error) {
      toast.error("Failed to dispatch emergency")
    } finally {
      setDispatching(null)
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

  const getEmergencyIcon = (type: string) => {
    switch (type?.toLowerCase()) {
      case "fire":
        return <Flame className="h-6 w-6 text-white" />
      case "police":
        return <Shield className="h-6 w-6 text-white" />
      case "ambulance":
      case "medical":
        return <Truck className="h-6 w-6 text-white" />
      default:
        return <AlertTriangle className="h-6 w-6 text-white" />
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority?.toUpperCase()) {
      case "CRITICAL":
        return "bg-red-600 text-white"
      case "HIGH":
        return "bg-orange-500 text-white"
      case "MEDIUM":
        return "bg-yellow-500 text-white"
      default:
        return "bg-blue-600 text-white"
    }
  }

  const getEmergencyBgColor = (type: string) => {
    switch (type?.toLowerCase()) {
      case "fire":
        return "border-l-4 border-l-orange-500 bg-orange-50"
      case "police":
        return "border-l-4 border-l-blue-600 bg-blue-50"
      case "ambulance":
      case "medical":
        return "border-l-4 border-l-red-600 bg-red-50"
      default:
        return "border-l-4 border-l-gray-400 bg-gray-50"
    }
  }

  const getEmergencyTypeIcon = (type: string) => {
    switch (type?.toLowerCase()) {
      case "fire":
        return "bg-orange-500"
      case "police":
        return "bg-blue-600"
      case "ambulance":
      case "medical":
        return "bg-red-600"
      default:
        return "bg-gray-600"
    }
  }

  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp)
      return date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })
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

  const parseKeywords = (keywords: string[] | string): string[] => {
    if (Array.isArray(keywords)) return keywords
    if (typeof keywords === "string") {
      try {
        const parsed = JSON.parse(keywords)
        return Array.isArray(parsed) ? parsed : []
      } catch {
        return keywords
          .split(",")
          .map((k) => k.trim())
          .filter(Boolean)
      }
    }
    return []
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-white via-gray-50 to-gray-100 p-6">
        <div className="mx-auto max-w-7xl">
          <Skeleton className="mb-8 h-12 w-64 bg-gray-200 rounded-lg" />
          <div className="grid gap-6">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-56 rounded-2xl bg-gray-200" />
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <>
      <Toaster
        position="bottom-right"
        richColors
        expand={true}
        containerClassName="!bottom-8 !right-8"
        toastOptions={{
          classNameFunction: ({ type }) => {
            return `!mt-4 !mb-4 !rounded-xl !shadow-xl !z-50`
          },
        }}
      />

      <div className="min-h-screen bg-gradient-to-br from-white via-gray-50 to-gray-100 font-sans">
        <header className="sticky top-0 z-50 border-b border-white/40 bg-white/80 backdrop-blur-2xl shadow-sm">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-red-500 via-red-600 to-red-700 shadow-lg shadow-red-500/30">
                <Activity className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-gray-900">Operator Console</h1>
                <p className="text-sm text-gray-500">Emergency Response System</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 rounded-full bg-white/60 border border-emerald-200/40 backdrop-blur-xl px-4 py-2 shadow-sm">
                <div className="h-2 w-2 animate-pulse rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/50" />
                <span className="text-sm font-semibold text-emerald-700">Live</span>
              </div>
              <Badge className="text-lg px-4 py-2 bg-white/60 border border-gray-200/40 backdrop-blur-xl text-gray-900 hover:bg-white/80 shadow-sm">
                {emergencies.length} Active
              </Badge>
              <Button
                onClick={fetchEmergencies}
                variant="outline"
                className="gap-2 bg-white/60 border border-gray-200/40 backdrop-blur-xl text-gray-700 hover:bg-white/80 shadow-sm transition-all duration-200"
              >
                <RefreshCw className="h-4 w-4" />
                Refresh
              </Button>
              <Link href="/station">
                <Button className="gap-2 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white font-semibold shadow-lg shadow-emerald-500/30 transition-all duration-300 hover:shadow-emerald-500/50">
                  <Radio className="h-4 w-4" />
                  Station
                </Button>
              </Link>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-7xl px-6 py-8">
          <Tabs value={view} onValueChange={(v) => setView(v as "list" | "map")} className="mb-8">
            <TabsList className="bg-white/60 border border-gray-200/40 backdrop-blur-xl shadow-sm">
              <TabsTrigger
                value="list"
                className="px-6 text-gray-700 data-[state=active]:bg-white/80 data-[state=active]:text-gray-900 data-[state=active]:shadow-sm transition-all duration-200"
              >
                List View
              </TabsTrigger>
              <TabsTrigger
                value="map"
                className="px-6 text-gray-700 data-[state=active]:bg-white/80 data-[state=active]:text-gray-900 data-[state=active]:shadow-sm transition-all duration-200"
              >
                Map View
              </TabsTrigger>
            </TabsList>
          </Tabs>

          {view === "map" ? (
            <div className="rounded-2xl overflow-hidden border border-white/40 shadow-lg bg-white/80 backdrop-blur-xl">
              <EmergencyMap emergencies={emergencies} />
            </div>
          ) : emergencies.length === 0 ? (
            <Card className="flex flex-col items-center justify-center py-20 text-center bg-white/60 border border-white/40 backdrop-blur-xl shadow-lg rounded-2xl">
              <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-emerald-100 to-emerald-200 border border-emerald-200/40">
                <Activity className="h-8 w-8 text-emerald-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900">No Active Emergencies</h3>
              <p className="mt-2 text-gray-500">All emergencies have been dispatched</p>
            </Card>
          ) : (
            <div className="grid gap-5 animate-in fade-in duration-500">
              {emergencies.map((emergency, idx) => {
                const keywords = parseKeywords(emergency.keywords)
                const locationDisplay = getLocationDisplay(emergency)
                const mapsUrl = getGoogleMapsUrl(emergency)

                return (
                  <div
                    key={emergency.id}
                    className="animate-in fade-in slide-in-from-bottom-4 duration-500"
                    style={{ animationDelay: `${idx * 50}ms` }}
                  >
                    <Card
                      className={`overflow-hidden border border-white/40 transition-all duration-300 hover:shadow-xl hover:scale-[1.01] bg-white/60 backdrop-blur-xl rounded-2xl ${getEmergencyBgColor(emergency.emergency_type)}`}
                    >
                      <div className="p-6">
                        <div className="flex items-start justify-between gap-6">
                          <div className="flex-1">
                            <div className="flex items-start gap-4 mb-4">
                              <div
                                className={`flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-xl ${getEmergencyTypeIcon(emergency.emergency_type)} shadow-lg transition-all duration-300 group-hover:scale-110`}
                              >
                                {getEmergencyIcon(emergency.emergency_type)}
                              </div>
                              <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                  <h3 className="text-2xl font-bold tracking-tight text-gray-900">
                                    {emergency.emergency_type || "Emergency"}
                                  </h3>
                                  <Badge className={`${getPriorityColor(emergency.priority)} shadow-lg font-bold`}>
                                    {emergency.priority?.toUpperCase() || "UNKNOWN"}
                                  </Badge>
                                </div>

                                <div className="flex items-center gap-2 mb-3">
                                  <Phone className="h-4 w-4 text-gray-600" />
                                  {emergency.phone_number && emergency.phone_number !== "Unknown" ? (
                                    <a
                                      href={`tel:${emergency.phone_number}`}
                                      className="font-semibold text-blue-600 hover:text-blue-700 transition-colors duration-200"
                                    >
                                      {emergency.phone_number}
                                    </a>
                                  ) : (
                                    <span className="text-gray-500">No Caller ID Available</span>
                                  )}
                                </div>

                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                  <Clock className="h-4 w-4" />
                                  <span className="font-medium">{formatTime(emergency.timestamp)}</span>
                                  <span className="text-gray-400">|</span>
                                  <span>{formatDate(emergency.timestamp)}</span>
                                </div>
                              </div>
                            </div>

                            <div className="space-y-4 mt-4">
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

                              <div className="group">
                                <h4 className="text-xs font-bold text-gray-700 uppercase tracking-widest mb-2 flex items-center gap-2">
                                  <MapPin className="h-4 w-4" />
                                  Location
                                </h4>
                                <div className="rounded-xl bg-white/80 p-4 border border-gray-200/60 group-hover:border-gray-300/80 transition-all duration-200">
                                  <p className="font-semibold text-gray-900">
                                    {locationDisplay || "Location not identified"}
                                  </p>
                                  {emergency.latitude && emergency.longitude && (
                                    <p className="text-xs text-gray-500 mt-2">
                                      {emergency.latitude.toFixed(6)}, {emergency.longitude.toFixed(6)}
                                    </p>
                                  )}
                                </div>
                              </div>

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

                          <div className="flex flex-col gap-3">
                            <Button
                              onClick={() => handleDispatch(emergency.id)}
                              disabled={dispatching === emergency.id}
                              className="bg-gradient-to-r from-red-500 via-red-600 to-red-700 hover:from-red-600 hover:via-red-700 hover:to-red-800 text-white font-bold px-6 shadow-lg shadow-red-500/30 hover:shadow-red-500/50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg"
                            >
                              {dispatching === emergency.id ? (
                                <>
                                  <RefreshCw className="h-4 w-4 animate-spin mr-2" />
                                  Sending...
                                </>
                              ) : (
                                <>
                                  <Send className="h-4 w-4 mr-2" />
                                  Dispatch
                                </>
                              )}
                            </Button>
                            {mapsUrl && (
                              <Button
                                onClick={(e) => openGoogleMaps(emergency, e)}
                                variant="outline"
                                className="gap-2 bg-white/60 border border-gray-200/40 backdrop-blur-xl text-gray-700 hover:bg-white/80 transition-all duration-200 shadow-sm rounded-lg"
                              >
                                <Navigation className="h-4 w-4" />
                                Maps
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    </Card>
                  </div>
                )
              })}
            </div>
          )}
        </main>
      </div>
    </>
  )
}
