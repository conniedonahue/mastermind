import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.db.session_manager import InMemorySessionManager

def test_in_memory_session_manager_create_and_get_session(app):
    test_data = {"test": "data"}
    session_id = InMemorySessionManager.create_session(test_data)
    
    assert session_id is not None
    assert isinstance(session_id, str)
    
    retrieved_session = InMemorySessionManager.get_session(session_id)
    assert retrieved_session == test_data

def test_in_memory_session_manager_update_session(app):
    initial_data = {"initial": "data"}
    session_id = InMemorySessionManager.create_session(initial_data)
    
    update_data = {"updated": "info"}
    result = InMemorySessionManager.update_session(session_id, update_data)
    
    assert result is True
    
    retrieved_session = InMemorySessionManager.get_session(session_id)
    assert retrieved_session == {**initial_data, **update_data}

def test_in_memory_session_manager_session_expiration(app):
    # Shortening SESSION_TIMEOUT for testing
    with patch.object(InMemorySessionManager, 'SESSION_TIMEOUT', timedelta(seconds=1)):
        
        test_data = {"test": "data"}
        session_id = InMemorySessionManager.create_session(test_data)
        
        # Wait for session to expire
        time.sleep(2)
        
        retrieved_session = InMemorySessionManager.get_session(session_id)
        assert retrieved_session is None

def test_in_memory_session_manager_delete_session(app):
    test_data = {"test": "data"}
    session_id = InMemorySessionManager.create_session(test_data)
    
    result = InMemorySessionManager.delete_session(session_id)
    assert "Deleted session" in result
    
    retrieved_session = InMemorySessionManager.get_session(session_id)
    assert retrieved_session is None

def test_in_memory_session_manager_active_session_count(app):
    InMemorySessionManager._store.clear()
    
    session_ids = [
        InMemorySessionManager.create_session({"test": f"data{i}"}) 
        for i in range(3)
    ]
    
    active_count = InMemorySessionManager.get_active_session_count()
    assert active_count == 3