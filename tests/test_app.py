"""Tests for the Mergington High School API"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestGetActivities:
    """Test the GET /activities endpoint"""

    def test_get_activities_returns_dict(self):
        """Test that /activities returns a dictionary of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_contains_basketball(self):
        """Test that activities include Basketball"""
        response = client.get("/activities")
        data = response.json()
        assert "Basketball" in data

    def test_get_activities_contains_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self):
        """Test successful signup for an activity"""
        response = client.post("/activities/Basketball/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_already_registered(self):
        """Test signup when student is already registered"""
        email = "james@mergington.edu"
        response = client.post(f"/activities/Basketball/signup?email={email}")
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_adds_participant_to_list(self):
        """Test that signup actually adds participant to the activity"""
        new_email = "unique_test@mergington.edu"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Tennis Club"]["participants"])
        
        # Sign up
        client.post(f"/activities/Tennis Club/signup?email={new_email}")
        
        # Check new count
        response = client.get("/activities")
        new_count = len(response.json()["Tennis Club"]["participants"])
        assert new_count == initial_count + 1


class TestUnregisterFromActivity:
    """Test the POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregister from an activity"""
        email = "michael@mergington.edu"
        response = client.post(f"/activities/Chess Club/unregister?email={email}")
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]

    def test_unregister_activity_not_found(self):
        """Test unregister from non-existent activity"""
        response = client.post("/activities/NonExistent/unregister?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_not_registered(self):
        """Test unregister when student is not registered"""
        response = client.post("/activities/Basketball/unregister?email=notregistered@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_removes_participant(self):
        """Test that unregister actually removes participant from the activity"""
        # First, sign up a student
        new_email = "temp_student@mergington.edu"
        client.post(f"/activities/Art Studio/signup?email={new_email}")
        
        # Get count after signup
        response = client.get("/activities")
        count_after_signup = len(response.json()["Art Studio"]["participants"])
        
        # Unregister
        client.post(f"/activities/Art Studio/unregister?email={new_email}")
        
        # Check count after unregister
        response = client.get("/activities")
        count_after_unregister = len(response.json()["Art Studio"]["participants"])
        assert count_after_unregister == count_after_signup - 1


class TestRootEndpoint:
    """Test the GET / endpoint"""

    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
