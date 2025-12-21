"use client"

import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { AlertTriangle, CheckCircle, Eye, History } from "lucide-react"
import type { DetectionResult } from "@/app/page"
import { formatProbability, getConfidenceLevel, getConfidenceColor } from "@/lib/api"

interface HistorySectionProps {
  history: DetectionResult[]
  onSelectResult: (result: DetectionResult) => void
}

export function HistorySection({ history, onSelectResult }: HistorySectionProps) {
  if (history.length === 0) {
    return (
      <section className="min-h-screen py-20 bg-gradient-to-br from-background via-background to-secondary/10">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Analysis History
            </h2>
            <p className="text-muted-foreground mb-8">Your previous image analyses will appear here</p>
            <Card className="p-12 bg-card/50 backdrop-blur-sm border-border/50">
              <History className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">No analyses yet</p>
              <p className="text-sm text-muted-foreground mt-2">Upload an image to get started</p>
            </Card>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section className="min-h-screen py-20 bg-gradient-to-br from-background via-background to-secondary/10">
      <div className="container mx-auto px-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Analysis History
            </h2>
            <p className="text-muted-foreground">Review your previous image analyses ({history.length} total)</p>
          </div>

          <div className="grid gap-4">
            {history.map((result, index) => {
              const confidenceLevel = getConfidenceLevel(result.probability)
              const confidenceColor = getConfidenceColor(confidenceLevel)

              return (
                <motion.div
                  key={result.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="p-4 bg-card/50 backdrop-blur-sm border-border/50 hover:bg-accent/5 transition-all duration-300 hover:shadow-lg">
                    <div className="flex items-center gap-4">
                      <div className="relative">
                        <img
                          src={result.imageUrl || "/placeholder.svg"}
                          alt="Analysis thumbnail"
                          className="w-16 h-16 object-cover rounded-lg border border-border/50"
                        />
                        {result.metadata?.face_bbox && (
                          <div className="absolute -top-1 -right-1 w-3 h-3 bg-primary rounded-full border-2 border-background" />
                        )}
                      </div>

                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          {result.label === "fake" ? (
                            <AlertTriangle className="h-4 w-4 text-destructive" />
                          ) : (
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          )}
                          <Badge variant={result.label === "fake" ? "destructive" : "default"}>
                            {result.label === "fake" ? "Fake" : "Real"}
                          </Badge>
                          <span className={`text-sm ${confidenceColor}`}>
                            {formatProbability(result.probability)} ({confidenceLevel})
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {result.timestamp.toLocaleDateString()} at {result.timestamp.toLocaleTimeString()}
                        </p>
                      </div>

                      <Button variant="outline" size="sm" onClick={() => onSelectResult(result)}>
                        <Eye className="h-4 w-4 mr-2" />
                        View Details
                      </Button>
                    </div>
                  </Card>
                </motion.div>
              )
            })}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
