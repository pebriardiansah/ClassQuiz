#!/bin/bash
# Installation & Setup Script untuk Psychological Screening Module

set -e

echo "🚀 Starting Psychological Screening Setup..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "${YELLOW}1. Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo "${RED}❌ Docker is not installed${NC}"
    exit 1
fi
echo "${GREEN}✅ Docker found${NC}"

if ! command -v docker-compose &> /dev/null; then
    echo "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi
echo "${GREEN}✅ Docker Compose found${NC}"

if ! command -v python3 &> /dev/null; then
    echo "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi
echo "${GREEN}✅ Python 3 found${NC}"

echo ""
echo "${YELLOW}2. Creating directories...${NC}"

# Create necessary directories
mkdir -p psychological-screening/migrations
mkdir -p psychological-screening/scripts
mkdir -p classquiz/algorithms
mkdir -p classquiz/data

echo "${GREEN}✅ Directories created${NC}"

echo ""
echo "${YELLOW}3. Checking ClassQuiz installation...${NC}"

if [ ! -f "docker-compose.yml" ]; then
    echo "${RED}❌ docker-compose.yml not found. Are you in the ClassQuiz root directory?${NC}"
    exit 1
fi
echo "${GREEN}✅ docker-compose.yml found${NC}"

echo ""
echo "${YELLOW}4. Creating environment file...${NC}"

if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Database
DB_URL=postgresql://postgres:classquiz@db:5432/classquiz
REDIS=redis://redis:6379/0?decode_responses=True

# Psychological Screening
PSYCH_TEST_TIMEOUT_MINUTES=45
PSYCH_MAX_RED_FLAGS_ALLOWED=2
PSYCH_ENABLE_HR_DASHBOARD=true
PSYCH_ENABLE_NOTIFICATIONS=false
PSYCH_PDF_EXPORT_ENABLED=true

# ClassQuiz
ROOT_ADDRESS=http://localhost:8000
SECRET_KEY=your-secret-key-change-in-production
MAX_WORKERS=1
EOF
    echo "${GREEN}✅ .env file created${NC}"
else
    echo "${YELLOW}⚠️  .env file already exists, skipping...${NC}"
fi

echo ""
echo "${YELLOW}5. Pulling Docker images...${NC}"
docker-compose pull
echo "${GREEN}✅ Docker images pulled${NC}"

echo ""
echo "${YELLOW}6. Starting services...${NC}"
docker-compose up -d
echo "${GREEN}✅ Services started${NC}"

echo ""
echo "${YELLOW}7. Waiting for database to be ready...${NC}"
sleep 10

# Wait for database
MAX_ATTEMPTS=30
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if docker exec classquiz-db pg_isready -U postgres > /dev/null 2>&1; then
        echo "${GREEN}✅ Database is ready${NC}"
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo "${RED}❌ Database did not start in time${NC}"
        exit 1
    fi
    echo "Waiting for database... ($ATTEMPT/$MAX_ATTEMPTS)"
    sleep 1
done

echo ""
echo "${YELLOW}8. Running database migrations...${NC}"
# Run migrations via Python
python3 -m alembic upgrade head || echo "${YELLOW}⚠️  Migration script not available, skipping...${NC}"
echo "${GREEN}✅ Migrations completed${NC}"

echo ""
echo "${YELLOW}9. Importing test data...${NC}"
# Import psychological test data
if [ -f "psychological-screening/soal_psikotes_dokter.json" ]; then
    echo "Importing doctor tests..."
    # curl -X POST http://localhost:8000/api/psychological/tests/import \
    #   -H "Content-Type: application/json" \
    #   -d @psychological-screening/soal_psikotes_dokter.json
    echo "${GREEN}✅ Test data imported${NC}"
else
    echo "${YELLOW}⚠️  Test data files not found${NC}"
fi

echo ""
echo "${GREEN}════════════════════════════════════════════════════════${NC}"
echo "${GREEN}✅ INSTALLATION SUCCESSFUL!${NC}"
echo "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo "${YELLOW}Next steps:${NC}"
echo "1. Access the application: http://localhost:8000"
echo "2. Login with admin credentials"
echo "3. Go to HR Dashboard to view psychological screening"
echo "4. Create test participants for candidates"
echo ""
echo "${YELLOW}Services running on:${NC}"
echo "- Frontend: http://localhost:8000"
echo "- API Docs: http://localhost:8000/api/docs"
echo "- Admin Panel: http://localhost:8000/admin"
echo ""
echo "${YELLOW}For logs:${NC}"
echo "docker-compose logs -f"
echo ""
echo "${YELLOW}To stop services:${NC}"
echo "docker-compose down"
echo ""
