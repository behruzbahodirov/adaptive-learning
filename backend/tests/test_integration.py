"""
Integration Tests - Adaptiv Ta'lim MVP
"""

import pytest
import requests
import json
from typing import Dict

BASE_URL = "http://localhost:8000"


class TestChatAPI:
    """Chat API testlari"""
    
    def test_health_check(self):
        """Health check endpoint"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "✅" in data["status"]
    
    def test_start_chat(self):
        """Chat sessiyasini boshlash"""
        response = requests.post(
            f"{BASE_URL}/api/chat/start",
            json={"student_name": "Ali"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["student_name"] == "Ali"
        assert "timestamp" in data
    
    def test_send_message(self):
        """Xabar yuborish va AI javob olish"""
        # 1. Chat boshlash
        start_response = requests.post(
            f"{BASE_URL}/api/chat/start",
            json={"student_name": "Zuhra"}
        )
        session_id = start_response.json()["session_id"]
        
        # 2. Xabar yuborish
        message_response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json={
                "session_id": session_id,
                "student_name": "Zuhra",
                "message": "2+3 nechaga?",
                "topic": "Matematika"
            }
        )
        
        assert message_response.status_code == 200
        data = message_response.json()
        assert "ai_response" in data
        assert "analytics" in data
        assert "session_id" in data
        assert data["session_id"] == session_id
    
    def test_multiple_messages(self):
        """Bir necha xabar yuborish"""
        start_response = requests.post(
            f"{BASE_URL}/api/chat/start",
            json={"student_name": "Kamron"}
        )
        session_id = start_response.json()["session_id"]
        
        messages = [
            "2+3 nechaga?",
            "5+5 nechaga?",
            "10-3 nechaga?"
        ]
        
        for msg in messages:
            response = requests.post(
                f"{BASE_URL}/api/chat/message",
                json={
                    "session_id": session_id,
                    "student_name": "Kamron",
                    "message": msg,
                    "topic": "Matematika"
                }
            )
            assert response.status_code == 200
            assert "analytics" in response.json()
    
    def test_invalid_session(self):
        """Noto'g'ri sessiya ID bilan xabar yuborish"""
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json={
                "session_id": "invalid-session-id",
                "student_name": "Test",
                "message": "Test",
                "topic": "Test"
            }
        )
        assert response.status_code == 404


class TestDashboard:
    """Dashboard API testlari"""
    
    def test_dashboard_empty(self):
        """Bo'sh dashboard"""
        response = requests.get(f"{BASE_URL}/api/teacher/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "total_students" in data
        assert "students_analytics" in data
        assert "recommendations" in data
    
    def test_dashboard_with_students(self):
        """Students bilan dashboard"""
        # 1. Bir necha o'quvchi qo'shish
        students = ["Ali", "Zuhra", "Kamron"]
        for student in students:
            start = requests.post(
                f"{BASE_URL}/api/chat/start",
                json={"student_name": student}
            )
            session_id = start.json()["session_id"]
            
            # 2. Har bir o'quvchi uchun xabar
            requests.post(
                f"{BASE_URL}/api/chat/message",
                json={
                    "session_id": session_id,
                    "student_name": student,
                    "message": "2+3 nechaga?",
                    "topic": "Matematika"
                }
            )
        
        # 3. Dashboard tekshirish
        response = requests.get(f"{BASE_URL}/api/teacher/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["total_students"] >= 1
        assert len(data["students_analytics"]) > 0


class TestAnalytics:
    """Analytics API testlari"""
    
    def test_analytics_structure(self):
        """Analytics JSON strukturasi"""
        start = requests.post(
            f"{BASE_URL}/api/chat/start",
            json={"student_name": "TestStudent"}
        )
        session_id = start.json()["session_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json={
                "session_id": session_id,
                "student_name": "TestStudent",
                "message": "2+3 nechaga?",
                "topic": "Math"
            }
        )
        
        analytics = response.json()["analytics"]
        assert "logical_thinking" in analytics
        assert "concept_understanding" in analytics
        assert "motivation" in analytics
        assert "recommendation" in analytics
        assert "status" in analytics
        
        # Qiymatlari 1-5 orasida bo'lishi kerak
        assert 1 <= analytics["logical_thinking"] <= 5
        assert 1 <= analytics["concept_understanding"] <= 5
        assert 1 <= analytics["motivation"] <= 5
    
    def test_analytics_extraction(self):
        """Analytics ajratib olish"""
        start = requests.post(
            f"{BASE_URL}/api/chat/start",
            json={"student_name": "AnalyticsTest"}
        )
        session_id = start.json()["session_id"]
        
        # 3 ta xabar yuborish
        for msg in ["2+3?", "5+5?", "10-3?"]:
            requests.post(
                f"{BASE_URL}/api/chat/message",
                json={
                    "session_id": session_id,
                    "student_name": "AnalyticsTest",
                    "message": msg,
                    "topic": "Math"
                }
            )
        
        # Dashboard dan o'quvchi ma'lumotlarini olib kelish
        dashboard = requests.get(f"{BASE_URL}/api/teacher/dashboard").json()
        student = next((s for s in dashboard["students_analytics"] 
                       if s["student_name"] == "AnalyticsTest"), None)
        
        assert student is not None
        assert student["message_count"] >= 3
    
    def test_negative_motivation_detection(self):
        """Negative motivatsiya aniqlanadi"""
        start = requests.post(
            f"{BASE_URL}/api/chat/start",
            json={"student_name": "NegativeTest"}
        )
        session_id = start.json()["session_id"]
        
        # Negative xabar
        response = requests.post(
            f"{BASE_URL}/api/chat/message",
            json={
                "session_id": session_id,
                "student_name": "NegativeTest",
                "message": "Bilmadim, qiyna",
                "topic": "Math"
            }
        )
        
        analytics = response.json()["analytics"]
        assert analytics["motivation"] < 3
    
    def test_recommendation_generation(self):
        """Tavsiya yaratiladi"""
        start = requests.post(
            f"{BASE_URL}/api/chat/start",
            json={"student_name": "RecommendTest"}
        )
        session_id = start.json()["session_id"]
        
        requests.post(
            f"{BASE_URL}/api/chat/message",
            json={
                "session_id": session_id,
                "student_name": "RecommendTest",
                "message": "Bilmadim",
                "topic": "Math"
            }
        )
        
        dashboard = requests.get(f"{BASE_URL}/api/teacher/dashboard").json()
        student = next((s for s in dashboard["students_analytics"] 
                       if s["student_name"] == "RecommendTest"), None)
        
        assert student is not None
        assert student["recommendation"] != ""
        assert len(student["recommendation"]) > 10


class TestStats:
    """Stats API testlari"""
    
    def test_stats_endpoint(self):
        """Stats endpoint"""
        response = requests.get(f"{BASE_URL}/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_students" in data
        assert "total_sessions" in data
        assert "total_messages" in data
        assert "active_sessions" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
