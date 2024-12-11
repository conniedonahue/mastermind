import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_session_manager(mocker):
    mock_session_manager = mocker.Mock()
    
    mock_session = {
        'config': {
            'player_info': {
                'player1': {'username' : 'username', 'user_id': 3}
            },
            'multiplayer': False, 
            'code_length': 4,
            'code': [1, 2, 3, 4],
            'allowed_attempts': 10
        },
        'state': {
            'player1': {
                'remaining_guesses': 10,
                'guesses': [],
                'status': 'in_progress'
            }
        }
    }
    
    mock_session_manager.get_session.return_value = mock_session
    mock_session_manager.create_session.return_value = "12345"
    mock_session_manager.update_session.return_value = True
    
    mocker.patch('app.routes.current_app.session_manager', mock_session_manager)
    
    return mock_session_manager

@pytest.fixture
def multiplayer_mock_session_manager(mocker, mock_session_manager):
    mock_session_manager.get_session.return_value = {
        'config': {
              'player_info': {
                'player1': {'username' : 'username', 'user_id': 3},
                'player2': {'username' : 'username2', 'user_id': 4}
            },
            'multiplayer': True, 
            'code_length': 4,
            'code': [1, 2, 3, 4],
            'allowed_attempts': 10
        },
        'state': {
            'player1': {
                'name': 'Player 1',
                'remaining_guesses': 10,
                'guesses': [],
                'status': 'in_progress'
            }
            # No player2 to simulate an open multiplayer game
        }
    }
    
    return mock_session_manager

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"game-settings-form" in response.data


def test_create_game(client):
    data = {
        'allowed_attempts': 10,
        'code_length': 4,
        'wordleify': 'wordleify',  
        'multiplayer': 'multiplayer'
    }

    response = client.post('/game', data=data)

    assert response.status_code == 201
    json_data = response.get_json()
    assert 'session_id' in json_data
    assert 'message' in json_data
    assert json_data['message'] == 'Game created successfully!'


def test_render_game_page(client, mock_session_manager):
    session_id = "12345"  

    response = client.get(f'/game/{session_id}')

    assert response.status_code == 200
    assert b"game-container" in response.data


def test_join_multiplayer_game(client, multiplayer_mock_session_manager):
    session_id = "12345"

    data = {'player2_name': 'Player 2'}
    response = client.post(f'/game/join/{session_id}', data=data, follow_redirects=True)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == 'Player 2 joined game successfully'

    response = client.post(f'/game/join/{session_id}', data=data, follow_redirects=True)
    assert response.status_code == 400
    json_data_second = response.get_json()

    assert json_data_second['error'] == 'Game is full'


def test_get_game_state(client, mock_session_manager):
    session_id = "12345"

    response = client.get(f'/game/{session_id}/state')

    assert response.status_code == 200

    json_data = response.get_json()
    assert 'game_state' in json_data
    assert 'player1' in json_data['game_state']

def test_guess(client, mock_session_manager):
    session_id = "12345"  

    data = {'guess': '1234', 'player': 'player1'}
    response = client.post(f'/game/{session_id}', data=data)

    assert response.status_code == 200
    json_data = response.get_json()
    assert 'result' in json_data