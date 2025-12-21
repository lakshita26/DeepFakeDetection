#!/bin/bash
# Quick GAN detection test script for evaluation preparation

echo "🚀 Starting GAN Detection Test Suite"
echo "====================================="

# Check if Next.js is running
if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ Next.js not running! Start it first with: npm run dev"
    exit 1
fi

echo "✅ Next.js server is running"

# Check Python dependencies
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    exit 1
fi

echo "✅ Python3 found"

# Install required Python packages
pip3 install -q requests 2>/dev/null || echo "⚠️  Could not install requests package"

# Run batch tests
echo ""
echo "🔍 Running batch GAN detection tests..."
python3 scripts/batch_test_gan.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed! Ready for evaluation."
else
    echo ""
    echo "⚠️  Some tests need attention. Review results above."
fi
