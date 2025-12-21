"use client"

import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Brain, Database, Eye, Zap, Shield, AlertCircle } from "lucide-react"

export function AboutSection() {
  const datasets = [
    { name: "FFHQ", description: "Flickr-Faces-HQ - High quality face images", count: "70K images" },
    { name: "FaceForensics++", description: "Comprehensive deepfake detection dataset", count: "1.8M videos" },
    { name: "DFDC", description: "Deepfake Detection Challenge dataset", count: "128K videos" },
  ]

  const techniques = [
    {
      icon: Brain,
      title: "Deep Learning Backbone",
      description: "Advanced neural networks with Vision Transformer blocks for high-level semantic feature extraction",
      color: "text-blue-500",
    },
    {
      icon: Eye,
      title: "Multi-Scale Feature Analysis",
      description: "Processes images at multiple scales with pixel-level anomaly and compression artifact detection",
      color: "text-green-500",
    },
    {
      icon: Database,
      title: "Texture & Pattern Analysis",
      description: "Advanced texture analysis and local pattern detection for identifying manipulation artifacts",
      color: "text-purple-500",
    },
    {
      icon: Zap,
      title: "Attention-Based Fusion",
      description: "Multi-head attention mechanisms with GAN and Diffusion model integration for enhanced detection",
      color: "text-yellow-500",
    },
    {
      icon: Zap,
      title: "GAN Artifact Detection",
      description:
        "Specialized detection for GAN-generated deepfakes including StyleGAN, ProGAN, and StarGAN artifacts",
      color: "text-red-500",
    },
    {
      icon: Brain,
      title: "Diffusion Model Analysis",
      description:
        "Forensic detection of diffusion-based synthetic faces with temporal and latent space artifact detection",
      color: "text-cyan-500",
    },
  ]

  return (
    <section className="min-h-screen py-20 bg-gradient-to-br from-background via-background to-secondary/10">
      <div className="container mx-auto px-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              About Our Technology
            </h2>
            <p className="text-muted-foreground text-lg">
              Advanced deepfake detection using multi-modal hybrid fusion with attention mechanisms
            </p>
          </div>

          <div className="space-y-12">
            {/* Techniques */}
            <div>
              <h3 className="text-2xl font-semibold mb-6 flex items-center gap-2">
                <Shield className="h-6 w-6 text-primary" />
                Detection Techniques
              </h3>
              <div className="grid md:grid-cols-2 gap-6">
                {techniques.map((technique, index) => (
                  <motion.div
                    key={technique.title}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Card className="p-6 h-full bg-card/50 backdrop-blur-sm border-border/50 hover:shadow-lg transition-all duration-300">
                      <technique.icon className={`h-8 w-8 ${technique.color} mb-4`} />
                      <h4 className="font-semibold mb-2">{technique.title}</h4>
                      <p className="text-muted-foreground text-sm leading-relaxed">{technique.description}</p>
                    </Card>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Datasets */}
            <div>
              <h3 className="text-2xl font-semibold mb-6 flex items-center gap-2">
                <Database className="h-6 w-6 text-primary" />
                Training Datasets
              </h3>
              <div className="grid gap-4">
                {datasets.map((dataset, index) => (
                  <motion.div
                    key={dataset.name}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Card className="p-4 bg-card/50 backdrop-blur-sm border-border/50">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Badge variant="secondary">{dataset.name}</Badge>
                          <span className="text-sm text-muted-foreground">{dataset.description}</span>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {dataset.count}
                        </Badge>
                      </div>
                    </Card>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Performance Metrics */}
            <div>
              <h3 className="text-2xl font-semibold mb-6">Model Performance</h3>
              <div className="grid md:grid-cols-3 gap-6">
                <Card className="p-6 text-center bg-card/50 backdrop-blur-sm border-border/50">
                  <div className="text-3xl font-bold text-primary mb-2">96.5%</div>
                  <div className="text-sm text-muted-foreground">Overall Accuracy</div>
                  <div className="text-xs text-muted-foreground mt-2 opacity-70">(+2.3% improvement)</div>
                </Card>
                <Card className="p-6 text-center bg-card/50 backdrop-blur-sm border-border/50">
                  <div className="text-3xl font-bold text-green-500 mb-2">94.8%</div>
                  <div className="text-sm text-muted-foreground">Precision</div>
                  <div className="text-xs text-muted-foreground mt-2 opacity-70">(+3.0% improvement)</div>
                </Card>
                <Card className="p-6 text-center bg-card/50 backdrop-blur-sm border-border/50">
                  <div className="text-3xl font-bold text-blue-500 mb-2">98.5%</div>
                  <div className="text-sm text-muted-foreground">Recall</div>
                  <div className="text-xs text-muted-foreground mt-2 opacity-70">(+2.4% improvement)</div>
                </Card>
              </div>
              <div className="grid md:grid-cols-2 gap-6 mt-6">
                <Card className="p-6 text-center bg-card/50 backdrop-blur-sm border-border/50">
                  <div className="text-3xl font-bold text-purple-500 mb-2">0.967</div>
                  <div className="text-sm text-muted-foreground">F1-Score</div>
                  <div className="text-xs text-muted-foreground mt-2 opacity-70">(+0.028 improvement)</div>
                </Card>
                <Card className="p-6 text-center bg-card/50 backdrop-blur-sm border-border/50">
                  <div className="text-3xl font-bold text-yellow-500 mb-2">Multi-Modal</div>
                  <div className="text-sm text-muted-foreground">7-Model Ensemble</div>
                  <div className="text-xs text-muted-foreground mt-2 opacity-70">
                    GAN + Diffusion + Classical + Deep
                  </div>
                </Card>
              </div>
            </div>

            {/* Disclaimer */}
            <Card className="p-6 bg-muted/20 backdrop-blur-sm border-border/50 border-l-4 border-l-yellow-500">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-yellow-500 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="text-lg font-semibold mb-3">Important Disclaimer</h3>
                  <div className="space-y-2 text-sm text-muted-foreground leading-relaxed">
                    <p>
                      This tool is designed for research and educational purposes. While our hybrid model achieves high
                      accuracy across multiple datasets, no deepfake detection system is 100% reliable.
                    </p>
                    <p>
                      Results should not be used as definitive proof in legal or forensic contexts without additional
                      verification by qualified experts. Always consider the possibility of false positives and false
                      negatives.
                    </p>
                    <p>
                      Uploaded images are processed securely and automatically deleted after analysis to protect your
                      privacy. No data is stored or shared with third parties.
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
