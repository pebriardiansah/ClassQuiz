# 🚀 QUICK START GUIDE - Setup Psychological Screening di ClassQuiz

## Prerequisites

✅ Docker & Docker Compose installed  
✅ Git installed  
✅ Basic knowledge tentang ClassQuiz  
✅ PostgreSQL 14+  
✅ Python 3.10+  

---

## Step 1: Clone & Setup Repository

```bash
# Clone repository
git clone https://github.com/pebriardiansah/ClassQuiz.git
cd ClassQuiz

# Create psychological-screening directory jika belum ada
mkdir -p psychological-screening

# Copy files ke folder yang tepat
cp psychological-screening/*.json ./classquiz/data/
cp psychological-screening/scoring_engine.py ./classquiz/algorithms/
cp psychological-screening/dashboard-hr.svelte ./frontend/src/routes/hr/
```

---

## Step 2: Setup Environment Variables

Buat file `.env` atau update yang sudah ada:

```env
# Database Configuration
DB_URL="postgresql://postgres:classquiz@db:5432/classquiz"

# Redis Configuration
REDIS="redis://redis:6379/0?decode_responses=True"

# Psychological Screening Config
PSYCH_TEST_TIMEOUT_MINUTES=45
PSYCH_MAX_RED_FLAGS_ALLOWED=2
PSYCH_ENABLE_HR_DASHBOARD=true
PSYCH_ENABLE_NOTIFICATIONS=true
PSYCH_PDF_EXPORT_ENABLED=true
PSYCH_NOTIFICATION_EMAIL=hr@rumahsakit.id

# Other ClassQuiz Settings
ROOT_ADDRESS="http://localhost:8000"
SECRET_KEY="your-secret-key-here"
MAX_WORKERS="1"
```

---

## Step 3: Update docker-compose.yml

Tambahkan psychological worker service:

```yaml
version: "3"

services:
  # ... existing services ...
  
  psychological-worker:
    image: ghcr.io/mawoka-myblock/classquiz-backend:master
    environment: *env_vars
    depends_on: *depends
    restart: always
    command: arq classquiz.worker_psychological.ScoringWorkerSettings
    volumes:
      - ./classquiz/algorithms:/app/classquiz/algorithms
    networks:
      - default

volumes:
  data:
  meilisearch-data:

networks:
  default:
    driver: bridge
```

---

## Step 4: Database Migration

```bash
# Akses PostgreSQL container
docker exec -it classquiz-db psql -U postgres -d classquiz

# Run migration script
\i /psychological-screening/migrations/001_initial_schema.sql

# Verify tables
\dt psychological_*

# Exit
\q
```

Atau jalankan migration via Python:

```bash
# Dari root directory ClassQuiz
python -m alembic upgrade head
```

---

## Step 5: Import Test Data

```bash
# Script untuk import soal ke database
python scripts/import_psychological_tests.py \
  --test-file psychological-screening/soal_psikotes_dokter.json \
  --position dokter

python scripts/import_psychological_tests.py \
  --test-file psychological-screening/soal_psikotes_perawat.json \
  --position perawat

python scripts/import_psychological_tests.py \
  --test-file psychological-screening/soal_psikotes_bidan.json \
  --position bidan
```

---

## Step 6: Start Docker Containers

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Verify all services running
docker-compose ps
```

Expected output:
```
NAME                    STATUS
classquiz-frontend      Up (healthy)
classquiz-api           Up (healthy)
classquiz-db            Up (healthy)
classquiz-redis         Up (healthy)
classquiz-meilisearch   Up (healthy)
classquiz-proxy         Up (healthy)
psychological-worker    Up
```

---

## Step 7: Access the Application

```bash
# Frontend (HR Dashboard & Quiz Interface)
http://localhost:8000

# API Documentation (Swagger)
http://localhost:8000/api/docs

# Admin Panel
http://localhost:8000/admin
```

---

## Step 8: Create Admin User

```bash
# Masuk ke API container
docker exec -it classquiz-api bash

# Create admin user
python -m classquiz.cli create-admin \
  --email admin@rumahsakit.id \
  --password secure_password_123

# Exit
exit
```

---

## Step 9: Test the System

### Test 1: Access Dashboard
1. Login ke http://localhost:8000
2. Go to HR Dashboard
3. Verify psychological screening tests terlihat

### Test 2: Create Test Candidate
```bash
# Via API
curl -X POST http://localhost:8000/api/participants \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test Dokter",
    "email": "test@example.com",
    "position_applied": "dokter"
  }'
```

### Test 3: Submit Test Responses
```bash
# Via API
curl -X POST http://localhost:8000/api/psychological/responses/submit \
  -H "Content-Type: application/json" \
  -d '{
    "participant_id": "<participant_id>",
    "test_id": "<test_id>",
    "responses": {
      "1": 4, "2": 5, "3": 3, "4": 4, "5": 2,
      "6": 4, "7": 5, "8": 2, "9": 4, "10": 4,
      "11": 4, "12": 5, "13": 3, "14": 4, "15": 2,
      "16": 3, "17": 4, "18": 3, "19": 2, "20": 3,
      "21": 4, "22": 4, "23": 4, "24": 4, "25": 2,
      "26": 4, "27": 4, "28": 4, "29": 2, "30": 4,
      "31": 4, "32": 4, "33": 4, "34": 4, "35": 5,
      "36": 4, "37": 2, "38": 4, "39": 2, "40": 2
    }
  }'
```

### Test 4: View Results
```bash
curl http://localhost:8000/api/psychological/results/<result_id>
```

---

## Step 10: Setup Email Notifications (Optional)

```env
# Add to .env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=HR System <noreply@rumahsakit.id>

# Enable notifications
PSYCH_ENABLE_NOTIFICATIONS=true
```

Restart services:
```bash
docker-compose down
docker-compose up -d
```

---

## Troubleshooting

### Issue: "Cannot connect to database"
```bash
# Check database logs
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up -d db
```

### Issue: "API worker not responding"
```bash
# Restart worker
docker-compose restart psychological-worker

# Check logs
docker-compose logs psychological-worker
```

### Issue: "Frontend not loading"
```bash
# Rebuild frontend
docker-compose down frontend
docker-compose up -d frontend

# Check logs
docker-compose logs frontend
```

### Issue: "Scoring not working"
```bash
# Verify Redis connection
docker exec -it classquiz-redis redis-cli ping

# Restart API
docker-compose restart api
```

---

## Verify Installation

Run validation script:

```bash
cd psychological-screening
python validate_installation.py
```

Expected output:
```
✅ Database tables created
✅ API endpoints accessible
✅ Frontend routes registered
✅ Scoring engine loaded
✅ Test data imported
✅ Worker service running

🎉 Installation successful!
```

---

## Next Steps

1. **Configure HR Accounts**
   - Create user accounts untuk HR staff
   - Set permissions
   - Share dashboard access

2. **Test with Real Data**
   - Import sample candidates
   - Run complete test flow
   - Validate scoring accuracy

3. **Training**
   - Train HR team on dashboard usage
   - Explain scoring interpretation
   - Setup support process

4. **Go Live**
   - Start with pilot group
   - Collect feedback
   - Scale to full recruitment

---

## Support & Troubleshooting

- 📧 Email: hr-tech@rumahsakit.id
- 💬 Slack: #psychological-screening-support
- 📚 Wiki: https://wiki.internal/classquiz-setup
- 🐛 Issues: https://github.com/pebriardiansah/ClassQuiz/issues

---

**Last Updated**: 2026-07-22  
**Version**: 1.0  
**Status**: ✅ Ready for Deployment
