import pytest
from app import create_app
from app.config import TestingConfig

@pytest.fixture
def app():
    """Create and configure a new app instance for testing."""
    app = create_app()
    app.config.from_object(TestingConfig)
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def mock_generate_code(mocker):
    mock_response = mocker.patch("requests.get")
    mock_response.return_value.status_code = 200
    mock_response.return_value.text = "1\n2\n3\n4"
    return [1, 2, 3, 4]

@pytest.fixture
def singleplayer_session_data():
    """Provide mock singleplayer session data."""
    return {
        'config': {'multiplayer': False, 'code': [1, 2, 3, 4]},
        'state': {'player1': {'remaining_guesses': 5}}
    }

@pytest.fixture
def multiplayer_session_data():
    """Provide mock multiplayer session data"""
    return {
        'config': {'multiplayer': True, 'code': [1,2,3,4]},
        'state': {
            'player1': {
                'remaining_guesses': 10,
                'guesses': []
                }, 
            'player2': {
                'remaining_guesses': 10,
                'guesses': []
                }
            }
    }
