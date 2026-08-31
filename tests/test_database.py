"""Tests for core.database CRUD operations, using a temporary SQLite file."""
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture()
def temp_db(monkeypatch):
    """Point the app at a fresh temp SQLite DB for each test."""
    tmp_dir = tempfile.mkdtemp()
    tmp_db_path = Path(tmp_dir) / "test.db"

    from config.settings import settings
    monkeypatch.setattr(settings, "DATABASE_PATH", tmp_db_path)
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite:///{tmp_db_path}")

    import importlib
    from core import database as db_module
    importlib.reload(db_module)
    db_module.init_db()
    yield db_module


def test_create_and_get_investigation(temp_db):
    inv_id = temp_db.create_investigation("Test Subject", depth="quick")
    inv = temp_db.get_investigation(inv_id)
    assert inv is not None
    assert inv["subject"] == "Test Subject"
    assert inv["depth"] == "quick"
    assert inv["status"] == "created"


def test_list_investigations(temp_db):
    temp_db.create_investigation("Subject A")
    temp_db.create_investigation("Subject B")
    results = temp_db.list_investigations()
    assert len(results) == 2


def test_rename_investigation(temp_db):
    inv_id = temp_db.create_investigation("Old Name")
    temp_db.rename_investigation(inv_id, "New Name")
    inv = temp_db.get_investigation(inv_id)
    assert inv["name"] == "New Name"


def test_update_status(temp_db):
    inv_id = temp_db.create_investigation("Subject")
    temp_db.update_investigation_status(inv_id, "completed")
    inv = temp_db.get_investigation(inv_id)
    assert inv["status"] == "completed"


def test_delete_investigation(temp_db):
    inv_id = temp_db.create_investigation("To Delete")
    temp_db.delete_investigation(inv_id)
    assert temp_db.get_investigation(inv_id) is None


def test_get_investigation_not_found(temp_db):
    assert temp_db.get_investigation(99999) is None
