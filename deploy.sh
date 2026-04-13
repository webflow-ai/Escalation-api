#!/bin/bash

# Smart Escalation API - Deployment Script
# This script helps you deploy the application using the hybrid approach

set -e

echo "🚀 Smart Escalation API - Deployment Helper"
echo "============================================"
echo ""

# Check if git is clean
if [[ -n $(git status -s) ]]; then
    echo "⚠️  You have uncommitted changes. Commit them first:"
    echo ""
    git status -s
    echo ""
    read -p "Commit changes now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        read -p "Enter commit message: " commit_msg
        git commit -m "$commit_msg"
        echo "✅ Changes committed"
    else
        echo "❌ Please commit changes before deploying"
        exit 1
    fi
fi

echo ""
echo "📦 Deployment Options:"
echo "1. Deploy Backend to Render (recommended)"
echo "2. Deploy Frontend to Vercel"
echo "3. Deploy Both (Backend → Render, Frontend → Vercel)"
echo ""
read -p "Choose option (1-3): " option

case $option in
    1)
        echo ""
        echo "🔧 Deploying Backend to Render..."
        echo ""
        echo "Steps:"
        echo "1. Push your code to GitHub:"
        git push
        echo "   ✅ Code pushed to GitHub"
        echo ""
        echo "2. Go to https://dashboard.render.com"
        echo "3. Click 'New +' → 'Web Service'"
        echo "4. Connect your GitHub repository"
        echo "5. Render will auto-detect render.yaml"
        echo "6. Add your GOOGLE_API_KEY in environment variables"
        echo "7. Click 'Create Web Service'"
        echo ""
        echo "⏳ Deployment will take 5-10 minutes (downloading ML models)"
        echo ""
        echo "After deployment:"
        echo "- Copy your backend URL (e.g., https://your-app.onrender.com)"
        echo "- Add VITE_API_URL environment variable in Vercel"
        echo "- Redeploy frontend"
        ;;
    2)
        echo ""
        echo "🔧 Deploying Frontend to Vercel..."
        echo ""
        echo "Steps:"
        echo "1. Push your code to GitHub:"
        git push
        echo "   ✅ Code pushed to GitHub"
        echo ""
        echo "2. Go to https://vercel.com/dashboard"
        echo "3. Import your GitHub repository"
        echo "4. Configure:"
        echo "   - Framework Preset: Vite"
        echo "   - Root Directory: frontend"
        echo "   - Build Command: npm run build"
        echo "   - Output Directory: dist"
        echo "5. Add environment variable:"
        echo "   - VITE_API_URL = https://your-backend.onrender.com"
        echo "6. Deploy"
        echo ""
        echo "✅ Frontend will be live in ~2 minutes"
        ;;
    3)
        echo ""
        echo "🔧 Deploying Full Stack..."
        echo ""
        git push
        echo "✅ Code pushed to GitHub"
        echo ""
        echo "📋 Follow these steps:"
        echo ""
        echo "STEP 1: Deploy Backend to Render"
        echo "--------------------------------"
        echo "1. Go to https://dashboard.render.com"
        echo "2. Click 'New +' → 'Web Service'"
        echo "3. Connect your GitHub repository"
        echo "4. Render will auto-detect render.yaml"
        echo "5. Add GOOGLE_API_KEY in environment variables"
        echo "6. Click 'Create Web Service'"
        echo "7. Wait for deployment (5-10 minutes)"
        echo "8. Copy your backend URL"
        echo ""
        echo "STEP 2: Deploy Frontend to Vercel"
        echo "---------------------------------"
        echo "1. Go to https://vercel.com/dashboard"
        echo "2. Import your GitHub repository"
        echo "3. Configure:"
        echo "   - Framework Preset: Vite"
        echo "   - Root Directory: frontend"
        echo "   - Build Command: npm run build"
        echo "   - Output Directory: dist"
        echo "4. Add environment variable:"
        echo "   - VITE_API_URL = [YOUR_RENDER_BACKEND_URL]"
        echo "5. Deploy"
        echo ""
        echo "STEP 3: Test"
        echo "------------"
        echo "1. Visit your Vercel frontend URL"
        echo "2. Ask a question"
        echo "3. Verify it connects to your Render backend"
        echo ""
        echo "✅ Full deployment complete!"
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "📚 For detailed instructions, see:"
echo "   - DEPLOYMENT_OPTIONS.md (overview)"
echo "   - BACKEND_DEPLOY.md (Render setup)"
echo "   - README.md (general setup)"
