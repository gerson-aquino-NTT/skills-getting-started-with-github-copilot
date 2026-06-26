import copy

import pytest
from httpx import AsyncClient, ASGITransport

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


@pytest.mark.anyio
async def test_get_activities():
    # Arrange
    transport = ASGITransport(app=app)

    # Act
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


@pytest.mark.anyio
async def test_signup_success():
    # Arrange
    transport = ASGITransport(app=app)
    email = "teststudent@mergington.edu"

    # Act
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


@pytest.mark.anyio
async def test_duplicate_signup_error():
    # Arrange
    transport = ASGITransport(app=app)
    email = "michael@mergington.edu"

    # Act
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


@pytest.mark.anyio
async def test_remove_existing_participant():
    # Arrange
    transport = ASGITransport(app=app)
    email = "daniel@mergington.edu"

    # Act
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.delete("/activities/Chess Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


@pytest.mark.anyio
async def test_remove_missing_participant_error():
    # Arrange
    transport = ASGITransport(app=app)
    email = "missing@mergington.edu"

    # Act
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.delete("/activities/Chess Club/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
