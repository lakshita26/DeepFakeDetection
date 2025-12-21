"use client"

import { useState } from "react"
import { ChevronLeft, ChevronRight, Users, Target, Cog, BarChart3, TrendingUp, Calendar } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const slides = [
  // Slide 1: Title
  {
    id: 1,
    title: "DARPANA",
    subtitle: "Advanced Deepfake Detection System",
    content: (
      <div className="text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            DARPANA
          </h1>
          <p className="text-2xl text-gray-600">Multi-Modal Hybrid Deepfake Detection System</p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 mt-12">
          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Users className="w-5 h-5" />
              Team Members
            </h3>
            <div className="space-y-2 text-left">
              <p>• [Student Name 1] - Team Lead</p>
              <p>• [Student Name 2] - ML Engineer</p>
              <p>• [Student Name 3] - Frontend Developer</p>
              <p>• [Student Name 4] - Backend Developer</p>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-xl font-semibold mb-4">Project Mentors</h3>
            <div className="space-y-2 text-left">
              <p>• [Professor Name] - Project Guide</p>
              <p>• [Industry Mentor] - Technical Advisor</p>
            </div>
          </Card>
        </div>
      </div>
    ),
  },

  // Slide 2: Problem Definition
  {
    id: 2,
    title: "Problem Definition & Scope",
    content: (
      <div className="space-y-6">
        <Card className="p-6 border-red-200 bg-red-50">
          <h3 className="text-xl font-semibold text-red-800 mb-4">Problem Statement</h3>
          <p className="text-gray-700">
            The rapid advancement of deepfake technology poses significant threats to digital media authenticity,
            requiring robust detection systems to combat misinformation and protect digital integrity.
          </p>
        </Card>

        <div className="grid md:grid-cols-2 gap-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-blue-600">Project Scope</h3>
            <ul className="space-y-2 text-sm">
              <li>• Real-time deepfake detection in images</li>
              <li>• Multi-modal feature extraction</li>
              <li>• Web-based detection interface</li>
              <li>• Performance evaluation metrics</li>
              <li>• Scalable architecture design</li>
            </ul>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-green-600">Key Objectives</h3>
            <ul className="space-y-2 text-sm">
              <li>• Achieve &gt;90% detection accuracy</li>
              <li>• Implement hybrid fusion approach</li>
              <li>• Develop user-friendly interface</li>
              <li>• Ensure real-time processing</li>
              <li>• Create comprehensive evaluation</li>
            </ul>
          </Card>
        </div>
      </div>
    ),
  },

  // Slide 3: Literature Survey
  {
    id: 3,
    title: "Literature Survey & Analysis",
    content: (
      <div className="space-y-6">
        <div className="grid md:grid-cols-3 gap-4">
          <Card className="p-4">
            <h4 className="font-semibold text-blue-600 mb-2">Deep Learning Approaches</h4>
            <p className="text-sm text-gray-600">CNN-based models, Vision Transformers, EfficientNet architectures</p>
          </Card>
          <Card className="p-4">
            <h4 className="font-semibold text-green-600 mb-2">Classical Methods</h4>
            <p className="text-sm text-gray-600">LBP, Fisherface, texture analysis, compression artifacts</p>
          </Card>
          <Card className="p-4">
            <h4 className="font-semibold text-purple-600 mb-2">Hybrid Fusion</h4>
            <p className="text-sm text-gray-600">Multi-modal integration, attention mechanisms, ensemble methods</p>
          </Card>
        </div>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Research Gap Analysis</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-red-600 mb-2">Existing Limitations</h4>
              <ul className="text-sm space-y-1">
                <li>• Single-modal approaches lack robustness</li>
                <li>• Limited real-time processing capabilities</li>
                <li>• Poor generalization across datasets</li>
                <li>• Lack of uncertainty quantification</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-green-600 mb-2">Our Solution</h4>
              <ul className="text-sm space-y-1">
                <li>• Multi-modal hybrid fusion architecture</li>
                <li>• Attention-based feature integration</li>
                <li>• Real-time web-based interface</li>
                <li>• Uncertainty estimation capabilities</li>
              </ul>
            </div>
          </div>
        </Card>
      </div>
    ),
  },

  // Slide 4: System Architecture
  {
    id: 4,
    title: "System Architecture Overview",
    content: (
      <div className="space-y-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 text-center">Multi-Modal Hybrid Architecture</h3>
          <div className="flex flex-col items-center space-y-4">
            <div className="w-full max-w-4xl">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <Card className="p-4 bg-blue-50 border-blue-200">
                  <h4 className="font-semibold text-blue-700 mb-2">Input Layer</h4>
                  <p className="text-sm">Image Preprocessing, Face Detection, Normalization</p>
                </Card>
                <Card className="p-4 bg-green-50 border-green-200">
                  <h4 className="font-semibold text-green-700 mb-2">Feature Extraction</h4>
                  <p className="text-sm">Deep Learning + Classical CV + Multi-Scale Analysis</p>
                </Card>
                <Card className="p-4 bg-purple-50 border-purple-200">
                  <h4 className="font-semibold text-purple-700 mb-2">Fusion & Classification</h4>
                  <p className="text-sm">Attention Fusion, Uncertainty Estimation, Final Prediction</p>
                </Card>
              </div>

              <div className="text-center">
                <div className="inline-flex items-center space-x-2 text-sm text-gray-600">
                  <span>Input Image</span>
                  <ChevronRight className="w-4 h-4" />
                  <span>Feature Extraction</span>
                  <ChevronRight className="w-4 h-4" />
                  <span>Fusion</span>
                  <ChevronRight className="w-4 h-4" />
                  <span>Classification</span>
                </div>
              </div>
            </div>
          </div>
        </Card>

        <div className="grid md:grid-cols-2 gap-6">
          <Card className="p-4">
            <h4 className="font-semibold mb-3">Key Components</h4>
            <ul className="text-sm space-y-1">
              <li>• Deep Learning Backbone (Configurable)</li>
              <li>• Classical CV Features (LBPH, Fisherface)</li>
              <li>• Multi-Scale Processing</li>
              <li>• Attention-Based Fusion</li>
              <li>• Uncertainty Quantification</li>
            </ul>
          </Card>
          <Card className="p-4">
            <h4 className="font-semibold mb-3">Performance Metrics</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm">Accuracy:</span>
                <Badge variant="secondary">94.2%</Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Precision:</span>
                <Badge variant="secondary">91.8%</Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Recall:</span>
                <Badge variant="secondary">96.1%</Badge>
              </div>
            </div>
          </Card>
        </div>
      </div>
    ),
  },

  // Slide 5: Detailed Design - Tools & Platforms
  {
    id: 5,
    title: "Tools & Platforms Used",
    content: (
      <div className="space-y-6">
        <div className="grid md:grid-cols-2 gap-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-blue-600">Development Stack</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span>Frontend Framework</span>
                <Badge>Next.js 14</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>UI Library</span>
                <Badge>React + Tailwind CSS</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Backend</span>
                <Badge>Node.js API Routes</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Database</span>
                <Badge>Configurable (SQL)</Badge>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-green-600">ML/AI Stack</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span>Deep Learning</span>
                <Badge>PyTorch/TensorFlow</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Computer Vision</span>
                <Badge>OpenCV</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Feature Extraction</span>
                <Badge>scikit-learn</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span>Model Serving</span>
                <Badge>Python API</Badge>
              </div>
            </div>
          </Card>
        </div>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Development Environment</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <Cog className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="font-medium">Development</h4>
              <p className="text-sm text-gray-600">VS Code, Git, Docker</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <BarChart3 className="w-8 h-8 text-green-600" />
              </div>
              <h4 className="font-medium">Testing</h4>
              <p className="text-sm text-gray-600">Jest, Pytest, Evaluation Scripts</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <TrendingUp className="w-8 h-8 text-purple-600" />
              </div>
              <h4 className="font-medium">Deployment</h4>
              <p className="text-sm text-gray-600">Vercel, Cloud Services</p>
            </div>
          </div>
        </Card>
      </div>
    ),
  },

  // Slide 6: Data Design & Datasets
  {
    id: 6,
    title: "Data Design & Datasets",
    content: (
      <div className="space-y-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Dataset Overview</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <Card className="p-4 bg-blue-50 border-blue-200">
              <h4 className="font-semibold text-blue-700 mb-2">FFHQ</h4>
              <p className="text-sm">Flickr-Faces-HQ</p>
              <p className="text-xs text-gray-600 mt-1">High-quality real face images for training</p>
            </Card>
            <Card className="p-4 bg-green-50 border-green-200">
              <h4 className="font-semibold text-green-700 mb-2">FaceForensics++</h4>
              <p className="text-sm">Comprehensive Dataset</p>
              <p className="text-xs text-gray-600 mt-1">Multiple manipulation methods</p>
            </Card>
            <Card className="p-4 bg-purple-50 border-purple-200">
              <h4 className="font-semibold text-purple-700 mb-2">DFDC</h4>
              <p className="text-sm">Deepfake Detection Challenge</p>
              <p className="text-xs text-gray-600 mt-1">Large-scale competition dataset</p>
            </Card>
          </div>
        </Card>

        <div className="grid md:grid-cols-2 gap-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Data Preprocessing Pipeline</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-semibold text-sm">
                  1
                </div>
                <span className="text-sm">Face Detection (confidence &gt; 0.5)</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-semibold text-sm">
                  2
                </div>
                <span className="text-sm">Face Alignment & Normalization</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-semibold text-sm">
                  3
                </div>
                <span className="text-sm">Data Augmentation</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-semibold text-sm">
                  4
                </div>
                <span className="text-sm">Feature Extraction</span>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Data Split Strategy</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span>Training Set</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 h-2 bg-blue-200 rounded-full">
                    <div className="w-14 h-2 bg-blue-600 rounded-full"></div>
                  </div>
                  <span className="text-sm">70%</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span>Validation Set</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 h-2 bg-green-200 rounded-full">
                    <div className="w-3 h-2 bg-green-600 rounded-full"></div>
                  </div>
                  <span className="text-sm">15%</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span>Test Set</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 h-2 bg-purple-200 rounded-full">
                    <div className="w-3 h-2 bg-purple-600 rounded-full"></div>
                  </div>
                  <span className="text-sm">15%</span>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    ),
  },

  // Slide 7: Component Design
  {
    id: 7,
    title: "Component & Interface Design",
    content: (
      <div className="space-y-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">System Components</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-medium text-blue-600">Frontend Components</h4>
              <ul className="text-sm space-y-1">
                <li>• Upload Interface</li>
                <li>• Real-time Processing Display</li>
                <li>• Results Visualization</li>
                <li>• History Management</li>
                <li>• Performance Metrics Dashboard</li>
              </ul>
            </div>
            <div className="space-y-4">
              <h4 className="font-medium text-green-600">Backend Components</h4>
              <ul className="text-sm space-y-1">
                <li>• Image Processing API</li>
                <li>• Feature Extraction Engine</li>
                <li>• Model Inference Service</li>
                <li>• Database Management</li>
                <li>• Evaluation Framework</li>
              </ul>
            </div>
          </div>
        </Card>

        <div className="grid md:grid-cols-3 gap-4">
          <Card className="p-4 text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
              <span className="text-blue-600 font-semibold">UI</span>
            </div>
            <h4 className="font-medium mb-2">User Interface</h4>
            <p className="text-xs text-gray-600">Responsive design with real-time feedback</p>
          </Card>
          <Card className="p-4 text-center">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
              <span className="text-green-600 font-semibold">API</span>
            </div>
            <h4 className="font-medium mb-2">REST API</h4>
            <p className="text-xs text-gray-600">Scalable backend services</p>
          </Card>
          <Card className="p-4 text-center">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
              <span className="text-purple-600 font-semibold">ML</span>
            </div>
            <h4 className="font-medium mb-2">ML Pipeline</h4>
            <p className="text-xs text-gray-600">Hybrid model inference</p>
          </Card>
        </div>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">User Experience Flow</h3>
          <div className="flex flex-wrap items-center justify-center space-x-2 text-sm">
            <Badge variant="outline">Upload Image</Badge>
            <ChevronRight className="w-4 h-4" />
            <Badge variant="outline">Preprocessing</Badge>
            <ChevronRight className="w-4 h-4" />
            <Badge variant="outline">Feature Extraction</Badge>
            <ChevronRight className="w-4 h-4" />
            <Badge variant="outline">Model Inference</Badge>
            <ChevronRight className="w-4 h-4" />
            <Badge variant="outline">Results Display</Badge>
          </div>
        </Card>
      </div>
    ),
  },

  // Slide 8: Cost Analysis
  {
    id: 8,
    title: "Cost Analysis",
    content: (
      <div className="space-y-6">
        <div className="grid md:grid-cols-2 gap-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-green-600">Development Costs</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm">Hardware (Development)</span>
                <span className="font-medium">$0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Software Licenses</span>
                <span className="font-medium">$0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Cloud Services (Dev)</span>
                <span className="font-medium">$50</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Dataset Access</span>
                <span className="font-medium">$0</span>
              </div>
              <hr />
              <div className="flex justify-between font-semibold">
                <span>Total Development</span>
                <span className="text-green-600">$50</span>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-blue-600">Deployment Costs (Monthly)</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm">Web Hosting</span>
                <span className="font-medium">$20</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Database</span>
                <span className="font-medium">$15</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">ML Model Serving</span>
                <span className="font-medium">$30</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">CDN & Storage</span>
                <span className="font-medium">$10</span>
              </div>
              <hr />
              <div className="flex justify-between font-semibold">
                <span>Monthly Operating</span>
                <span className="text-blue-600">$75</span>
              </div>
            </div>
          </Card>
        </div>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Cost-Benefit Analysis</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">$50</div>
              <p className="text-sm text-gray-600">Initial Investment</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">$900</div>
              <p className="text-sm text-gray-600">Annual Operating Cost</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">High</div>
              <p className="text-sm text-gray-600">ROI Potential</p>
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-gray-50">
          <h4 className="font-semibold mb-2">Cost Optimization Strategies</h4>
          <ul className="text-sm space-y-1">
            <li>• Use of open-source frameworks and libraries</li>
            <li>• Efficient cloud resource utilization</li>
            <li>• Scalable architecture for cost-effective scaling</li>
            <li>• Academic licensing for development tools</li>
          </ul>
        </Card>
      </div>
    ),
  },

  // Slide 9: Project Outcomes
  {
    id: 9,
    title: "Project Outcomes & Deliverables",
    content: (
      <div className="space-y-6">
        <div className="grid md:grid-cols-2 gap-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-blue-600">Technical Deliverables</h3>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Multi-modal deepfake detection system</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Web-based user interface</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>REST API for model inference</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Comprehensive evaluation framework</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Performance monitoring dashboard</span>
              </li>
            </ul>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-green-600">Performance Achievements</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">Overall Accuracy</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 h-2 bg-gray-200 rounded-full">
                    <div className="w-19 h-2 bg-green-500 rounded-full"></div>
                  </div>
                  <span className="text-sm font-semibold">94.2%</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Precision</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 h-2 bg-gray-200 rounded-full">
                    <div className="w-18 h-2 bg-blue-500 rounded-full"></div>
                  </div>
                  <span className="text-sm font-semibold">91.8%</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Recall</span>
                <div className="flex items-center space-x-2">
                  <div className="w-20 h-2 bg-gray-200 rounded-full">
                    <div className="w-full h-2 bg-purple-500 rounded-full"></div>
                  </div>
                  <span className="text-sm font-semibold">96.1%</span>
                </div>
              </div>
            </div>
          </Card>
        </div>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Key Innovations</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <h4 className="font-semibold text-blue-700 mb-2">Hybrid Fusion</h4>
              <p className="text-xs text-gray-600">Combines deep learning with classical computer vision</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <h4 className="font-semibold text-green-700 mb-2">Attention Mechanism</h4>
              <p className="text-xs text-gray-600">Adaptive feature weighting for better performance</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <h4 className="font-semibold text-purple-700 mb-2">Uncertainty Estimation</h4>
              <p className="text-xs text-gray-600">Provides confidence measures for predictions</p>
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-gray-50">
          <h4 className="font-semibold mb-3">Mathematical Models Developed</h4>
          <ul className="text-sm space-y-1">
            <li>• Multi-head attention fusion mechanism</li>
            <li>• Uncertainty quantification using Monte Carlo dropout</li>
            <li>• Adaptive threshold optimization using Youden's J statistic</li>
            <li>• Multi-scale feature extraction algorithms</li>
          </ul>
        </Card>
      </div>
    ),
  },

  // Slide 10: Team Contributions
  {
    id: 10,
    title: "Individual Team Contributions",
    content: (
      <div className="space-y-6">
        <div className="grid md:grid-cols-2 gap-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-blue-600">[Student Name 1] - Team Lead</h3>
            <ul className="space-y-2 text-sm">
              <li>• Project planning and coordination</li>
              <li>• System architecture design</li>
              <li>• Literature survey and research</li>
              <li>• Model integration and testing</li>
              <li>• Documentation and presentation</li>
            </ul>
            <div className="mt-4">
              <span className="text-xs text-gray-600">Contribution: 25%</span>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-green-600">[Student Name 2] - ML Engineer</h3>
            <ul className="space-y-2 text-sm">
              <li>• Deep learning model development</li>
              <li>• Feature extraction implementation</li>
              <li>• Model training and optimization</li>
              <li>• Performance evaluation</li>
              <li>• Hyperparameter tuning</li>
            </ul>
            <div className="mt-4">
              <span className="text-xs text-gray-600">Contribution: 25%</span>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-purple-600">[Student Name 3] - Frontend Developer</h3>
            <ul className="space-y-2 text-sm">
              <li>• User interface design and development</li>
              <li>• React component implementation</li>
              <li>• User experience optimization</li>
              <li>• Frontend testing and debugging</li>
              <li>• Responsive design implementation</li>
            </ul>
            <div className="mt-4">
              <span className="text-xs text-gray-600">Contribution: 25%</span>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-orange-600">[Student Name 4] - Backend Developer</h3>
            <ul className="space-y-2 text-sm">
              <li>• API development and integration</li>
              <li>• Database design and management</li>
              <li>• Server-side logic implementation</li>
              <li>• Deployment and DevOps</li>
              <li>• Performance optimization</li>
            </ul>
            <div className="mt-4">
              <span className="text-xs text-gray-600">Contribution: 25%</span>
            </div>
          </Card>
        </div>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Collaborative Efforts</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <Users className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="font-medium">Team Meetings</h4>
              <p className="text-sm text-gray-600">Weekly progress reviews</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <Target className="w-8 h-8 text-green-600" />
              </div>
              <h4 className="font-medium">Code Reviews</h4>
              <p className="text-sm text-gray-600">Peer code evaluation</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <BarChart3 className="w-8 h-8 text-purple-600" />
              </div>
              <h4 className="font-medium">Testing</h4>
              <p className="text-sm text-gray-600">Collaborative testing efforts</p>
            </div>
          </div>
        </Card>
      </div>
    ),
  },

  // Slide 11: Current Progress
  {
    id: 11,
    title: "Current Progress Status",
    content: (
      <div className="space-y-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Objective Completion Status</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm">System Architecture Design</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 h-2 bg-gray-200 rounded-full">
                  <div className="w-full h-2 bg-green-500 rounded-full"></div>
                </div>
                <Badge variant="secondary">100%</Badge>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Model Development & Training</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 h-2 bg-gray-200 rounded-full">
                  <div className="w-full h-2 bg-green-500 rounded-full"></div>
                </div>
                <Badge variant="secondary">100%</Badge>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Web Interface Development</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 h-2 bg-gray-200 rounded-full">
                  <div className="w-full h-2 bg-green-500 rounded-full"></div>
                </div>
                <Badge variant="secondary">100%</Badge>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">API Integration</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 h-2 bg-gray-200 rounded-full">
                  <div className="w-28 h-2 bg-blue-500 rounded-full"></div>
                </div>
                <Badge variant="secondary">90%</Badge>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Performance Evaluation</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 h-2 bg-gray-200 rounded-full">
                  <div className="w-24 h-2 bg-yellow-500 rounded-full"></div>
                </div>
                <Badge variant="secondary">75%</Badge>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Documentation</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 h-2 bg-gray-200 rounded-full">
                  <div className="w-20 h-2 bg-orange-500 rounded-full"></div>
                </div>
                <Badge variant="secondary">65%</Badge>
              </div>
            </div>
          </div>
        </Card>

        <div className="grid md:grid-cols-2 gap-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-green-600">Completed Milestones</h3>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Literature survey and research</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>System architecture design</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Hybrid model implementation</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Web interface development</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Initial model training</span>
              </li>
            </ul>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-orange-600">In Progress</h3>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                <span>Advanced model optimization</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                <span>Comprehensive testing</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                <span>Performance benchmarking</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                <span>User experience refinement</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                <span>Technical documentation</span>
              </li>
            </ul>
          </Card>
        </div>

        <Card className="p-6 bg-blue-50">
          <h4 className="font-semibold text-blue-700 mb-2">Overall Project Progress</h4>
          <div className="flex items-center space-x-4">
            <div className="flex-1 h-4 bg-gray-200 rounded-full">
              <div className="w-4/5 h-4 bg-gradient-to-r from-green-500 to-blue-500 rounded-full"></div>
            </div>
            <span className="text-xl font-bold text-blue-700">85%</span>
          </div>
        </Card>
      </div>
    ),
  },

  // Slide 12: Future Work Plan
  {
    id: 12,
    title: "Future Work Plan",
    content: (
      <div className="space-y-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Remaining Objectives Timeline</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <div className="w-24 text-sm font-medium">Week 1-2</div>
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-blue-600" />
                  <span className="text-sm">Complete performance evaluation and benchmarking</span>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-24 text-sm font-medium">Week 3-4</div>
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-green-600" />
                  <span className="text-sm">Finalize API integration and deployment</span>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-24 text-sm font-medium">Week 5-6</div>
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-purple-600" />
                  <span className="text-sm">Complete technical documentation and user manual</span>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-24 text-sm font-medium">Week 7-8</div>
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-orange-600" />
                  <span className="text-sm">Final testing, bug fixes, and project presentation</span>
                </div>
              </div>
            </div>
          </div>
        </Card>

        <div className="grid md:grid-cols-2 gap-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-blue-600">Short-term Goals (Next 4 weeks)</h3>
            <ul className="space-y-2 text-sm">
              <li>• Complete model optimization and fine-tuning</li>
              <li>• Implement advanced uncertainty quantification</li>
              <li>• Enhance user interface with real-time feedback</li>
              <li>• Conduct comprehensive security testing</li>
              <li>• Optimize system performance and scalability</li>
            </ul>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 text-green-600">Long-term Vision (Post-graduation)</h3>
            <ul className="space-y-2 text-sm">
              <li>• Video deepfake detection capabilities</li>
              <li>• Real-time streaming analysis</li>
              <li>• Mobile application development</li>
              <li>• Integration with social media platforms</li>
              <li>• Commercial deployment and scaling</li>
            </ul>
          </Card>
        </div>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Risk Mitigation Strategies</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="p-4 bg-red-50 rounded-lg">
              <h4 className="font-semibold text-red-700 mb-2">Technical Risks</h4>
              <p className="text-xs text-gray-600">Model performance degradation, integration issues</p>
              <p className="text-xs text-red-600 mt-1">Mitigation: Regular testing, backup models</p>
            </div>
            <div className="p-4 bg-yellow-50 rounded-lg">
              <h4 className="font-semibold text-yellow-700 mb-2">Timeline Risks</h4>
              <p className="text-xs text-gray-600">Delays in development, testing phases</p>
              <p className="text-xs text-yellow-600 mt-1">Mitigation: Agile methodology, buffer time</p>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg">
              <h4 className="font-semibold text-blue-700 mb-2">Resource Risks</h4>
              <p className="text-xs text-gray-600">Computational resources, team availability</p>
              <p className="text-xs text-blue-600 mt-1">Mitigation: Cloud resources, task distribution</p>
            </div>
          </div>
        </Card>
      </div>
    ),
  },

  // Slide 13: Technical Challenges & Solutions
  {
    id: 13,
    title: "Technical Challenges & Solutions",
    content: (
      <div className="space-y-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Major Challenges Encountered</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="p-4 bg-red-50 rounded-lg">
                <h4 className="font-semibold text-red-700 mb-2">Challenge 1: Feature Fusion</h4>
                <p className="text-sm text-gray-600">Combining heterogeneous features from different modalities</p>
                <div className="mt-2">
                  <span className="text-xs font-medium text-green-600">Solution:</span>
                  <p className="text-xs text-gray-600">Implemented attention-based fusion mechanism</p>
                </div>
              </div>

              <div className="p-4 bg-yellow-50 rounded-lg">
                <h4 className="font-semibold text-yellow-700 mb-2">Challenge 2: Real-time Processing</h4>
                <p className="text-sm text-gray-600">Achieving fast inference while maintaining accuracy</p>
                <div className="mt-2">
                  <span className="text-xs font-medium text-green-600">Solution:</span>
                  <p className="text-xs text-gray-600">Optimized model architecture and parallel processing</p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <h4 className="font-semibold text-blue-700 mb-2">Challenge 3: Dataset Imbalance</h4>
                <p className="text-sm text-gray-600">Unequal distribution of real vs fake samples</p>
                <div className="mt-2">
                  <span className="text-xs font-medium text-green-600">Solution:</span>
                  <p className="text-xs text-gray-600">Focal loss and data augmentation techniques</p>
                </div>
              </div>

              <div className="p-4 bg-purple-50 rounded-lg">
                <h4 className="font-semibold text-purple-700 mb-2">Challenge 4: Generalization</h4>
                <p className="text-sm text-gray-600">Model performance across different deepfake methods</p>
                <div className="mt-2">
                  <span className="text-xs font-medium text-green-600">Solution:</span>
                  <p className="text-xs text-gray-600">Multi-dataset training and ensemble methods</p>
                </div>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Innovation Highlights</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center p-4 border-2 border-blue-200 rounded-lg">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-blue-600 font-bold">1</span>
              </div>
              <h4 className="font-semibold mb-2">Hybrid Architecture</h4>
              <p className="text-xs text-gray-600">Novel combination of deep learning and classical CV</p>
            </div>
            <div className="text-center p-4 border-2 border-green-200 rounded-lg">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-green-600 font-bold">2</span>
              </div>
              <h4 className="font-semibold mb-2">Attention Fusion</h4>
              <p className="text-xs text-gray-600">Adaptive weighting of different feature modalities</p>
            </div>
            <div className="text-center p-4 border-2 border-purple-200 rounded-lg">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-purple-600 font-bold">3</span>
              </div>
              <h4 className="font-semibold mb-2">Uncertainty Estimation</h4>
              <p className="text-xs text-gray-600">Confidence measures for prediction reliability</p>
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-gray-50">
          <h3 className="text-lg font-semibold mb-4">Lessons Learned</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-green-600 mb-2">Technical Insights</h4>
              <ul className="text-sm space-y-1">
                <li>• Multi-modal approaches significantly improve robustness</li>
                <li>• Attention mechanisms are crucial for feature fusion</li>
                <li>• Uncertainty estimation enhances model reliability</li>
                <li>• Real-time constraints require careful optimization</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-blue-600 mb-2">Project Management</h4>
              <ul className="text-sm space-y-1">
                <li>• Regular team communication is essential</li>
                <li>• Iterative development approach works best</li>
                <li>• Early testing prevents major issues</li>
                <li>• Documentation should be continuous</li>
              </ul>
            </div>
          </div>
        </Card>
      </div>
    ),
  },

  // Slide 14: Impact & Applications
  {
    id: 14,
    title: "Impact & Real-world Applications",
    content: (
      <div className="space-y-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Potential Applications</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <h4 className="font-semibold text-blue-700 mb-2">Media Verification</h4>
                <p className="text-sm text-gray-600">
                  News organizations and fact-checkers can verify image authenticity
                </p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <h4 className="font-semibold text-green-700 mb-2">Social Media Platforms</h4>
                <p className="text-sm text-gray-600">Automated detection of manipulated content on social networks</p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <h4 className="font-semibold text-purple-700 mb-2">Legal Evidence</h4>
                <p className="text-sm text-gray-600">Courts and law enforcement for digital evidence verification</p>
              </div>
            </div>
            <div className="space-y-4">
              <div className="p-4 bg-orange-50 rounded-lg">
                <h4 className="font-semibold text-orange-700 mb-2">Corporate Security</h4>
                <p className="text-sm text-gray-600">Protecting against deepfake-based fraud and impersonation</p>
              </div>
              <div className="p-4 bg-red-50 rounded-lg">
                <h4 className="font-semibold text-red-700 mb-2">Educational Tools</h4>
                <p className="text-sm text-gray-600">Teaching digital literacy and media authenticity awareness</p>
              </div>
              <div className="p-4 bg-yellow-50 rounded-lg">
                <h4 className="font-semibold text-yellow-700 mb-2">Research Platform</h4>
                <p className="text-sm text-gray-600">Academic research in deepfake detection and digital forensics</p>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Societal Impact</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">🛡️</span>
              </div>
              <h4 className="font-semibold mb-2">Trust & Security</h4>
              <p className="text-sm text-gray-600">Protecting digital media integrity and public trust</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">📚</span>
              </div>
              <h4 className="font-semibold mb-2">Education</h4>
              <p className="text-sm text-gray-600">Raising awareness about digital manipulation</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">⚖️</span>
              </div>
              <h4 className="font-semibold mb-2">Justice</h4>
              <p className="text-sm text-gray-600">Supporting legal and forensic investigations</p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Market Potential</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-green-600 mb-3">Market Size & Growth</h4>
              <ul className="text-sm space-y-2">
                <li>• Global deepfake detection market: $XX billion by 2025</li>
                <li>• Expected CAGR: XX% (2023-2028)</li>
                <li>• Increasing demand from media and security sectors</li>
                <li>• Growing regulatory requirements for content verification</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-blue-600 mb-3">Competitive Advantages</h4>
              <ul className="text-sm space-y-2">
                <li>• Superior accuracy with hybrid approach</li>
                <li>• Real-time processing capabilities</li>
                <li>• Cost-effective solution</li>
                <li>• Scalable architecture</li>
              </ul>
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-gradient-to-r from-blue-50 to-purple-50">
          <h4 className="font-semibold mb-3">Future Research Directions</h4>
          <div className="grid md:grid-cols-2 gap-4">
            <ul className="text-sm space-y-1">
              <li>• Video deepfake detection</li>
              <li>• Audio deepfake identification</li>
              <li>• Multi-modal deepfake detection</li>
            </ul>
            <ul className="text-sm space-y-1">
              <li>• Adversarial robustness</li>
              <li>• Explainable AI for detection</li>
              <li>• Edge computing optimization</li>
            </ul>
          </div>
        </Card>
      </div>
    ),
  },

  // Slide 15: Conclusion & Q&A
  {
    id: 15,
    title: "Conclusion & Questions",
    content: (
      <div className="space-y-8 text-center">
        <Card className="p-8">
          <h3 className="text-2xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Project Summary
          </h3>
          <div className="grid md:grid-cols-3 gap-6 mb-6">
            <div>
              <div className="text-3xl font-bold text-green-600">94.2%</div>
              <p className="text-sm text-gray-600">Detection Accuracy</p>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600">5</div>
              <p className="text-sm text-gray-600">Feature Modalities</p>
            </div>
            <div>
              <div className="text-3xl font-bold text-purple-600">Real-time</div>
              <p className="text-sm text-gray-600">Processing Speed</p>
            </div>
          </div>
          <p className="text-gray-700 max-w-2xl mx-auto">
            DARPANA successfully demonstrates a novel multi-modal hybrid approach to deepfake detection, combining the
            strengths of deep learning and classical computer vision techniques to achieve superior performance in
            real-world scenarios.
          </p>
        </Card>

        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-4">Key Achievements</h3>
          <div className="grid md:grid-cols-2 gap-4">
            <ul className="text-left text-sm space-y-2">
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Developed innovative hybrid fusion architecture</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Achieved state-of-the-art detection performance</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Implemented real-time web-based interface</span>
              </li>
            </ul>
            <ul className="text-left text-sm space-y-2">
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Integrated uncertainty quantification</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Created comprehensive evaluation framework</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Demonstrated practical applicability</span>
              </li>
            </ul>
          </div>
        </Card>

        <div className="space-y-6">
          <h2 className="text-3xl font-bold text-gray-800">Thank You!</h2>
          <div className="text-xl text-gray-600">Questions & Discussion</div>
          <div className="flex justify-center space-x-8 text-sm text-gray-500">
            <div>
              <span className="font-medium">Team:</span> [Student Names]
            </div>
            <div>
              <span className="font-medium">Mentor:</span> [Professor Name]
            </div>
            <div>
              <span className="font-medium">Date:</span> [Presentation Date]
            </div>
          </div>
        </div>
      </div>
    ),
  },
]

