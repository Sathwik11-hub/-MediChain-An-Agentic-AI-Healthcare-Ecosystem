#!/bin/bash

# MediChain Deployment Cleanup Script
# This script removes all unnecessary files to reduce deployment size

set -e  # Exit on error

echo "🧹 Starting MediChain Cleanup..."
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found. Are you in the project root?"
    exit 1
fi

print_success "Found project root directory"

# 1. Remove Python cache files
echo ""
echo "📦 Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".tox" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.pyd" -delete 2>/dev/null || true
print_success "Python cache removed"

# 2. Remove virtual environments
echo ""
echo "🐍 Removing virtual environments..."
rm -rf venv/ env/ .venv/ ENV/ 2>/dev/null || true
print_success "Virtual environments removed"

# 3. Remove test artifacts
echo ""
echo "🧪 Removing test artifacts..."
rm -rf .coverage htmlcov/ .hypothesis/ 2>/dev/null || true
print_success "Test artifacts removed"

# 4. Remove build artifacts
echo ""
echo "🏗️  Removing build artifacts..."
rm -rf build/ dist/ *.egg-info/ 2>/dev/null || true
print_success "Build artifacts removed"

# 5. Remove logs
echo ""
echo "📝 Removing log files..."
find . -type f -name "*.log" -delete 2>/dev/null || true
rm -rf logs/ 2>/dev/null || true
print_success "Log files removed"

# 6. Remove temporary files
echo ""
echo "🗑️  Removing temporary files..."
find . -type f -name "*.tmp" -delete 2>/dev/null || true
find . -type f -name "*.temp" -delete 2>/dev/null || true
rm -rf tmp/ temp/ 2>/dev/null || true
print_success "Temporary files removed"

# 7. Remove OS-specific files
echo ""
echo "💻 Removing OS-specific files..."
find . -type f -name ".DS_Store" -delete 2>/dev/null || true
find . -type f -name "Thumbs.db" -delete 2>/dev/null || true
print_success "OS-specific files removed"

# 8. Check for large files
echo ""
echo "🔍 Checking for large files (>10MB)..."
LARGE_FILES=$(find . -type f -size +10M 2>/dev/null | grep -v ".git" || true)
if [ -z "$LARGE_FILES" ]; then
    print_success "No large files found"
else
    print_warning "Found large files:"
    echo "$LARGE_FILES"
    echo ""
    print_warning "Consider moving these to external storage (S3, Google Cloud Storage)"
fi

# 9. Display directory sizes
echo ""
echo "📊 Directory sizes:"
du -sh */ 2>/dev/null | sort -hr | head -10 || true

# 10. Display total size
echo ""
echo "📏 Total project size:"
du -sh . 2>/dev/null || true

# 11. Check git status
echo ""
echo "📁 Git status:"
git status --short 2>/dev/null || print_warning "Not a git repository or git not available"

echo ""
echo "════════════════════════════════════════════════════════════"
print_success "Cleanup completed!"
echo ""
echo "Next steps:"
echo "1. Review the sizes above"
echo "2. Choose deployment strategy (see DEPLOYMENT_FIX.md)"
echo "3. For Vercel: cp requirements-vercel.txt requirements.txt"
echo "4. For Railway/Render: cp requirements-full.txt requirements.txt"
echo "5. Deploy: vercel --prod (or railway up)"
echo "════════════════════════════════════════════════════════════"
