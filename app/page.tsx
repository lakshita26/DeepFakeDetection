"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Navigation } from "@/components/navigation"
import { HeroSection } from "@/components/hero-section"
import { UploadSection } from "@/components/upload-section"
import { ResultsSection } from "@/components/results-section"
import { HistorySection } from "@/components/history-section"
import { AboutSection } from "@/components/about-section"
import type { DetectionResult } from "@/lib/types"

// Re-export DetectionResult type for components that import from page
export type { DetectionResult } from "@/lib/types"

export default function HomePage() {
  const [currentSection, setCurrentSection] = useState<"home" | "upload" | "results" | "history" | "about">("home")
  const [currentResult, setCurrentResult] = useState<DetectionResult | null>(null)
  const [history, setHistory] = useState<DetectionResult[]>([])

  const handleDetectionComplete = (result: DetectionResult) => {
    setCurrentResult(result)
    setHistory((prev) => [result, ...prev])
    setCurrentSection("results")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-secondary/5">
      <Navigation currentSection={currentSection} onSectionChange={setCurrentSection} />

      <main className="relative">
        <AnimatePresence mode="wait">
          {currentSection === "home" && (
            <motion.div
              key="home"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              <HeroSection onGetStarted={() => setCurrentSection("upload")} />
            </motion.div>
          )}

          {currentSection === "upload" && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              <UploadSection onDetectionComplete={handleDetectionComplete} />
            </motion.div>
          )}

          {currentSection === "results" && currentResult && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              <ResultsSection result={currentResult} onNewAnalysis={() => setCurrentSection("upload")} />
            </motion.div>
          )}

          {currentSection === "history" && (
            <motion.div
              key="history"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              <HistorySection
                history={history}
                onSelectResult={(result) => {
                  setCurrentResult(result)
                  setCurrentSection("results")
                }}
              />
            </motion.div>
          )}

          {currentSection === "about" && (
            <motion.div
              key="about"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              <AboutSection />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}
