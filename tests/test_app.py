import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture to provide a TestClient and isolate activities state per test.
    Saves the original activities, restores after each test.
    """
    # Deep copy the original activities
    original_activities = copy.deepcopy(activities)
    
    yield TestClient(app)
    
    # Restore original activities after test completes
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities(self, client):
        """
        Arrange: Create test client.
        Act: Call GET /activities.
        Assert: Status 200 and response contains expected activity keys.
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        
        # Verify activity structure
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client):
        """
        Arrange: Create test client, select activity, pick a new email.
        Act: POST to /activities/{activity_name}/signup?email=...
        Assert: Status 200, message includes email, participant added.
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert email in data["message"]
        assert email in activities[activity_name]["participants"]
    
    def test_signup_duplicate(self, client):
        """
        Arrange: Create test client, identify existing participant.
        Act: POST signup for already-registered participant.
        Assert: Status 400, response contains 'already signed up'.
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_invalid_activity(self, client):
        """
        Arrange: Create test client, prepare non-existent activity name.
        Act: POST to /activities/{invalid}/signup?email=...
        Assert: Status 404, response contains 'Activity not found'.
        """
        # Arrange
        activity_name = "NonExistentActivity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in data["detail"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""
    
    def test_remove_participant_success(self, client):
        """
        Arrange: Create test client, select activity with participants.
        Act: DELETE /activities/{activity_name}/participants?email=...
        Assert: Status 200, confirmation message, participant removed.
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Existing participant
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert email in data["message"]
        assert email not in activities[activity_name]["participants"]
    
    def test_remove_participant_not_registered(self, client):
        """
        Arrange: Create test client, select activity, pick unregistered email.
        Act: DELETE /activities/{activity_name}/participants?email=...
        Assert: Status 404, response contains 'not registered'.
        """
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"  # Not registered
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "not registered" in data["detail"].lower()
