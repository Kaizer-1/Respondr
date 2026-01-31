// API client for emergency response backend

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8080"

export interface EmergencyCall {
  id: number
  timestamp: string
  phone_number: string
  audio_path: string
  language: string
  transcript: string
  emergency_type: string
  priority: string
  confidence: number
  keywords: string
  location_text: string
  latitude: number
  longitude: number
  status: string
  assigned_unit?: string
  dispatched_at?: string
  created_at?: string
}

export interface ApiResponse {
  success: boolean
  calls?: EmergencyCall[]
  call?: EmergencyCall
  message?: string
  error?: string
  count?: number
}

export const api = {
  getCalls: async (status?: string): Promise<ApiResponse> => {
    const url = status ? `${API_BASE}/api/calls?status=${status}` : `${API_BASE}/api/calls`
    const response = await fetch(url)
    if (!response.ok) throw new Error("Failed to fetch calls")
    return response.json()
  },

  getCall: async (callId: number): Promise<ApiResponse> => {
    const response = await fetch(`${API_BASE}/api/calls/${callId}`)
    if (!response.ok) throw new Error("Failed to fetch call")
    return response.json()
  },

  dispatchCall: async (callId: number): Promise<ApiResponse> => {
    const response = await fetch(`${API_BASE}/api/calls/${callId}/dispatch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })
    if (!response.ok) throw new Error("Failed to dispatch call")
    return response.json()
  },

  resolveCall: async (callId: number): Promise<ApiResponse> => {
    const response = await fetch(`${API_BASE}/api/calls/${callId}/resolve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    })
    if (!response.ok) throw new Error("Failed to resolve call")
    return response.json()
  },
}
