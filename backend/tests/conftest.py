"""Skupne nastavitve testov. Testi tecejo na loceni bazi (glej DATABASE_URL spodaj)."""

import os

os.environ.setdefault(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/bookshelf_test"
)
os.environ.setdefault("FIREBASE_CREDENTIALS", "tests/no-firebase-key.json")

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.auth import get_token_claims
from app.db import Base, SessionLocal, engine
from app.main import app
from app.models import Edition, User, Work

TEST_CLAIMS = {"uid": "test-uid", "email": "test@example.com"}


@pytest.fixture(scope="session", autouse=True)
def migrate():
    if not (engine.url.database or "").endswith("_test"):
        pytest.exit(f"DATABASE_URL must point to a *_test database, not {engine.url.database}")
    command.upgrade(Config("alembic.ini"), "head")


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()
    tables = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))


@pytest.fixture
def client(db):
    app.dependency_overrides[get_token_claims] = lambda: TEST_CLAIMS
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def user(db):
    user = User(id=TEST_CLAIMS["uid"], username="tester", email=TEST_CLAIMS["email"])
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def edition(db):
    work = Work(
        title="The Final Empire",
        author="Brandon Sanderson",
        series="Mistborn",
        series_number=1,
        openlibrary_key="/works/OL5738148W",
    )
    edition = Edition(isbn="9780765311788", openlibrary_key="/books/OL7353617M")
    work.editions.append(edition)
    db.add(work)
    db.commit()
    return edition
