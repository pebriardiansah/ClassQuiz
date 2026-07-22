#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementation Guide Code Examples
Kode-kode siap pakai untuk integrasi ke ClassQuiz backend
"""

# ============================================================================
# 1. FASTAPI ROUTES - Tambahkan ke classquiz/routes/psychological_tests.py
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
import json

router = APIRouter(prefix="/api/psychological", tags=["Psychological Screening"])

# ---- GET TESTS ----
@router.get("/tests")
async def get_available_tests(
    position: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get available psychological tests
    Filter by position: 'dokter', 'perawat', 'bidan'
    """
    query = db.query(PsychologicalTest).filter(
        PsychologicalTest.is_active == True
    )
    
    if position:
        query = query.filter(
            PsychologicalTest.target_position == position.lower()
        )
    
    tests = query.all()
    return {
        "total": len(tests),
        "tests": [
            {
                "id": t.id,
                "title": t.title,
                "position": t.target_position,
                "duration": t.duration_minutes,
                "questions": t.total_questions
            }
            for t in tests
        ]
    }

@router.get("/tests/{test_id}")
async def get_test_details(
    test_id: str,
    db: Session = Depends(get_db)
):
    """
    Get full test details with all questions
    """
    test = db.query(PsychologicalTest).filter(
        PsychologicalTest.id == test_id
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    questions = db.query(PsychologicalQuestion).filter(
        PsychologicalQuestion.test_id == test_id
    ).order_by(PsychologicalQuestion.question_number).all()
    
    return {
        "id": test.id,
        "title": test.title,
        "description": test.description,
        "duration": test.duration_minutes,
        "questions": [
            {
                "id": q.id,
                "number": q.question_number,
                "text": q.text,
                "dimension": q.dimension,
                "type": "likert5"  # Fixed for now
            }
            for q in questions
        ]
    }

# ---- SUBMIT RESPONSES ----
@router.post("/responses/submit")
async def submit_test_responses(
    participant_id: str,
    test_id: str,
    responses: Dict[int, int],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Submit test responses and trigger automatic scoring
    
    responses: {question_id: score}
    """
    import asyncio
    from classquiz.algorithms.scoring_engine import PsychologicalTestScoring
    
    # 1. Validate participant
    participant = db.query(Participant).filter(
        Participant.id == participant_id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    # 2. Validate test
    test = db.query(PsychologicalTest).filter(
        PsychologicalTest.id == test_id
    ).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # 3. Save responses to database
    for question_id, score in responses.items():
        response = PsychologicalResponse(
            id=str(uuid.uuid4()),
            participant_id=participant_id,
            test_id=test_id,
            question_id=question_id,
            response_score=score,
            created_at=datetime.now()
        )
        db.add(response)
    
    db.commit()
    
    # 4. Run scoring engine
    scoring = PsychologicalTestScoring()
    result = scoring.score_test(
        responses=responses,
        position=test.target_position
    )
    
    # 5. Save result to database
    db_result = PsychologicalResult(
        id=str(uuid.uuid4()),
        participant_id=participant_id,
        test_id=test_id,
        test_taken_at=datetime.now(),
        openness=result.personality_scores.get('Openness', 0),
        conscientiousness=result.personality_scores.get('Conscientiousness', 0),
        extraversion=result.personality_scores.get('Extraversion', 0),
        agreeableness=result.personality_scores.get('Agreeableness', 0),
        neuroticism=result.personality_scores.get('Neuroticism', 0),
        stress_handling=result.stress_resilience.get('handling', 0),
        stress_resilience=result.stress_resilience.get('resilience', 0),
        eq_self_awareness=result.emotional_intelligence.get('SelfAwareness', 0),
        eq_self_regulation=result.emotional_intelligence.get('SelfRegulation', 0),
        eq_empathy=result.emotional_intelligence.get('Empathy', 0),
        eq_social_skills=result.emotional_intelligence.get('SocialSkills', 0),
        eq_motivation=result.emotional_intelligence.get('Motivation', 0),
        eq_overall=result.emotional_intelligence.get('Overall', 0),
        overall_score=result.overall_score,
        recommendation=result.recommendation.value,
        red_flags=json.dumps(result.red_flags),
        created_at=datetime.now()
    )
    
    db.add(db_result)
    db.commit()
    
    # 6. Send notification (if enabled)
    if os.getenv('PSYCH_ENABLE_NOTIFICATIONS') == 'true':
        await send_result_notification(participant, result)
    
    return {
        "status": "success",
        "result_id": db_result.id,
        "overall_score": result.overall_score,
        "recommendation": result.recommendation.value,
        "message": "Test responses submitted successfully"
    }

# ---- GET RESULT ----
@router.get("/results/{result_id}")
async def get_result(
    result_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed result with interpretation
    """
    result = db.query(PsychologicalResult).filter(
        PsychologicalResult.id == result_id
    ).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return {
        "id": result.id,
        "participant_id": result.participant_id,
        "overall_score": result.overall_score,
        "recommendation": result.recommendation,
        "personality_scores": {
            "Openness": result.openness,
            "Conscientiousness": result.conscientiousness,
            "Extraversion": result.extraversion,
            "Agreeableness": result.agreeableness,
            "Neuroticism": result.neuroticism
        },
        "stress_resilience": {
            "handling": result.stress_handling,
            "resilience": result.stress_resilience
        },
        "emotional_intelligence": {
            "self_awareness": result.eq_self_awareness,
            "self_regulation": result.eq_self_regulation,
            "empathy": result.eq_empathy,
            "social_skills": result.eq_social_skills,
            "motivation": result.eq_motivation,
            "overall": result.eq_overall
        },
        "red_flags": json.loads(result.red_flags),
        "test_taken_at": result.test_taken_at
    }

# ---- HR DASHBOARD ----
@router.get("/dashboard/candidates")
async def get_candidates(
    position: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_hr_user)
):
    """
    Get list of candidates with screening results for HR
    """
    query = db.query(Participant, PsychologicalResult).outerjoin(
        PsychologicalResult,
        Participant.id == PsychologicalResult.participant_id
    ).filter(
        Participant.organization_id == current_user.organization_id
    )
    
    if position:
        query = query.filter(Participant.position_applied == position.lower())
    
    if status:
        query = query.filter(Participant.status == status)
    
    total = query.count()
    candidates = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "candidates": [
            {
                "id": p.id,
                "name": p.full_name,
                "email": p.email,
                "position": p.position_applied,
                "overall_score": r.overall_score if r else None,
                "recommendation": r.recommendation if r else None,
                "test_date": r.created_at.isoformat() if r else None
            }
            for p, r in candidates
        ]
    }


