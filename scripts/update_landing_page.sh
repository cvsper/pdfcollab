#!/bin/bash
# Script to update the React landing page

echo "🚀 Updating React Landing Page..."

# Optional: Build the React app for production
if command -v npm &> /dev/null; then
    echo "📦 Building React app for production..."
    npm run build
    
    if [ $? -eq 0 ]; then
        echo "✅ React app built successfully"
        echo "📁 Built files available in static/dist/"
    else
        echo "⚠️  Build failed, using CDN version"
    fi
else
    echo "ℹ️  npm not available, using CDN version"
fi

echo "🌐 Landing page ready at: http://localhost:5006/"
echo "🔐 Authentication ready at: http://localhost:5006/auth/login"
echo "📊 Dashboard available at: http://localhost:5006/dashboard"

echo ""
echo "✅ Landing page update complete!"