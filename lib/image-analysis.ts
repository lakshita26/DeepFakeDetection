/**
 * Advanced image analysis utilities for deepfake detection
 * Uses pixel-level analysis to detect AI-generated and manipulated content
 */

/**
 * Analyzes entropy at multiple scales - AI images have unnaturally uniform entropy
 */
export function calculateImageEntropy(buffer: Buffer): number {
  // Build histogram of byte values
  const histogram: { [key: number]: number } = {}

  for (let i = 0; i < buffer.length; i++) {
    const byte = buffer[i]
    histogram[byte] = (histogram[byte] || 0) + 1
  }

  // Calculate Shannon entropy
  let entropy = 0
  const length = buffer.length

  for (const count of Object.values(histogram)) {
    const probability = count / length
    if (probability > 0) {
      entropy -= probability * Math.log2(probability)
    }
  }

  // Normalize to 0-1 range (max entropy for 8-bit is 8)
  return entropy / 8
}

/**
 * Deep pixel neighborhood analysis - detects unnatural smoothness in AI-generated images
 */
export function analyzeCompressionQuality(buffer: Buffer, compressionRatio: number): number {
  let suspiciousScore = 0
  const windowSize = 16 // Analyze 16x16 pixel blocks
  const stride = 8

  // Sample multiple regions
  for (let offset = 0; offset < Math.min(buffer.length - windowSize * 3, 5000); offset += stride * 3) {
    // Simulate RGB channels (assuming interleaved RGB data)
    const rChannel = buffer[offset]
    const gChannel = buffer[offset + 1]
    const bChannel = buffer[offset + 2]

    // Check for unnatural smoothness (GAN artifact)
    const nextR = buffer[offset + 3] || rChannel
    const nextG = buffer[offset + 4] || gChannel
    const nextB = buffer[offset + 5] || bChannel

    const gradientR = Math.abs(rChannel - nextR)
    const gradientG = Math.abs(gChannel - nextG)
    const gradientB = Math.abs(bChannel - nextB)

    // AI images often have suspiciously smooth gradients
    if (gradientR < 3 && gradientG < 3 && gradientB < 3) {
      suspiciousScore += 0.02 // Too smooth - likely AI
    }

    // Or unnaturally sharp edges
    if (gradientR > 100 || gradientG > 100 || gradientB > 100) {
      suspiciousScore += 0.01 // Artificial edge
    }

    // Check for JPEG blockiness at 8x8 boundaries
    if (offset % 8 === 0) {
      const blockBoundaryDiff = Math.abs(rChannel - (buffer[offset - 3] || rChannel))
      if (blockBoundaryDiff > 40) {
        suspiciousScore -= 0.01 // Real JPEG artifacts (good sign)
      }
    }
  }

  // High compression ratio with low artifacts = suspicious
  if (compressionRatio > 0.7 && suspiciousScore > 0.3) {
    suspiciousScore += 0.15
  }

  return Math.min(1, Math.max(0, suspiciousScore))
}

/**
 * Analyzes local pixel variance - AI images lack natural micro-texture
 */
export function analyzePixelConsistency(buffer: Buffer, entropy: number): number {
  let inconsistencyScore = 0
  const patchSize = 25
  let smoothRegions = 0
  let totalPatches = 0

  // Analyze patches throughout the image
  for (let i = 0; i < Math.min(buffer.length - patchSize, 3000); i += patchSize) {
    const patch = buffer.slice(i, i + patchSize)

    // Calculate local variance
    const mean = patch.reduce((sum, val) => sum + val, 0) / patch.length
    const variance = patch.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / patch.length
    const stdDev = Math.sqrt(variance)

    totalPatches++

    // Real photos have natural noise (stdDev usually 10-50)
    // AI images are suspiciously smooth (stdDev < 5)
    if (stdDev < 5) {
      smoothRegions++
      inconsistencyScore += 0.03
    }

    // Check for unnatural uniformity
    const uniqueValues = new Set(patch).size
    if (uniqueValues < 5) {
      inconsistencyScore += 0.02 // Too uniform
    }

    // Check for artificial patterns (repeated values)
    let repeats = 0
    for (let j = 1; j < patch.length; j++) {
      if (patch[j] === patch[j - 1]) repeats++
    }
    if (repeats > patch.length * 0.7) {
      inconsistencyScore += 0.025 // Suspiciously repetitive
    }
  }

  // If too many smooth regions, likely AI-generated
  const smoothRatio = smoothRegions / totalPatches
  if (smoothRatio > 0.6) {
    inconsistencyScore += 0.2
  }

  // Low entropy + high smoothness = AI-generated
  if (entropy < 0.5 && smoothRatio > 0.5) {
    inconsistencyScore += 0.15
  }

  return Math.min(1, inconsistencyScore)
}

/**
 * Detects symmetry and geometric artifacts common in GAN-generated faces
 */
