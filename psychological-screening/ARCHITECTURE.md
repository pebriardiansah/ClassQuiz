# 🏗️ ARCHITECTURE - Implementasi Psychological Screening Module di ClassQuiz

## Table of Contents
1. [System Overview](#system-overview)
2. [Database Schema](#database-schema)
3. [Backend Architecture](#backend-architecture)
4. [Frontend Architecture](#frontend-architecture)
5. [API Endpoints](#api-endpoints)
6. [Integration Points](#integration-points)
7. [Deployment](#deployment)

---

## System Overview {#system-overview}

```
┌─────────────────────────────────────────────────────────────┐
│                    PSYCHOLOGICAL SCREENING SYSTEM             │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│   FRONTEND (SvelteKit)          │   BACKEND (FastAPI)   │
│  ┌────────────────┐  │         │  ┌────────────────┐  │
│  │ Quiz Interface │  │         │  │ Scoring Engine │  │
│  │ HR Dashboard   │  │         │  │ API Routes     │  │
│  │ Result Display │  │         │  │ DB Operations  │  │
│  └────────────────┘  │         │  └────────────────┘  │
└──────────────────────┘         └──────────────────────┘
          │                               │
          └───────────────┬───────────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
        ┌─────▼─────┐          ┌──────▼──────┐
        │ PostgreSQL │          │    Redis    │
        │  Database  │          │    Cache    │
        └────────────┘          └─────────────┘
              │
        ┌─────▼──────────┐
        │  Meilisearch   │
        │  (Analytics)   │
        └────────────────┘
```

---

## Database Schema {#database-schema}

### 1. PsychologicalTest Table
```sql
CREATE TABLE psychological_tests (
    id UUID PRIMARY KEY,
    test_code VARCHAR(50) UNIQUE,  -- "BIG_FIVE", "DASS21", "EQ", etc
    title VARCHAR(255),
    description TEXT,
    target_position VARCHAR(100),  -- "dokter", "perawat", "bidan"
    test_type VARCHAR(50),  -- "personality", "stress", "mental_health"
    duration_minutes INT,
    total_questions INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    organization_id UUID REFERENCES organizations(id)
);
```

### 2. PsychologicalQuestion Table
```sql
CREATE TABLE psychological_questions (
    id UUID PRIMARY KEY,
    test_id UUID REFERENCES psychological_tests(id),
    question_number INT,
    text VARCHAR(500),
    dimension VARCHAR(100),  -- "Openness", "Agreeableness", etc
    question_type VARCHAR(50),  -- "likert5", "likert7", "binary"
    is_reverse BOOLEAN DEFAULT FALSE,
    weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3. PsychologicalResponse Table
```sql
CREATE TABLE psychological_responses (
    id UUID PRIMARY KEY,
    participant_id UUID REFERENCES participants(id),
    test_id UUID REFERENCES psychological_tests(id),
    question_id UUID REFERENCES psychological_questions(id),
    response_score INT,  -- 1-5 untuk likert5
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4. PsychologicalResult Table
```sql
CREATE TABLE psychological_results (
    id UUID PRIMARY KEY,
    participant_id UUID REFERENCES participants(id),
    test_id UUID REFERENCES psychological_tests(id),
    test_taken_at TIMESTAMP,
    duration_seconds INT,
    
    -- Big Five Scores
    openness FLOAT,
    conscientiousness FLOAT,
    extraversion FLOAT,
    agreeableness FLOAT,
    neuroticism FLOAT,
    
    -- Stress Resilience
    stress_handling FLOAT,
    stress_resilience FLOAT,
    
    -- Emotional Intelligence
    eq_self_awareness FLOAT,
    eq_self_regulation FLOAT,
    eq_empathy FLOAT,
    eq_social_skills FLOAT,
    eq_motivation FLOAT,
    eq_overall FLOAT,
    
    -- Overall Assessment
    overall_score FLOAT,
    recommendation VARCHAR(50),  -- "PROCEED", "FURTHER_ASSESSMENT", "CAUTION"
    red_flags TEXT,  -- JSON array
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

### 5. Participant Table (Extension)
```sql
CREATE TABLE participants (
    id UUID PRIMARY KEY,
    full_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    position_applied VARCHAR(100),  -- "dokter", "perawat", "bidan"
    
    -- Relationship
    user_id UUID REFERENCES users(id),
    organization_id UUID REFERENCES organizations(id),
    recruitment_campaign_id UUID,
    
    -- Status
    status VARCHAR(50),  -- "pending", "completed", "processing", "hired", "rejected"
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

### 6. PsychologicalInterpretation Table
```sql
CREATE TABLE psychological_interpretations (
    id UUID PRIMARY KEY,
    result_id UUID REFERENCES psychological_results(id),
    interpretation_text TEXT,
    hr_recommendation TEXT,
    next_step_action VARCHAR(255),
    interpretted_by VARCHAR(100),  -- HR staff name
    interpretted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Backend Architecture {#backend-architecture}

### Directory Structure
```
classquiz/
├── models/
│   ├── psychological_test.py          # Pydantic models untuk test
│   ├── psychological_response.py       # Response models
│   ├── psychological_result.py         # Result models
│   └── participant.py                  # Participant models
│
├── routes/
│   ├── psychological_tests.py          # API endpoints untuk test management
│   ├── psychological_responses.py      # Submit responses
│   ├── psychological_results.py        # Get results
│   ├── psychological_dashboard.py      # HR Dashboard data
│   └── psychological_reports.py        # Generate reports
│
├── algorithms/
│   ├── scoring_engine.py               # Main scoring logic
│   ├── big_five_scoring.py            # Big Five calculation
│   ├── stress_resilience_scoring.py    # Stress scoring
│   ├── emotional_intelligence_scoring.py  # EQ scoring
│   ├── red_flags_detector.py           # Identify red flags
│   └── recommendation_engine.py        # Generate recommendations
│
├── services/
│   ├── psychological_test_service.py   # Business logic
│   ├── report_generator.py             # PDF/JSON report generation
│   └── notification_service.py         # Email notifications
│
└── utils/
    ├── psychological_constants.py      # Constants & configurations
    └── validation.py                   # Input validation
```

### Core Models (Python/FastAPI)

```python
# classquiz/models/psychological_test.py
from pydantic import BaseModel
from typing import Dict, List, Optional
from enum import Enum

class PositionType(str, Enum):
    DOKTER = "dokter"
    PERAWAT = "perawat"
    BIDAN = "bidan"

class RecommendationType(str, Enum):
    PROCEED = "PROCEED"
    FURTHER_ASSESSMENT = "FURTHER_ASSESSMENT"
    CAUTION = "CAUTION"

class PsychologicalTest(BaseModel):
    id: str
    test_code: str
    title: str
    target_position: PositionType
    total_questions: int
    duration_minutes: int
    is_active: bool

class PsychologicalResult(BaseModel):
    participant_id: str
    test_id: str
    overall_score: float
    recommendation: RecommendationType
    
    # Big Five
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    
    # Stress & Resilience
    stress_handling: float
    stress_resilience: float
    
    # EQ
    eq_overall: float
    eq_self_awareness: float
    eq_empathy: float
    eq_social_skills: float
    eq_motivation: float
    
    # Flags
    red_flags: List[str]
    hr_recommendation: str
    next_step_action: str
```

### FastAPI Routes

```python
# classquiz/routes/psychological_tests.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
import uuid

router = APIRouter(prefix="/api/psychological", tags=["Psychological Tests"])

# Get all available tests
@router.get("/tests")
async def get_available_tests(position: str = None):
    """Get available psychological tests, optionally filtered by position"""
    # Filter by position if provided
    # Return list of tests with metadata

# Get specific test
@router.get("/tests/{test_id}")
async def get_test_details(test_id: str):
    """Get full test with all questions"""
    # Return test object with questions

# Submit responses
@router.post("/responses/submit")
async def submit_responses(
    participant_id: str,
    test_id: str,
    responses: Dict[int, int]  # question_id -> score
):
    """
    Submit test responses and trigger automatic scoring
    """
    # Save responses
    # Call scoring engine
    # Save result
    # Return result summary

# Get result
@router.get("/results/{result_id}")
async def get_result(result_id: str):
    """Get detailed result with interpretation"""
    # Return full result with HR recommendations

# HR Dashboard - List candidates
@router.get("/dashboard/candidates")
async def get_candidates(
    position: str = None,
    status: str = None,
    sort_by: str = "created_at"
):
    """Get list of candidates with their screening results for HR"""
    # Return paginated list with scores & recommendations

# HR Dashboard - Candidate detail
@router.get("/dashboard/candidates/{participant_id}")
async def get_candidate_detail(participant_id: str):
    """Get complete candidate profile with test results"""
    # Return full candidate data with all test results

# Export report
@router.get("/reports/export/{result_id}")
async def export_report(result_id: str, format: str = "pdf"):
    """Export result as PDF or JSON"""
    # Generate report
    # Return file
```

---

## Frontend Architecture {#frontend-architecture}

### Directory Structure
```
frontend/src/routes/
├── psychological-tests/
│   ├── +page.svelte              # List available tests
│   ├── [test_id]/
│   │   └── +page.svelte          # Take test (Likert form)
│   └── results/
│       └── [result_id]/
│           └── +page.svelte      # View result (Candidate view)
│
├── hr/
│   ├── dashboard/
│   │   └── +page.svelte          # Main HR dashboard
│   ├── candidates/
│   │   ├── +page.svelte          # Candidates list
│   │   └── [candidate_id]/
│   │       └── +page.svelte      # Candidate detail
│   └── reports/
│       └── +page.svelte          # Advanced reporting

frontend/src/components/
├── PsychologicalTestForm.svelte      # Quiz form component
├── ResultCard.svelte                 # Result display
├── ScoreVisualization.svelte         # Charts & graphs
├── RedFlagAlert.svelte               # Red flags display
├── HRDashboard.svelte                # Main dashboard (sudah dibuat)
└── CandidateManagement.svelte        # Candidate management
```

### Key Svelte Components

```svelte
<!-- PsychologicalTestForm.svelte -->
<script>
  export let test;
  export let onSubmit;
  
  let currentQuestion = 0;
  let responses = {};
  let startTime = Date.now();
  
  function handleResponse(questionId, score) {
    responses[questionId] = score;
    if (currentQuestion < test.total_questions - 1) {
      currentQuestion++;
    }
  }
  
  function submitTest() {
    const duration = Math.floor((Date.now() - startTime) / 1000);
    onSubmit({responses, duration});
  }
</script>

<div class="test-container">
  <div class="progress-bar">
    {currentQuestion + 1} / {test.total_questions}
  </div>
  
  <div class="question-display">
    <p class="question-text">
      {test.questions[currentQuestion].text}
    </p>
    
    <div class="likert-options">
      {#each [1,2,3,4,5] as option}
        <button 
          on:click={() => handleResponse(test.questions[currentQuestion].id, option)}
          class="likert-button"
        >
          {option}
        </button>
      {/each}
    </div>
  </div>
  
  <button on:click={submitTest}>Selesai</button>
</div>
```

---

## API Endpoints {#api-endpoints}

### Psychological Tests Endpoints
```
POST   /api/psychological/tests              # Create new test (Admin)
GET    /api/psychological/tests              # List tests
GET    /api/psychological/tests/{id}         # Get test details
PUT    /api/psychological/tests/{id}         # Update test
DELETE /api/psychological/tests/{id}         # Delete test
```

### Responses Endpoints
```
POST   /api/psychological/responses/submit   # Submit test responses
GET    /api/psychological/responses/{id}     # Get specific response
```

### Results Endpoints
```
GET    /api/psychological/results/{id}       # Get test result
GET    /api/psychological/results            # List results (for candidates)
POST   /api/psychological/results/{id}/interpret  # Add HR interpretation
```

### HR Dashboard Endpoints
```
GET    /api/psychological/dashboard/candidates        # List candidates
GET    /api/psychological/dashboard/candidates/{id}   # Candidate detail
GET    /api/psychological/dashboard/statistics        # Org statistics
GET    /api/psychological/dashboard/trends            # Trend analysis
```

### Reports Endpoints
```
GET    /api/psychological/reports/export/{id}        # Export result
POST   /api/psychological/reports/batch-export        # Export multiple
GET    /api/psychological/reports/analytics          # Analytics report
```

---

## Integration Points {#integration-points}

### 1. Scoring Engine Integration
```python
# classquiz/algorithms/scoring_engine.py
from classquiz.models.psychological_result import PsychologicalResult
from classquiz.algorithms.big_five_scoring import calculate_big_five
from classquiz.algorithms.recommendation_engine import generate_recommendation

async def score_test(test_id: str, responses: Dict[int, int]) -> PsychologicalResult:
    # 1. Get test metadata
    test = await get_test(test_id)
    
    # 2. Calculate scores
    big_five = calculate_big_five(responses, test.target_position)
    stress = calculate_stress_resilience(responses)
    eq = calculate_emotional_intelligence(responses)
    
    # 3. Detect red flags
    red_flags = detect_red_flags(big_five, stress, eq, test.target_position)
    
    # 4. Calculate overall score
    overall = calculate_overall_score(big_five, stress, eq, test.target_position)
    
    # 5. Generate recommendation
    recommendation = generate_recommendation(overall, red_flags)
    
    # 6. Generate HR text
    hr_recommendation = generate_hr_recommendation(
        recommendation, big_five, red_flags, test.target_position
    )
    
    # 7. Save to database
    result = await save_result({
        'big_five': big_five,
        'stress': stress,
        'eq': eq,
        'overall_score': overall,
        'recommendation': recommendation,
        'red_flags': red_flags,
        'hr_recommendation': hr_recommendation
    })
    
    return result
```

### 2. WebSocket Integration (Real-time Results)
```python
# Enable real-time updates untuk HR dashboard
from fastapi import WebSocket

@router.websocket("/ws/results/{participant_id}")
async def websocket_endpoint(websocket: WebSocket, participant_id: str):
    """
    WebSocket untuk real-time updates ketika test selesai
    """
    await websocket.accept()
    
    try:
        while True:
            # Listen untuk new results
            result = await get_latest_result(participant_id)
            if result:
                await websocket.send_json({
                    'type': 'result_completed',
                    'result': result.dict()
                })
    except Exception as e:
        await websocket.close(code=1000)
```

### 3. Email Notification Integration
```python
# Send result to participant & HR
from classquiz.services.notification_service import NotificationService

async def notify_test_completed(result_id: str):
    result = await get_result(result_id)
    
    # Send to candidate
    await NotificationService.send_email(
        to=result.participant.email,
        subject="Hasil Tes Psikologis Anda",
        template="result_notification_participant.html",
        context={'result': result}
    )
    
    # Send to HR
    await NotificationService.send_email(
        to=result.organization.hr_email,
        subject="Hasil Tes Psikologis - Kandidat Baru",
        template="result_notification_hr.html",
        context={'result': result}
    )
```

### 4. Report Generation
```python
# Generate PDF report
from classquiz.services.report_generator import ReportGenerator

async def generate_pdf_report(result_id: str):
    result = await get_result(result_id)
    
    generator = ReportGenerator()
    pdf = await generator.generate_report(
        result=result,
        language='id',  # Indonesian
        format='pdf'
    )
    
    return pdf  # Return as FileResponse
```

---

## Deployment {#deployment}

### Docker Compose Configuration
```yaml
# Add to existing docker-compose.yml

  psychological-worker:
    image: ghcr.io/mawoka-myblock/classquiz-backend:master
    environment: *env_vars
    depends_on: *depends
    restart: *restart
    command: arq classquiz.worker_psychological.ScoringWorkerSettings
    volumes:
      - ./classquiz/algorithms:/app/classquiz/algorithms

  redis-psychological:
    image: valkey/valkey:alpine
    restart: always
    ports:
      - "6380:6379"
    healthcheck:
      test: ["CMD", "valkey-cli", "ping"]
```

### Environment Variables
```env
# Psychological Screening Config
PSYCH_TEST_TIMEOUT_MINUTES=45
PSYCH_MAX_RED_FLAGS_ALLOWED=2
PSYCH_ENABLE_HR_DASHBOARD=true
PSYCH_ENABLE_NOTIFICATIONS=true
PSYCH_PDF_EXPORT_ENABLED=true

# Scoring Config
PSYCH_SCORING_ALGORITHM_VERSION=1.0
PSYCH_RED_FLAG_SENSITIVITY=high

# Email Config (untuk notifications)
PSYCH_NOTIFICATION_EMAIL=hr@rumahsakit.id
PSYCH_SMTP_SERVER=smtp.rumahsakit.id
```

### Database Migration
```sql
-- Run migration untuk create tables
-- File: migrations/psych_screening_initial.sql

CREATE TABLE psychological_tests (...)
CREATE TABLE psychological_questions (...)
CREATE TABLE psychological_responses (...)
CREATE TABLE psychological_results (...)
CREATE TABLE participants (...)
CREATE TABLE psychological_interpretations (...)

CREATE INDEX idx_participant_test ON psychological_results(participant_id, test_id);
CREATE INDEX idx_result_recommendation ON psychological_results(recommendation);
CREATE INDEX idx_created_date ON psychological_results(created_at);
```

---

## Performance Optimization {#performance}

### Caching Strategy
```python
# Cache test questions dalam Redis
@router.get("/tests/{test_id}")
async def get_test(test_id: str, redis_client):
    cache_key = f"test:{test_id}"
    
    # Check cache first
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Query database
    test = await db.get_test(test_id)
    
    # Cache untuk 24 jam
    await redis_client.setex(
        cache_key,
        86400,
        json.dumps(test)
    )
    
    return test
```

### Database Indexing
```sql
-- Optimize common queries
CREATE INDEX idx_participant_org ON participants(organization_id);
CREATE INDEX idx_result_test_position ON psychological_results(test_id, recommendation);
CREATE INDEX idx_created_date ON psychological_results(created_at DESC);
```

---

## Security Considerations {#security}

### Access Control
- ✅ Kandidat hanya bisa lihat test yang di-assign
- ✅ HR hanya bisa lihat candidates di org mereka
- ✅ Admin bisa manage semua tests
- ✅ Scoring engine immutable (tidak bisa di-edit result)

### Data Privacy
- ✅ Encrypt sensitive data di database
- ✅ GDPR compliant data retention policy
- ✅ Audit logging untuk semua actions
- ✅ Secure PDF export dengan password

---

**Last Updated**: 2026-07-22  
**Status**: ✅ Ready for Implementation  
**Next Phase**: Backend Development & Testing
