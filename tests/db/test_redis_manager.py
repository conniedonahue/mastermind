import pytest
import time
import json
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from redis import Redis
from app.db.session_manager import InMemorySessionManager, RedisSessionManager

@pytest.fixture
def mock_redis_session_manager():
    mock_redis = Mock(spec=Redis)
    
    session_manager = RedisSessionManager(mock_redis)
    
    return session_manager, mock_redis

def test_redis_session_manager_create_and_get_session(mock_redis_session_manager):
    session_manager, mock_redis = mock_redis_session_manager
    
    test_data = {"test": "data"}
    
    mock_redis.setex = Mock()
    mock_redis.get = Mock(return_value=json.dumps(test_data))
    
    
    session_id = session_manager.create_session(test_data)
    assert session_id is not None
    mock_redis.setex.assert_called_once()
    
    
    retrieved_session = session_manager.get_session(session_id)
    assert retrieved_session == test_data
    mock_redis.get.assert_called_once_with(session_id)

def test_redis_session_manager_update_session(mock_redis_session_manager):
    session_manager, mock_redis = mock_redis_session_manager

    initial_data = {"initial": "data"}
    mock_redis.get = Mock(return_value=json.dumps(initial_data))
    mock_redis.setex = Mock()
    
    session_id = str(uuid.uuid4())
    
    update_data = {"updated": "info"}
    result = session_manager.update_session(session_id, update_data)
    assert result is True
    mock_redis.setex.assert_called_once()
    
    call_args = mock_redis.setex.call_args[0]
    assert call_args[0] == session_id
    merged_data = json.loads(call_args[2])
    assert merged_data == {**initial_data, **update_data}

def test_redis_session_manager_delete_session(mock_redis_session_manager):
    session_manager, mock_redis = mock_redis_session_manager
    
    session_id = str(uuid.uuid4())
    session_manager.delete_session(session_id)
    
    mock_redis.delete.assert_called_once_with(session_id)

def test_redis_session_manager_nonexistent_session(mock_redis_session_manager):
    session_manager, mock_redis = mock_redis_session_manager

    mock_redis.get = Mock(return_value=None)
    
    session_id = str(uuid.uuid4())
    retrieved_session = session_manager.get_session(session_id)
    assert retrieved_session is None

    result = session_manager.update_session(session_id, {"test": "data"})
    assert result is False