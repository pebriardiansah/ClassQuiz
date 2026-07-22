#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Psychological Test Scoring Engine untuk HR Rumah Sakit
Menggunakan klasifikasi Big Five Personality, Stress Resilience, dan Emotional Intelligence
Semua scoring dan interpretasi dalam Bahasa Indonesia

File: classquiz/algorithms/scoring_engine.py
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import json

class Recommendation(Enum):
    """Tipe rekomendasi"""
    PROCEED = "PROCEED"
    FURTHER_ASSESSMENT = "FURTHER_ASSESSMENT"
    CAUTION = "CAUTION"

@dataclass
class CandidateResponse:
    """Menyimpan respons kandidat"""
    candidate_id: str
    candidate_name: str
    position: str  # "dokter", "perawat", "bidan"
    responses: Dict[int, int]  # question_id -> score (1-5)
    test_date: str

@dataclass
class ScoringResult:
    """Hasil scoring tes"""
    candidate_name: str
    position: str
    personality_scores: Dict[str, float]
    stress_resilience: Dict[str, float]
    emotional_intelligence: Dict[str, float]
    overall_score: float
    recommendation: Recommendation
    red_flags: List[str]
    hr_recommendation: str
    next_step: str

class PsychologicalTestScoring:
    """Engine untuk scoring tes psikologis"""
    
    # Question mapping untuk Big Five (Questions 1-40)
    BIG_FIVE_MAPPING = {
        1: ("Openness", False),
        2: ("Conscientiousness", False),
        3: ("Extraversion", False),
        4: ("Agreeableness", False),
        5: ("Neuroticism", True),
        6: ("Openness", False),
        7: ("Conscientiousness", False),
        8: ("Extraversion", True),
        9: ("Agreeableness", False),
        10: ("Neuroticism", True),
        11: ("Openness", False),
        12: ("Conscientiousness", False),
        13: ("Extraversion", False),
        14: ("Agreeableness", False),
        15: ("Neuroticism", True),
        16: ("Openness", True),
        17: ("Conscientiousness", True),
        18: ("Extraversion", False),
        19: ("Agreeableness", True),
        20: ("Neuroticism", True),
        41: ("Openness", False),
        42: ("Conscientiousness", False),
        43: ("Extraversion", False),
        44: ("Agreeableness", False),
        45: ("Neuroticism", True),
        46: ("Openness", False),
        47: ("Conscientiousness", False),
        48: ("Extraversion", False),
        49: ("Agreeableness", False),
        50: ("Neuroticism", True),
    }
    
    # Stress Resilience mapping (Questions 21-30, 51-56)
    STRESS_MAPPING = {
        21: ("Handling", False),
        22: ("Resilience", False),
        23: ("Handling", False),
        24: ("Resilience", False),
        25: ("Handling", True),
        26: ("Resilience", False),
        27: ("Handling", False),
        28: ("Resilience", False),
        29: ("Handling", True),
        30: ("Resilience", False),
        51: ("Handling", False),
        52: ("Resilience", False),
        53: ("Handling", False),
        54: ("Resilience", False),
        55: ("Handling", False),
        56: ("Resilience", False),
    }
    
    # Emotional Intelligence mapping (Questions 31-40, 57-65)
    EQ_MAPPING = {
        31: ("SelfAwareness", False),
        32: ("SelfRegulation", False),
        33: ("Empathy", False),
        34: ("SocialSkills", False),
        35: ("Motivation", False),
        36: ("Empathy", False),
        37: ("SelfRegulation", True),
        38: ("SocialSkills", False),
        39: ("Empathy", True),
        40: ("Motivation", True),
        57: ("SelfAwareness", False),
        58: ("SelfRegulation", False),
        59: ("Empathy", False),
        60: ("SocialSkills", False),
        61: ("Motivation", False),
        62: ("Empathy", False),
        63: ("SocialSkills", False),
        64: ("SelfRegulation", False),
        65: ("Motivation", False),
    }
    
    IDEAL_SCORES = {
        "dokter": {
            "Conscientiousness": (4.0, 4.5),
            "Openness": (3.8, 4.2),
            "Agreeableness": (3.5, 4.0),
            "Emotional_Stability": (3.5, 4.0),
            "EQ_Overall": (3.5, 4.2),
            "Stress_Resilience": (3.2, 4.0),
        },
        "perawat": {
            "Agreeableness": (4.2, 4.6),
            "Conscientiousness": (4.0, 4.5),
            "Emotional_Stability": (3.5, 4.0),
            "EQ_Overall": (3.8, 4.3),
            "Stress_Resilience": (3.5, 4.2),
        },
        "bidan": {
            "Agreeableness": (4.3, 4.7),
            "Conscientiousness": (4.2, 4.6),
            "Emotional_Stability": (3.6, 4.1),
            "EQ_Overall": (4.0, 4.4),
            "Stress_Resilience": (3.6, 4.2),
        }
    }
    
    RED_FLAGS_THRESHOLDS = {
        "dokter": {
            "Neuroticism_high": 4.2,
            "Conscientiousness_low": 3.0,
            "Stress_Level_high": 4.0,
            "Empathy_low": 3.0,
        },
        "perawat": {
            "Agreeableness_low": 3.5,
            "Neuroticism_high": 4.0,
            "Stress_Level_high": 4.2,
        },
        "bidan": {
            "Agreeableness_critical_low": 3.6,
            "Conscientiousness_low": 3.8,
            "Neuroticism_high": 4.0,
        }
    }
    
    def __init__(self):
        self.responses = None
        
    def calculate_big_five_scores(self, responses: Dict[int, int]) -> Dict[str, float]:
        """Hitung skor Big Five Personality"""
        scores = {
            "Openness": [],
            "Conscientiousness": [],
            "Extraversion": [],
            "Agreeableness": [],
            "Neuroticism": []
        }
        
        for q_id, response_score in responses.items():
            if q_id in self.BIG_FIVE_MAPPING:
                dimension, is_reverse = self.BIG_FIVE_MAPPING[q_id]
                
                # Reverse scoring jika diperlukan
                if is_reverse:
                    response_score = 6 - response_score
                
                scores[dimension].append(response_score)
        
        # Hitung rata-rata untuk setiap dimensi
        avg_scores = {}
        for dimension, values in scores.items():
            if values:
                avg_scores[dimension] = sum(values) / len(values)
            else:
                avg_scores[dimension] = 0
        
        return avg_scores
    
    def calculate_stress_resilience_scores(self, responses: Dict[int, int]) -> Dict[str, float]:
        """Hitung skor Stress Resilience"""
        handling_scores = []
        resilience_scores = []
        
        for q_id, response_score in responses.items():
            if q_id in self.STRESS_MAPPING:
                dimension, is_reverse = self.STRESS_MAPPING[q_id]
                
                if is_reverse:
                    response_score = 6 - response_score
                
                if dimension == "Handling":
                    handling_scores.append(response_score)
                else:
                    resilience_scores.append(response_score)
        
        return {
            "handling": sum(handling_scores) / len(handling_scores) if handling_scores else 0,
            "resilience": sum(resilience_scores) / len(resilience_scores) if resilience_scores else 0,
        }
    
    def calculate_emotional_intelligence_scores(self, responses: Dict[int, int]) -> Dict[str, float]:
        """Hitung skor Emotional Intelligence"""
        eq_categories = {
            "SelfAwareness": [],
            "SelfRegulation": [],
            "Empathy": [],
            "SocialSkills": [],
            "Motivation": []
        }
        
        for q_id, response_score in responses.items():
            if q_id in self.EQ_MAPPING:
                category, is_reverse = self.EQ_MAPPING[q_id]
                
                if is_reverse:
                    response_score = 6 - response_score
                
                eq_categories[category].append(response_score)
        
        eq_scores = {}
        for category, values in eq_categories.items():
            eq_scores[category] = sum(values) / len(values) if values else 0
        
        # Overall EQ
        all_scores = [score for scores in eq_categories.values() for score in scores]
        eq_scores["Overall"] = sum(all_scores) / len(all_scores) if all_scores else 0
        
        return eq_scores
    
    def identify_red_flags(self, 
                          big_five: Dict[str, float],
                          stress: Dict[str, float],
                          eq: Dict[str, float],
                          position: str) -> List[str]:
        """Identifikasi red flags untuk posisi tertentu"""
        red_flags = []
        thresholds = self.RED_FLAGS_THRESHOLDS.get(position, {})
        
        if position == "dokter":
            if big_five.get("Neuroticism", 0) > thresholds.get("Neuroticism_high", 4.2):
                red_flags.append("⚠️ Tingkat neuroticism tinggi - cenderung cemas/khawatir")
            
            if big_five.get("Conscientiousness", 0) < thresholds.get("Conscientiousness_low", 3.0):
                red_flags.append("❌ Conscientiousness rendah - risiko kesalahan medis")
            
            if stress.get("handling", 0) < 3.0 or stress.get("resilience", 0) < 3.0:
                red_flags.append("⚠️ Ketahanan stress rendah - tidak siap untuk beban kerja medis")
            
            if eq.get("Empathy", 0) < thresholds.get("Empathy_low", 3.0):
                red_flags.append("⚠️ Empati rendah - kurang sesuai untuk patient care")
        
        elif position == "perawat":
            if big_five.get("Agreeableness", 0) < thresholds.get("Agreeableness_low", 3.5):
                red_flags.append("❌ Agreeableness rendah - kurang empati untuk patient care")
            
            if big_five.get("Neuroticism", 0) > thresholds.get("Neuroticism_high", 4.0):
                red_flags.append("⚠️ Neuroticism tinggi - mudah mengalami burnout")
            
            if stress.get("handling", 0) < 3.0 or stress.get("resilience", 0) < 3.5:
                red_flags.append("⚠️ Stress resilience rendah - tidak tahan dalam situasi darurat")
        
        elif position == "bidan":
            if big_five.get("Agreeableness", 0) < thresholds.get("Agreeableness_critical_low", 3.6):
                red_flags.append("❌ Agreeableness kritis rendah - tidak sesuai untuk maternal care")
            
            if big_five.get("Conscientiousness", 0) < thresholds.get("Conscientiousness_low", 3.8):
                red_flags.append("❌ Conscientiousness rendah - penting untuk safety prosedur")
            
            if big_five.get("Neuroticism", 0) > thresholds.get("Neuroticism_high", 4.0):
                red_flags.append("⚠️ Pregnant mothers sangat sensitive - stability penting")
        
        return red_flags
    
    def calculate_overall_score(self,
                               big_five: Dict[str, float],
                               stress: Dict[str, float],
                               eq: Dict[str, float],
                               position: str) -> float:
        """Hitung overall score berdasarkan position"""
        weights = {
            "dokter": {
                "Conscientiousness": 0.25,
                "Openness": 0.20,
                "Agreeableness": 0.15,
                "Emotional_Stability": 0.15,
                "EQ_Overall": 0.15,
                "Stress_Resilience": 0.10,
            },
            "perawat": {
                "Agreeableness": 0.30,
                "Conscientiousness": 0.20,
                "Stress_Resilience": 0.20,
                "EQ_Overall": 0.20,
                "Emotional_Stability": 0.10,
            },
            "bidan": {
                "Agreeableness": 0.30,
                "Conscientiousness": 0.25,
                "Stress_Resilience": 0.20,
                "EQ_Overall": 0.15,
                "Emotional_Stability": 0.10,
            }
        }
        
        weight_dict = weights.get(position, weights["dokter"])
        overall = 0
        
        for component, weight in weight_dict.items():
            if "Stress_Resilience" in component:
                score = (stress.get("handling", 0) + stress.get("resilience", 0)) / 2
            elif "EQ_Overall" in component:
                score = eq.get("Overall", 0)
            elif component == "Emotional_Stability":
                score = 5 - big_five.get("Neuroticism", 0)  # Inverse of neuroticism
            else:
                score = big_five.get(component, 0)
            
            overall += score * weight
        
        return overall
    
    def get_recommendation(self,
                          overall_score: float,
                          red_flags: List[str],
                          position: str) -> Tuple[Recommendation, str, str]:
        """Tentukan rekomendasi berdasarkan skor dan red flags"""
        
        if len(red_flags) >= 2:
            recommendation = Recommendation.CAUTION
            if position == "dokter":
                hr_rec = "Ada indikasi signifikan yang perlu dievaluasi lebih lanjut. Disarankan konsultasi dengan psikolog profesional sebelum hiring."
                next_step = "Tinjau Ulang atau Rujuk ke Psikolog Profesional"
            elif position == "perawat":
                hr_rec = "Ada beberapa indikasi perhatian. Pertimbangkan training khusus atau evaluasi lebih mendalam."
                next_step = "Assessment Lanjutan dengan Psikolog"
            else:  # bidan
                hr_rec = "Ada indikasi yang perlu dievaluasi. Maternal care memerlukan stabilitas emosional tinggi."
                next_step = "Konsultasi Psikolog sebelum Placement"
        
        elif len(red_flags) == 1 or overall_score < 3.4:
            recommendation = Recommendation.FURTHER_ASSESSMENT
            hr_rec = "Ada beberapa aspek yang perlu dikonfirmasi lebih lanjut. Lakukan interview mendalam dengan HR."
            next_step = "Verification Interview dengan HR"
        
        else:
            recommendation = Recommendation.PROCEED
            if position == "dokter":
                hr_rec = "Kandidat menunjukkan profil psikologis yang sesuai untuk posisi dokter. Lanjutkan ke tahap interview teknis."
                next_step = "Interview Tahap 2 - Medical Knowledge & Clinical Skills"
            elif position == "perawat":
                hr_rec = "Kandidat menunjukkan profil yang sesuai untuk perawatan pasien. Lanjutkan ke tahap interview berikutnya."
                next_step = "Interview Tahap 2 - Clinical Skills & Team Fit"
            else:  # bidan
                hr_rec = "Kandidat menunjukkan potensi yang baik untuk maternal care. Lanjutkan ke tahap interview berikutnya."
                next_step = "Interview Tahap 2 - Obstetric Knowledge & Experience"
        
        return recommendation, hr_rec, next_step
    
    def score_test(self, responses: CandidateResponse) -> ScoringResult:
        """Scoring lengkap untuk semua aspek tes"""
        
        self.responses = responses
        position = responses.position.lower()
        
        # Hitung semua skor
        big_five = self.calculate_big_five_scores(responses.responses)
        stress = self.calculate_stress_resilience_scores(responses.responses)
        eq = self.calculate_emotional_intelligence_scores(responses.responses)
        
        # Hitung overall score
        overall = self.calculate_overall_score(big_five, stress, eq, position)
        
        # Identifikasi red flags
        red_flags = self.identify_red_flags(big_five, stress, eq, position)
        
        # Get recommendation
        recommendation, hr_rec, next_step = self.get_recommendation(overall, red_flags, position)
        
        return ScoringResult(
            candidate_name=responses.candidate_name,
            position=position,
            personality_scores=big_five,
            stress_resilience=stress,
            emotional_intelligence=eq,
            overall_score=overall,
            recommendation=recommendation,
            red_flags=red_flags,
            hr_recommendation=hr_rec,
            next_step=next_step
        )


