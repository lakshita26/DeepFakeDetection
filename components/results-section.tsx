"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { AlertTriangle, CheckCircle, Upload, Download } from "lucide-react"
import type { DetectionResult } from "@/lib/types"
import { getConfidenceLevel, getConfidenceColor } from "@/lib/api"

interface ResultsSectionProps {
  result: DetectionResult
  onNewAnalysis: () => void
}

export function ResultsSection({ result, onNewAnalysis }: ResultsSectionProps) {
  const [showAdvancedMetrics, setShowAdvancedMetrics] = useState(false)

  const isFake = result.probability < 0.5
  const confidencePercentage = Math.round(isFake ? (1 - result.probability) * 100 : result.probability * 100)
  const confidenceLevel = getConfidenceLevel(Math.abs(result.probability - 0.5) * 2)
  const confidenceColor = getConfidenceColor(confidenceLevel)

  const uncertainty = result.uncertainty || 0
  const usedMLModel = result.metadata?.ml_model !== undefined
  const mlInfo = result.metadata?.ml_model

  const handleExportReport = () => {
    const reportData = {
      timestamp: new Date().toISOString(),
      result: isFake ? "Likely Fake" : "Likely Real",
      confidence: confidencePercentage,
      confidenceLevel: confidenceLevel,
      uncertainty: Math.round(uncertainty * 100),
      detectionMethod: usedMLModel ? "ML Model" : "Heuristic",
      modelVersion: usedMLModel ? "Hybrid ML v2.0" : "Heuristic v1.0",
      faceDetected: result.metadata?.face_bbox ? "Yes" : "No",
      preprocessing: result.metadata?.preprocessing?.aligned ? "Face Aligned" : "Standard",
      technicalDetails: result.metadata,
      modelsUsed: result.modelsUsed || [],
    }

    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `deepfake-detection-report-${Date.now()}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <section className="min-h-screen py-4 bg-gradient-to-br from-background via-background to-secondary/10">
      <div className="container mx-auto px-3">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-7xl mx-auto">
          <div className="text-center mb-3">
            <h2 className="text-2xl font-bold mb-1 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Analysis Results
            </h2>
            <p className="text-sm text-muted-foreground">Detailed analysis of your uploaded image</p>
          </div>

          <div className="grid lg:grid-cols-2 gap-3 items-start">
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }}>
              <Card className="p-2 bg-card/50 backdrop-blur-sm border-border/50 overflow-hidden">
                <div className="mb-1.5">
                  <h3 className="text-base font-semibold">Uploaded Image</h3>
                  <p className="text-xs text-muted-foreground">Image being analyzed</p>
                </div>
                <div className="relative w-full max-h-[45vh] rounded-lg overflow-hidden bg-muted/20 border border-border/50">
                  {result.imageUrl ? (
                    <img
                      src={result.imageUrl || "/placeholder.svg"}
                      alt="Analyzed image"
                      className="w-full h-full object-contain"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                      No image available
                    </div>
                  )}
                </div>

                {result.metadata?.face_bbox && (
                  <div className="mt-1.5 p-1.5 rounded-md bg-primary/10 border border-primary/20">
                    <p className="text-xs text-primary font-medium">Face detected and analyzed</p>
                  </div>
                )}
              </Card>
            </motion.div>

            <div className="space-y-3">
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2 }}
              >
                <Card
                  className={`p-3 bg-card/50 backdrop-blur-sm border-border/50 ${
                    isFake
                      ? "border-destructive/50 bg-destructive/5 shadow-lg shadow-destructive/10"
                      : "border-green-500/50 bg-green-500/5 shadow-lg shadow-green-500/10"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    {isFake ? (
                      <AlertTriangle className="h-6 w-6 text-destructive" />
                    ) : (
                      <CheckCircle className="h-6 w-6 text-green-500" />
                    )}
                    <div>
                      <h3 className="text-xl font-bold">{isFake ? "Likely Fake" : "Likely Real"}</h3>
                      <p className={`text-xs ${confidenceColor}`}>
                        {confidencePercentage}% confidence ({confidenceLevel})
                      </p>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span>Confidence Level</span>
                      <span>{confidencePercentage}%</span>
                    </div>
                    <Progress
                      value={confidencePercentage}
                      className={`h-2 ${isFake ? "[&>div]:bg-destructive" : "[&>div]:bg-green-500"}`}
                    />
                  </div>
                </Card>
              </motion.div>

              <Card className="p-3 bg-card/50 backdrop-blur-sm border-border/50">
                <div className="flex justify-between items-center mb-2">
                  <h4 className="text-sm font-semibold">Technical Details</h4>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 text-xs"
                    onClick={() => setShowAdvancedMetrics(!showAdvancedMetrics)}
                  >
                    {showAdvancedMetrics ? "Hide" : "Show"} Advanced
                  </Button>
                </div>
                <div className="space-y-1.5 text-xs">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Detection Method</span>
                    <Badge variant={usedMLModel ? "default" : "secondary"} className="text-xs h-5">
                      {usedMLModel ? "ML Model" : "Heuristic"}
                    </Badge>
                  </div>

                  {usedMLModel && mlInfo && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Model Prediction</span>
                        <Badge variant="outline" className="text-xs h-5">
                          {mlInfo.prediction}
                        </Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Processing Time</span>
                        <span className="text-foreground">{mlInfo.processing_time_ms?.toFixed(1) || "N/A"} ms</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Decision Threshold</span>
                        <span className="text-foreground">{mlInfo.threshold?.toFixed(3) || "0.500"}</span>
                      </div>
                    </>
                  )}

                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Model Version</span>
                    <Badge variant="secondary" className="text-xs h-5">
                      {usedMLModel ? "Hybrid ML v2.0" : "Heuristic v1.0"}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Face Detected</span>
                    <Badge variant={result.metadata?.face_bbox ? "default" : "destructive"} className="text-xs h-5">
                      {result.metadata?.face_bbox ? "Yes" : "No"}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Preprocessing</span>
                    <Badge
                      variant={result.metadata?.preprocessing?.aligned ? "default" : "secondary"}
                      className="text-xs h-5"
                    >
                      {result.metadata?.preprocessing?.aligned ? "Face Aligned" : "Standard"}
                    </Badge>
                  </div>

                  {showAdvancedMetrics && usedMLModel && mlInfo?.feature_importance && (
                    <div className="pt-2 border-t border-border/50">
                      <p className="text-muted-foreground mb-2 font-medium text-xs">Feature Importance:</p>
                      <div className="space-y-1.5">
                        {Object.entries(mlInfo.feature_importance).map(([feature, importance]) => (
                          <div key={feature}>
                            <div className="flex justify-between text-xs mb-0.5">
                              <span className="capitalize">{feature}</span>
                              <span>{Math.round((importance as number) * 100)}%</span>
                            </div>
                            <Progress value={(importance as number) * 100} className="h-1" />
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {result.modelsUsed && result.modelsUsed.length > 0 && (
                    <div className="pt-1.5 border-t border-border/50">
                      <p className="text-muted-foreground mb-1.5 text-xs">Components Used:</p>
                      <div className="flex flex-wrap gap-1.5">
                        {result.modelsUsed.map((model) => (
                          <Badge key={model} variant="outline" className="text-xs h-5">
                            {model}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </Card>

              <div className="flex gap-2">
                <Button onClick={onNewAnalysis} className="flex-1 h-9 text-sm">
                  <Upload className="h-3.5 w-3.5 mr-2" />
                  Analyze Another
                </Button>
                <Button onClick={async () => {
                  try {
                    const res = await fetch('/api/history/save', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify(result)
                    })
                    if (res.status === 401) {
                      // not authenticated
                      window.location.href = '/login'
                      return
                    }
                    if (!res.ok) throw new Error('Failed to save')
                    alert('Saved to your history')
                  } catch (e) {
                    alert('Unable to save result: ' + (e instanceof Error ? e.message : String(e)))
                  }
                }} className="h-9 text-sm" aria-label="Save to history">
                  Save
                </Button>
                <Button variant="outline" onClick={handleExportReport} className="h-9 text-sm bg-transparent">
                  <Download className="h-3.5 w-3.5 mr-2" />
                  Export Report
                </Button>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
