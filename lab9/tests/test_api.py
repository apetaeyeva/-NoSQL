"""Тесты HTTP-слоя без запущенной СУБД: репозиторий подменён in-memory fake."""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app, get_repository  # noqa: E402
from repository import InMemoryCourseRepository  # noqa: E402

COURSE = {"code": "NOSQL301", "title": "NoSQL design", "teacher": "Ivanov A.",
          "room": "A-204", "credits": 4}


@pytest.fixture
def repo():
    r = InMemoryCourseRepository()
    app.dependency_overrides[get_repository] = lambda: r
    yield r
    app.dependency_overrides.clear()


@pytest.fixture
def client(repo):
    return TestClient(app, raise_server_exceptions=False)


def test_create_and_get(client):
    assert client.post("/courses", json=COURSE).status_code == 201
    r = client.get("/courses/NOSQL301")
    assert r.status_code == 200 and r.json()["room"] == "A-204"


def test_not_found(client):
    r = client.get("/courses/NOSQL999")
    assert r.status_code == 404 and r.json()["detail"] == "Course not found"


def test_validation_error(client):
    bad = {**COURSE, "code": "bad code", "credits": 99}
    assert client.post("/courses", json=bad).status_code == 422
    assert client.get("/courses/bad-code").status_code == 422


def test_duplicate(client):
    client.post("/courses", json=COURSE)
    assert client.post("/courses", json=COURSE).status_code == 409


def test_list_by_teacher(client):
    client.post("/courses", json=COURSE)
    client.post("/courses", json={**COURSE, "code": "DB302", "teacher": "Petrova M."})
    r = client.get("/courses", params={"teacher": "Ivanov A."})
    assert [c["code"] for c in r.json()] == ["NOSQL301"]
    assert len(client.get("/courses").json()) == 2


def test_update_room(client):
    client.post("/courses", json=COURSE)
    r = client.patch("/courses/NOSQL301/room", json={"room": "B-101"})
    assert r.status_code == 200 and r.json()["room"] == "B-101"
    assert client.patch("/courses/NOSQL999/room", json={"room": "B-1"}).status_code == 404


def test_delete(client):
    client.post("/courses", json=COURSE)
    assert client.delete("/courses/NOSQL301").status_code == 204
    assert client.delete("/courses/NOSQL301").status_code == 404


def test_storage_unavailable_returns_503(client, repo):
    repo.available = False
    r = client.get("/courses/NOSQL301")
    assert r.status_code == 503
    assert r.json() == {"detail": "Storage temporarily unavailable"}
    assert "mongodb" not in r.text.lower()


def test_unexpected_error_returns_500_without_details(client, repo):
    def boom(_):
        raise RuntimeError("secret mongodb://user:pass@host")
    repo.get_by_code = boom
    r = client.get("/courses/NOSQL301")
    assert r.status_code == 500 and "secret" not in r.text
