# 🚀 Quick Start Script for MediChain

echo "🏥 MediChain - Multi-Agent Medical AI System"
echo "============================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your API keys."
    echo ""
fi

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1)
echo "Found: $python_version"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🚀 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Start databases: docker-compose up -d postgres neo4j"
echo "3. Start API: python api/main.py"
echo "4. Start Frontend: streamlit run frontend/app.py"
echo ""
echo "Or use Docker: docker-compose up -d"
echo ""
echo "📖 For more information, see README.md"
