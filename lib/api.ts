import type { DetectionResult } from "./types"

export async function detectImage(file: File): Promise<DetectionResult> {
  const formData = new FormData()
  formData.append("image", file)

  try {
    const response = await fetch("/api/detect", {
      method: "POST",
      body: formData,
    })

    const contentType = response.headers.get("content-type")
    if (!contentType || !contentType.includes("application/json")) {
      throw new Error("Server returned non-JSON response")
    }

    if (!response.ok) {
      let errorMessage = "Detection failed"
      try {
        const error = await response.json()
        errorMessage = error.error || errorMessage
      } catch {
        // If we can't parse the error response, use default message
      }
      throw new Error(errorMessage)
    }

    const result = await response.json()

    return {
      ...result,
      timestamp: new Date(result.timestamp),
    }
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error("Failed to analyze image")
  }
}

export function formatProbability(probability: number): string {
  return `${(probability * 100).toFixed(1)}%`
}

export function getConfidenceLevel(probability: number): "low" | "medium" | "high" {
  const distance = Math.abs(probability - 0.5)
  if (distance < 0.2) return "low"
  if (distance < 0.35) return "medium"
  return "high"
}

export function getConfidenceColor(level: "low" | "medium" | "high"): string {
  switch (level) {
    case "low":
      return "text-yellow-500"
    case "medium":
      return "text-blue-500"
    case "high":
      return "text-green-500"
  }
}

export function getUncertaintyLevel(uncertainty: number): "low" | "medium" | "high" {
  if (uncertainty < 0.3) return "low"
  if (uncertainty < 0.6) return "medium"
  return "high"
}

export function getUncertaintyMessage(uncertainty: number): string {
  const level = getUncertaintyLevel(uncertainty)
  switch (level) {
    case "low":
      return "High confidence in result"
    case "medium":
      return "Moderate confidence"
    case "high":
      return "Low confidence - ambiguous image"
  }
}
