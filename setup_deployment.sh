#!/bin/bash
# Quick setup script for migrating to Supabase + Render

echo "========================================="
echo "  Supabase + Render Deployment Setup"
echo "========================================="
echo ""

# Check if data.db exists
if [ ! -f "data.db" ]; then
    echo "❌ Error: data.db not found!"
    echo "Please make sure your optimized database exists."
    exit 1
fi

echo "✓ Found data.db"
echo ""

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL not set!"
    echo ""
    echo "Please set your Supabase connection string:"
    echo "  export DATABASE_URL='postgresql://postgres.xxxxx:PASSWORD@host:6543/postgres'"
    echo ""
    echo "Or create a .env file with:"
    echo "  DATABASE_URL=postgresql://..."
    echo ""
    read -p "Do you want to continue without DATABASE_URL? (y/n): " continue_without
    if [ "$continue_without" != "y" ]; then
        exit 1
    fi
else
    echo "✓ DATABASE_URL is set"
fi

echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "========================================="
echo "  Migration Options"
echo "========================================="
echo ""
echo "1. Migrate ALL data (~3M rows) to Supabase"
echo "2. Migrate LIMITED data (1.5M rows) to fit free tier"
echo "3. Test locally with SQLite (no migration)"
echo "4. Exit"
echo ""

read -p "Choose option (1-4): " option

case $option in
    1)
        echo ""
        echo "Starting full migration..."
        python3 migrate_to_postgres.py
        ;;
    2)
        echo ""
        echo "Starting limited migration (1.5M rows)..."
        python3 migrate_to_postgres.py --limit 1500000
        ;;
    3)
        echo ""
        echo "Testing locally with SQLite..."
        python3 api.py
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid option!"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "  Next Steps"
echo "========================================="
echo ""
echo "1. If migration succeeded, test locally:"
echo "   python3 api.py"
echo ""
echo "2. Deploy to Render:"
echo "   - Push to GitHub: git push origin main"
echo "   - Create web service on Render"
echo "   - Add DATABASE_URL environment variable"
echo ""
echo "3. Monitor your app at:"
echo "   https://your-app.onrender.com"
echo ""
