#!/usr/bin/env python3
"""
Batch test GAN-generated images for deepfake detection
Tests all images in test-images directory and generates report
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Tuple

def test_image(image_path: str, api_url: str = "http://localhost:3000/api/detect") -> Dict:
    """
    Test a single image through the detection API
    
    Args:
        image_path: Path to image file
        api_url: Detection API endpoint
        
    Returns:
        Detection result dictionary
    """
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(api_url, files=files, timeout=30)
            
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        return {"error": str(e)}

def categorize_result(confidence: float, is_fake: bool) -> Tuple[str, str]:
    """
    Categorize detection result
    
    Args:
        confidence: Detection confidence (0-100)
        is_fake: Whether detected as fake
        
    Returns:
        (status, description) tuple
    """
    if is_fake:
        if confidence >= 80:
            return ("✅ CORRECT", "High confidence fake detection")
        elif confidence >= 60:
            return ("✅ CORRECT", "Medium confidence fake detection")
        else:
            return ("⚠️ WEAK", "Low confidence on fake image")
    else:
        return ("❌ WRONG", "Fake image detected as real!")

def main():
    """Run batch GAN detection tests"""
    
    # Test images directory
    test_dir = Path("public/test-images")
    
    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        sys.exit(1)
    
    # Find all GAN test images
    gan_patterns = ["gan-", "F_PGN1_", "F_STG_", "stylegan", "progan", "diffusion"]
    test_images = []
    
    for pattern in gan_patterns:
        test_images.extend(list(test_dir.glob(f"*{pattern}*")))
    
    if not test_images:
        print("❌ No GAN test images found!")
        print(f"   Looking for patterns: {', '.join(gan_patterns)}")
        sys.exit(1)
    
    print(f"🔍 Testing {len(test_images)} GAN-generated images...\n")
    print("=" * 70)
    
    results = []
    
    for img_path in test_images:
        print(f"\n📸 Testing: {img_path.name}")
        
        result = test_image(str(img_path))
        
        if "error" in result:
            print(f"   ❌ Error: {result['error']}")
            results.append({
                "image": img_path.name,
                "status": "ERROR",
                "error": result['error']
            })
            continue
        
        # Extract detection details
        confidence = result.get('confidence', 0)
        is_fake = result.get('prediction', 'real').lower() == 'fake'
        uncertainty = result.get('uncertainty', 0)
        
        # Categorize result
        status, description = categorize_result(confidence, is_fake)
        
        print(f"   Result: {result.get('prediction', 'unknown').upper()}")
        print(f"   Confidence: {confidence}%")
        print(f"   Uncertainty: {uncertainty}%")
        print(f"   Status: {status} - {description}")
        
        results.append({
            "image": img_path.name,
            "prediction": result.get('prediction'),
            "confidence": confidence,
            "uncertainty": uncertainty,
            "status": status,
            "description": description
        })
    
    # Generate summary report
    print("\n" + "=" * 70)
    print("\n📊 TEST SUMMARY")
    print("=" * 70)
    
    correct = sum(1 for r in results if r.get("status", "").startswith("✅"))
    weak = sum(1 for r in results if r.get("status", "").startswith("⚠️"))
    wrong = sum(1 for r in results if r.get("status", "").startswith("❌"))
    errors = sum(1 for r in results if r.get("status") == "ERROR")
    
    total = len(results)
    success_rate = (correct / total * 100) if total > 0 else 0
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Correct: {correct}")
    print(f"⚠️  Weak: {weak}")
    print(f"❌ Wrong: {wrong}")
    print(f"🔧 Errors: {errors}")
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    # Evaluation readiness
    print("\n" + "=" * 70)
    print("🎓 EVALUATION READINESS")
    print("=" * 70)
    
    if success_rate >= 80:
        print("\n✅ EXCELLENT - Ready for evaluation!")
        print("   Your system reliably detects GAN-generated fakes.")
    elif success_rate >= 60:
        print("\n⚠️  GOOD - Should be okay for evaluation")
        print("   Most fakes detected, but some improvements needed.")
    else:
        print("\n❌ NEEDS WORK - Not ready for evaluation")
        print("   Detection accuracy too low. Review algorithm.")
    
    # Save detailed results
    report_path = "test-results-gan.json"
    with open(report_path, 'w') as f:
        json.dump({
            "summary": {
                "total": total,
                "correct": correct,
                "weak": weak,
                "wrong": wrong,
                "errors": errors,
                "success_rate": success_rate
            },
            "results": results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {report_path}")
    print("\n" + "=" * 70)
    
    # Exit with appropriate code
    sys.exit(0 if success_rate >= 60 else 1)

if __name__ == "__main__":
    main()
