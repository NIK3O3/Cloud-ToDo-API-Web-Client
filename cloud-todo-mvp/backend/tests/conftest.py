import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["ENV"] = "test"
os.environ["API_KEY"] = "test-api-key"
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from app.api.deps import get_task_service  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.main import create_app  # noqa: E402
from app.models.task import TaskModel  # noqa: E402,F401
from app.repositories.task_repository import TaskRepository  # noqa: E402
from app.services.task_service import TaskService  # noqa: E402


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    with TestingSessionLocal() as session:
        yield session
    Base.metadata.drop_all(engine)


@pytest.fixture()
def task_service(db_session: Session) -> TaskService:
    return TaskService(TaskRepository(db_session))


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_task_service() -> TaskService:
        return TaskService(TaskRepository(db_session))

    app.dependency_overrides[get_task_service] = override_task_service
    with TestClient(app) as test_client:
        yield test_client
