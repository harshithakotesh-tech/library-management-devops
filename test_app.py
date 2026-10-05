import pytest
from app import app

@pytest.fixture
def client(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setattr("app.DB", str(db))
    from app import init_db
    init_db()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Library Management System" in response.data

def test_add_book(client):
    response = client.post("/add", data={
        "title": "Python Basics",
        "author": "John",
        "category": "Programming",
        "isbn": "123",
        "publisher": "ABC",
        "quantity": "2"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Python Basics" in response.data

def test_issue_and_return(client):
    client.post("/add", data={
        "title": "DevOps",
        "author": "Jane",
        "category": "DevOps",
        "isbn": "456",
        "publisher": "XYZ",
        "quantity": "2"
    })
    response = client.get("/issue/1", follow_redirects=True)
    assert b">1<" in response.data
    response = client.get("/return/1", follow_redirects=True)
    assert b">2<" in response.data

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}
