from fastapi.testclient import TestClient
from app.models.member import Member
from sqlalchemy.orm import Session


async def test_register_member(client: TestClient, db_session: Session):
    response = client.post("/api/v1/register", json={
        "name": "John Doe",
        "email": "john@example.com",
        "password": "secret88"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert "id" in data

    member = db_session.query(Member).filter(Member.email == "john@example.com").first()
    assert member is not None
    assert member.verify_password("secret88")


async def test_register_duplicate_email(client: TestClient, db_session: Session):
    client.post("/api/v1/register", json={
        "name": "John Doe",
        "email": "john@example.com",
        "password": "secret88"
    })
    response = client.post("/api/v1/register", json={
        "name": "Jane Doe",
        "email": "john@example.com",
        "password": "secret88"
    })
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}
