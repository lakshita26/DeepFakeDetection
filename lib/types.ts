export interface DetectionResult {
  id: string
  label: "real" | "fake"
  probability: number
  timestamp: Date
  imageUrl: string
  confidence?: number
  uncertainty?: number
  modelsUsed?: string[]
  metadataEnhanced?: {
    ganArtifacts?: {
      spectralScore: number
      textureConsistency: number
      edgeDistribution: number
    }
    diffusionArtifacts?: {
      noiseDistribution: number
      waveletEnergy: number
      frequencyContent: number
    }
    ensembleScores?: {
      ganDetectorScore: number
      diffusionDetectorScore: number
      agreementScore: number
    }
  }
  metadata?: {
    face_bbox?: [number, number, number, number]
    preprocessing?: { aligned: boolean }
    classical_features?: { lbph_len: number; fisher_len: number }
  }
  gradcam_url?: string
}

export type { DetectionResult }
