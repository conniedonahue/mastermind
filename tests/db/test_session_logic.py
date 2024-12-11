import pytest
from app.db.session_manager import initialize_session
from unittest.mock import Mock

def test_initialize_session_singleplayer(mocker):
    mock_session_manager = Mock()
    mock_session_manager.create_session.return_value = "test_session_id"

    session_config = {
         'player_info': {
                'player1': {'username' : 'username', 'user_id': 3}
            },
        'allowed_attempts': 10,
        'code_length': 4,
        'wordleify': False,
        'multiplayer': False,
        'code': [1, 2, 3, 4]
    }

    session_id, session_state = initialize_session(mock_session_manager, session_config)

    assert session_id == "test_session_id"
    assert 'player1' in session_state
    assert 'player2' not in session_state
    assert session_state['player1']['remaining_guesses'] == 10
    assert session_state['player1']['guesses'] == []
    assert session_state['status'] == 'active'

def test_initialize_session_multiplayer(mocker):
    mock_session_manager = Mock()
    mock_session_manager.create_session.return_value = "test_multiplayer_session_id"

    session_config = {
        'player_info': {
                'player1': {'username' : 'username', 'user_id': 3},
                'player2': {'username' : 'username2', 'user_id': 4}
            },
        'allowed_attempts': 10,
        'code_length': 4,
        'wordleify': False,
        'multiplayer': True,
        'code': [1, 2, 3, 4]
    }

    session_id, session_state = initialize_session(mock_session_manager, session_config)

    assert session_id == "test_multiplayer_session_id"
    assert 'player1' in session_state
    assert session_state['player1']['remaining_guesses'] == 10
    assert session_state['player1']['guesses'] == []
    assert session_state['status'] == 'active_waiting'

def test_initialize_session_missing_config_keys():
    mock_session_manager = Mock()

    session_config = {
        'allowed_attempts': 10,
        'code_length': 4,
        # Missing some required keys
    }

    with pytest.raises(ValueError, match="Error adopting config, missing"):
        initialize_session(mock_session_manager, session_config)

def test_initialize_session_none_config_values():
    mock_session_manager = Mock()

    session_config = {
        'allowed_attempts': None,
        'code_length': 4,
        'wordleify': False,
        'multiplayer': False,
        'code': None
    }

    with pytest.raises(ValueError, match="Error adopting config, missing"):
        initialize_session(mock_session_manager, session_config)