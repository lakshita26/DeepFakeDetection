"use client"

import { useState, useCallback } from "react"
import { motion } from "framer-motion"
import { useDropzone } from "react-dropzone"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Upload, Camera, X, FileImage } from "lucide-react"
import type { DetectionResult } from "@/lib/types"
import { detectImage } from "@/lib/api"

interface UploadSectionProps {
  onDetectionComplete: (result: DetectionResult) => void
}

export function UploadSection({ onDetectionComplete }: UploadSectionProps) {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      setUploadedFile(file)
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
      setError(null)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".jpeg", ".jpg", ".png", ".webp"],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
  })

  const handleAnalyze = async () => {
    if (!uploadedFile) return

    setIsAnalyzing(true)
    setProgress(0)
    setError(null)

    // Simulate analysis progress
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return 90
        }
        return prev + Math.random() * 15
      })
    }, 200)

    try {
      const result = await detectImage(uploadedFile)

      const resultWithImage = {
        ...result,
        imageUrl: previewUrl || undefined,
      }

      setProgress(100)
      setTimeout(() => {
        onDetectionComplete(resultWithImage)
        setIsAnalyzing(false)
        setProgress(0)
      }, 500)
    } catch (error) {
      console.error("Analysis failed:", error)
      setError(error instanceof Error ? error.message : "Analysis failed")
      setIsAnalyzing(false)
      setProgress(0)
      clearInterval(progressInterval)
    }
  }

  const clearFile = () => {
    setUploadedFile(null)
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
      setPreviewUrl(null)
    }
    setError(null)
  }

  return (
    <section className="min-h-screen py-20 bg-gradient-to-br from-background via-background to-secondary/10">
      <div className="container mx-auto px-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Upload Image for Analysis
            </h2>
            <p className="text-muted-foreground">
              Upload an image to detect if it's been manipulated by deepfake technology
            </p>
          </div>

          <Card className="p-8 bg-card/50 backdrop-blur-sm border-border/50">
            {!uploadedFile ? (
              <motion.div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-300 ${
                  isDragActive
                    ? "border-primary bg-primary/10 shadow-lg shadow-primary/20"
                    : "border-border hover:border-primary/50 hover:bg-primary/5"
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <input {...getInputProps()} />
                <Upload className="h-16 w-16 text-primary mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">
                  {isDragActive ? "Drop your image here" : "Drag & drop an image"}
                </h3>
                <p className="text-muted-foreground mb-4">or click to browse files</p>
                <p className="text-sm text-muted-foreground">Supports: JPEG, PNG, WebP (max 10MB)</p>
              </motion.div>
            ) : (
              <div className="space-y-6">
                <div className="relative">
                  <img
                    src={previewUrl || "/placeholder.svg?height=400&width=600"}
                    alt="Preview"
                    className="w-full max-h-96 object-contain rounded-lg border border-border/50"
                  />
                  <Button variant="destructive" size="sm" className="absolute top-2 right-2" onClick={clearFile}>
                    <X className="h-4 w-4" />
                  </Button>
                </div>

                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <FileImage className="h-4 w-4" />
                  <span>{uploadedFile.name}</span>
                  <span>({(uploadedFile.size / 1024 / 1024).toFixed(1)} MB)</span>
                </div>

                {error && (
                  <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
                    {error}
                  </div>
                )}

                {isAnalyzing && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Analyzing image...</span>
                      <span>{Math.round(progress)}%</span>
                    </div>
                    <Progress value={progress} className="h-2" />
                  </div>
                )}

                <Button onClick={handleAnalyze} disabled={isAnalyzing} className="w-full" size="lg">
                  {isAnalyzing ? (
                    <>
                      <motion.div
                        className="h-4 w-4 border-2 border-current border-t-transparent rounded-full mr-2"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
                      />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Camera className="mr-2 h-4 w-4" />
                      Analyze Image
                    </>
                  )}
                </Button>
              </div>
            )}
          </Card>
        </motion.div>
      </div>
    </section>
  )
}
