/**
 * Python ML Model Integration
 * Handles communication between Next.js and Python ML models
 */

import { spawn } from "child_process"
import path from "path"
import fs from "fs"
import { promisify } from "util"

const writeFile = promisify(fs.writeFile)
const unlink = promisify(fs.unlink)
const mkdir = promisify(fs.mkdir)

export interface MLPrediction {
  is_fake: boolean
  confidence: number
  probability_real: number
  probability_fake: number
  threshold: number
  prediction: "REAL" | "FAKE"
  processing_time_ms: number
  feature_importance?: {
    lbph: number
    fisherface: number
    efficientnet: number
  }
}

export interface MLResult {
  success: boolean
  prediction?: MLPrediction
  error?: string
}

/**
 * Check if Python ML model is available
 */
export async function isPythonMLAvailable(): Promise<boolean> {
  return new Promise((resolve) => {
    const modelPath = path.join(process.cwd(), "ml", "models", "best_model.pth")
    resolve(fs.existsSync(modelPath))
  })
}

/**
 * Run Python ML inference on an image
 */
export async function runPythonInference(imageBuffer: Buffer, fileName: string): Promise<MLResult> {
  try {
    // Create temp directory if it doesn't exist
    const tempDir = path.join(process.cwd(), "temp")
    await mkdir(tempDir, { recursive: true })

    // Save image temporarily
    const tempImagePath = path.join(tempDir, `${Date.now()}-${fileName}`)
    await writeFile(tempImagePath, imageBuffer)

    // Run Python inference
    const result = await executePythonScript(tempImagePath)

    // Clean up temp file
    try {
      await unlink(tempImagePath)
    } catch (e) {
      console.warn("Failed to delete temp file:", e)
    }

    return result
  } catch (error) {
    console.error("Python ML inference error:", error)
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    }
  }
}

/**
 * Execute Python script and parse JSON output
 */
function executePythonScript(imagePath: string): Promise<MLResult> {
  return new Promise((resolve) => {
    const pythonPath = "python3" // or 'python' depending on system
    const scriptPath = path.join(process.cwd(), "ml", "api_bridge.py")

    const pythonProcess = spawn(pythonPath, [scriptPath, imagePath])

    let stdout = ""
    let stderr = ""

    pythonProcess.stdout.on("data", (data) => {
      stdout += data.toString()
    })

    pythonProcess.stderr.on("data", (data) => {
      stderr += data.toString()
    })

    pythonProcess.on("close", (code) => {
      if (code !== 0) {
        console.error("Python script error:", stderr)
        resolve({
          success: false,
          error: `Python script failed with code ${code}: ${stderr}`,
        })
        return
      }

      try {
        const result = JSON.parse(stdout)
        resolve(result)
      } catch (e) {
        console.error("Failed to parse Python output:", stdout)
        resolve({
          success: false,
          error: "Failed to parse Python output",
        })
      }
    })

    pythonProcess.on("error", (error) => {
      console.error("Failed to start Python process:", error)
      resolve({
        success: false,
        error: `Failed to start Python: ${error.message}`,
      })
    })
  })
}

/**
 * Convert ML prediction to app format
 */
export function convertMLToAppFormat(mlResult: MLPrediction) {
  return {
    id: Math.random().toString(36).substring(7),
    label: mlResult.is_fake ? ("fake" as const) : ("real" as const),
    probability: mlResult.probability_real, // Probability of being real
    confidence: mlResult.confidence,
    uncertainty: 1 - mlResult.confidence,
    timestamp: new Date().toISOString(),
    imageUrl: `/placeholder.svg?height=400&width=400&query=${
      mlResult.is_fake
        ? `deepfake-detected-${Math.round(mlResult.confidence * 100)}percent-confidence`
        : `authentic-real-image-${Math.round(mlResult.confidence * 100)}percent-confidence`
    }`,
    metadata: {
      face_bbox: [100, 100, 200, 200] as [number, number, number, number],
      preprocessing: { aligned: true },
      classical_features: {
        lbph_len: 256,
        fisher_len: 100,
      },
      ml_model: {
        prediction: mlResult.prediction,
        threshold: mlResult.threshold,
        processing_time_ms: mlResult.processing_time_ms,
        feature_importance: mlResult.feature_importance,
      },
      analysis_details: {
        overall_assessment: mlResult.is_fake
          ? `Deepfake detected by ML model with ${Math.round(mlResult.confidence * 100)}% confidence`
          : `Authentic image verified by ML model with ${Math.round(mlResult.confidence * 100)}% confidence`,
      },
    },
    gradcam_url: `/placeholder.svg?height=400&width=400&query=${
      mlResult.is_fake
        ? `red-orange-heatmap-deepfake-artifacts-${Math.round(mlResult.confidence * 100)}confidence`
        : `blue-green-heatmap-authentic-features-${Math.round(mlResult.confidence * 100)}confidence`
    }`,
  }
}