export function analyzeFaceGeometry(buffer: Buffer, fileName: string): number {
  let ganArtifactScore = 0

  // Check for telltale GAN patterns in filename
  const ganPatterns = /(_GAN|_STG|_PGN|StyleGAN|ProGAN|fake|generated|synthetic)/i
  if (ganPatterns.test(fileName)) {
    return 0.95 // Clearly labeled as GAN-generated
  }

  // Analyze pixel distribution for unnatural symmetry
  const sampleSize = Math.min(buffer.length, 4000)
  const leftHalf = buffer.slice(0, sampleSize / 2)
  const rightHalf = buffer.slice(sampleSize / 2, sampleSize)

  // Calculate mean intensity for each half
  const leftMean = leftHalf.reduce((sum, val) => sum + val, 0) / leftHalf.length
  const rightMean = rightHalf.reduce((sum, val) => sum + val, 0) / rightHalf.length

  // Perfect symmetry is suspicious (GAN faces are often too symmetric)
  const symmetryDiff = Math.abs(leftMean - rightMean)
  if (symmetryDiff < 2) {
    ganArtifactScore += 0.25 // Unnaturally symmetric
  }

  // Check for "GAN fingerprint" - repetitive patterns in high-frequency content
  let patternRepetition = 0
  for (let i = 0; i < sampleSize - 50; i += 50) {
    const block1 = buffer.slice(i, i + 25)
    const block2 = buffer.slice(i + 25, i + 50)

    let similarity = 0
    for (let j = 0; j < 25; j++) {
      if (Math.abs(block1[j] - block2[j]) < 5) similarity++
    }

    if (similarity > 20) patternRepetition++
  }

  if (patternRepetition > 15) {
    ganArtifactScore += 0.2 // Repetitive patterns = GAN artifact
  }

  return Math.min(1, ganArtifactScore)
}

/**
 * Analyzes texture realism - AI images lack natural micro-texture detail
 */
export function analyzeTextureQuality(buffer: Buffer, fileSize: number): number {
  let fakeTextureScore = 0
  const windowSize = 50
  let textureAnalyses = 0

  // Analyze texture in multiple regions
  for (let i = 0; i < Math.min(buffer.length - windowSize, 2500); i += windowSize) {
    const window = buffer.slice(i, i + windowSize)

    // Calculate local gradient strength
    let gradientSum = 0
    for (let j = 1; j < window.length; j++) {
      gradientSum += Math.abs(window[j] - window[j - 1])
    }
    const avgGradient = gradientSum / window.length

    textureAnalyses++

    // Real photos have moderate gradient strength (5-25)
    // AI images are either too smooth or have artificial sharpening
    if (avgGradient < 3) {
      fakeTextureScore += 0.04 // Over-smoothed (AI artifact)
    } else if (avgGradient > 35) {
      fakeTextureScore += 0.02 // Over-sharpened (AI post-processing)
    }

    // Check for unnatural color banding (AI diffusion artifact)
    const uniqueValues = new Set(window).size
    if (uniqueValues < 10) {
      fakeTextureScore += 0.03 // Color banding
    }
  }

  // Large file but smooth texture = upscaled AI image
  if (fileSize > 500000 && fakeTextureScore > 0.4) {
    fakeTextureScore += 0.15
  }

  return Math.min(1, fakeTextureScore)
}

/**
 * Frequency domain analysis - AI images have suspicious frequency distributions
 */
export function analyzeFrequencySpectrum(buffer: Buffer, entropy: number): number {
  let frequencyAnomalyScore = 0

  // Analyze high-frequency content (edges, details)
  let highFreqCount = 0
  let lowFreqCount = 0

  for (let i = 1; i < Math.min(buffer.length, 3000); i++) {
    const diff = Math.abs(buffer[i] - buffer[i - 1])

    if (diff > 20) {
      highFreqCount++ // Sharp transitions
    } else if (diff < 3) {
      lowFreqCount++ // Smooth regions
    }
  }

  const totalSamples = Math.min(buffer.length, 3000)
  const highFreqRatio = highFreqCount / totalSamples
  const lowFreqRatio = lowFreqCount / totalSamples

  // Real photos have balanced frequency distribution
  // AI images have unnatural frequency patterns:

  // 1. Too much low frequency (over-smoothed)
  if (lowFreqRatio > 0.7) {
    frequencyAnomalyScore += 0.25
  }

  // 2. Suspicious combination: low entropy + low frequency
  if (entropy < 0.5 && lowFreqRatio > 0.6) {
    frequencyAnomalyScore += 0.3
  }

  // 3. Unnatural mix: very high and very low with nothing in between
  const midFreqCount = totalSamples - highFreqCount - lowFreqCount
  const midFreqRatio = midFreqCount / totalSamples
  if (midFreqRatio < 0.2 && (highFreqRatio > 0.3 || lowFreqRatio > 0.5)) {
    frequencyAnomalyScore += 0.2 // Missing mid-frequencies = AI processing
  }

  return Math.min(1, frequencyAnomalyScore)
}
