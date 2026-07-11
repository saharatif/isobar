import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

SAMPLE_RESUME = """Jane Doe
Senior Backend Engineer

Summary
Senior engineer with 9 years experience building Python services on AWS.

Skills
Python, FastAPI, Postgres, Docker, Kubernetes, AWS

Experience
Senior Backend Engineer — Northwind (2020 - present)
Built FastAPI microservices on AWS with Postgres and Docker.

Backend Engineer — Fabrikam (2016 - 2020)
Python and SQL data pipelines.
"""


def make_settings(tmp_path, **overrides) -> Settings:
    defaults = dict(
        database_url=f"sqlite+aiosqlite:///{tmp_path}/test.db",
        storage_dir=tmp_path / "uploads",
        openai_api_key=None,  # forces the offline KeywordExtractor
        seed_demo_jobs=True,
        _env_file=None,  # tests must not pick up a developer's .env
    )
    defaults.update(overrides)
    return Settings(**defaults)


@pytest.fixture()
def settings(tmp_path) -> Settings:
    return make_settings(tmp_path)


@pytest.fixture()
def client(settings):
    app = create_app(settings)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def uploaded_resume(client) -> dict:
    response = client.post(
        "/uploads",
        files={"file": ("jane.txt", SAMPLE_RESUME.encode(), "text/plain")},
    )
    assert response.status_code == 201
    return response.json()