if __name__ == "__main__":
    # Contoh penggunaan
    engine = PsychologicalTestScoring()
    
    sample_responses = CandidateResponse(
        candidate_id="CAND001",
        candidate_name="Dr. Ahmad Rakhmat",
        position="Dokter",
        responses={
            1: 4, 2: 5, 3: 3, 4: 4, 5: 2,
            6: 4, 7: 5, 8: 2, 9: 4, 10: 4,
            11: 4, 12: 5, 13: 3, 14: 4, 15: 2,
            16: 3, 17: 4, 18: 3, 19: 2, 20: 3,
            21: 4, 22: 4, 23: 4, 24: 4, 25: 2,
            26: 4, 27: 4, 28: 4, 29: 2, 30: 4,
            31: 4, 32: 4, 33: 4, 34: 4, 35: 5,
            36: 4, 37: 2, 38: 4, 39: 2, 40: 2,
        },
        test_date="2026-07-22"
    )
    
    result = engine.score_test(sample_responses)
    
    print("\n" + "="*70)
    print(f"📋 HASIL SKRINING PSIKOLOGIS")
    print("="*70)
    print(f"Nama Kandidat: {result.candidate_name}")
    print(f"Posisi: {result.position.upper()}")
    print(f"Overall Score: {result.overall_score:.2f}/5.0")
    print(f"Rekomendasi: {result.recommendation.value}")
    print("\n📊 SKOR PERSONALITY (Big Five):")
    for trait, score in result.personality_scores.items():
        print(f"  {trait}: {score:.2f}")
    print("\n⚡ STRESS RESILIENCE:")
    print(f"  Handling: {result.stress_resilience['handling']:.2f}")
    print(f"  Resilience: {result.stress_resilience['resilience']:.2f}")
    print("\n❤️ EMOTIONAL INTELLIGENCE:")
    for category, score in result.emotional_intelligence.items():
        print(f"  {category}: {score:.2f}")
    
    if result.red_flags:
        print("\n🚩 RED FLAGS:")
        for flag in result.red_flags:
            print(f"  {flag}")
    
    print(f"\n💡 REKOMENDASI HR:")
    print(f"  {result.hr_recommendation}")
    print(f"\n📍 LANGKAH SELANJUTNYA:")
    print(f"  {result.next_step}")
    print("="*70 + "\n")