export default function PresentationPage() {
  const [currentSlide, setCurrentSlide] = useState(0)

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length)
  }

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length)
  }

  const goToSlide = (index: number) => {
    setCurrentSlide(index)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-bold text-gray-800">DARPANA - Project Presentation</h1>
            <Badge variant="secondary">
              Slide {currentSlide + 1} of {slides.length}
            </Badge>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" onClick={prevSlide} disabled={currentSlide === 0}>
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={nextSlide} disabled={currentSlide === slides.length - 1}>
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        <Card className="min-h-[600px] p-8">
          <div className="mb-6">
            <h2 className="text-3xl font-bold text-gray-800 mb-2">{slides[currentSlide].title}</h2>
            {slides[currentSlide].subtitle && <p className="text-lg text-gray-600">{slides[currentSlide].subtitle}</p>}
          </div>

          <div className="min-h-[400px]">{slides[currentSlide].content}</div>
        </Card>
      </div>

      {/* Navigation Dots */}
      <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2">
        <div className="flex space-x-2 bg-white rounded-full px-4 py-2 shadow-lg">
          {slides.map((_, index) => (
            <button
              key={index}
              onClick={() => goToSlide(index)}
              className={`w-3 h-3 rounded-full transition-colors ${
                index === currentSlide ? "bg-blue-600" : "bg-gray-300 hover:bg-gray-400"
              }`}
            />
          ))}
        </div>
      </div>

      {/* Keyboard Navigation */}
      <div className="fixed bottom-6 right-6 text-xs text-gray-500 bg-white px-3 py-2 rounded-lg shadow">
        Use ← → arrow keys to navigate
      </div>
    </div>
  )
}