# ============================================================================
# 2. DATABASE MODELS - Tambahkan ke classquiz/models/
# ============================================================================

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class PsychologicalTest(Base):
    __tablename__ = "psychological_tests"
    
    id = Column(String(36), primary_key=True)
    test_code = Column(String(50), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    target_position = Column(String(100), nullable=False)  # dokter, perawat, bidan
    test_type = Column(String(50))  # personality, stress, mental_health
    duration_minutes = Column(Integer, default=30)
    total_questions = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    questions = relationship("PsychologicalQuestion", back_populates="test")
    results = relationship("PsychologicalResult", back_populates="test")

class PsychologicalQuestion(Base):
    __tablename__ = "psychological_questions"
    
    id = Column(String(36), primary_key=True)
    test_id = Column(String(36), ForeignKey("psychological_tests.id"))
    question_number = Column(Integer)
    text = Column(String(500), nullable=False)
    dimension = Column(String(100))
    question_type = Column(String(50), default="likert5")
    is_reverse = Column(Boolean, default=False)
    weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.now)
    
    test = relationship("PsychologicalTest", back_populates="questions")

class PsychologicalResponse(Base):
    __tablename__ = "psychological_responses"
    
    id = Column(String(36), primary_key=True)
    participant_id = Column(String(36), ForeignKey("participants.id"))
    test_id = Column(String(36), ForeignKey("psychological_tests.id"))
    question_id = Column(String(36), ForeignKey("psychological_questions.id"))
    response_score = Column(Integer)  # 1-5
    created_at = Column(DateTime, default=datetime.now)

class PsychologicalResult(Base):
    __tablename__ = "psychological_results"
    
    id = Column(String(36), primary_key=True)
    participant_id = Column(String(36), ForeignKey("participants.id"))
    test_id = Column(String(36), ForeignKey("psychological_tests.id"))
    test_taken_at = Column(DateTime)
    
    # Big Five
    openness = Column(Float)
    conscientiousness = Column(Float)
    extraversion = Column(Float)
    agreeableness = Column(Float)
    neuroticism = Column(Float)
    
    # Stress
    stress_handling = Column(Float)
    stress_resilience = Column(Float)
    
    # EQ
    eq_self_awareness = Column(Float)
    eq_self_regulation = Column(Float)
    eq_empathy = Column(Float)
    eq_social_skills = Column(Float)
    eq_motivation = Column(Float)
    eq_overall = Column(Float)
    
    # Overall
    overall_score = Column(Float)
    recommendation = Column(String(50))  # PROCEED, FURTHER_ASSESSMENT, CAUTION
    red_flags = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    test = relationship("PsychologicalTest", back_populates="results")

class Participant(Base):
    __tablename__ = "participants"
    
    id = Column(String(36), primary_key=True)
    full_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(20))
    position_applied = Column(String(100))  # dokter, perawat, bidan
    status = Column(String(50), default="pending")  # pending, completed, hired, rejected
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# ============================================================================
# 3. INTEGRATION EXAMPLE - Cara menggunakan dari aplikasi
# ============================================================================

from classquiz.algorithms.scoring_engine import PsychologicalTestScoring, CandidateResponse

def example_usage():
    """Contoh cara menggunakan scoring engine"""
    
    # Create scoring engine instance
    engine = PsychologicalTestScoring()
    
    # Prepare candidate responses
    responses = CandidateResponse(
        candidate_id="CAND001",
        candidate_name="Dr. Ahmad",
        position="Dokter",
        responses={
            1: 4, 2: 5, 3: 3, 4: 4, 5: 2,
            6: 4, 7: 5, 8: 2, 9: 4, 10: 4,
            # ... more responses ...
        },
        test_date="2026-07-22"
    )
    
    # Score the test
    result = engine.score_test(responses)
    
    # Use results
    print(f"Overall Score: {result.overall_score}")
    print(f"Recommendation: {result.recommendation.value}")
    print(f"Red Flags: {result.red_flags}")
    print(f"HR Recommendation: {result.hr_recommendation}")
    
    return result

if __name__ == "__main__":
    example_usage()
