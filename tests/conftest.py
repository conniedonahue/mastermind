import pytest
from unittest.mock import MagicMock
from app import create_app
from app.config import TestingConfig

@pytest.fixture(scope="session")
def mock_db():
    """Mock database components."""
    class MockDBComponents:
        def __init__(self):
            self.engine = MagicMock()
            self.base = MagicMock()
            self.session = MagicMock()
            
        def setup_session(self):
            """Create a new session instance"""
            return self.session()
            
    return MockDBComponents()

@pytest.fixture(scope="session")
def app(mock_db):
    """Create and configure a new app instance for testing."""
    app = create_app()
    app.config.from_object(TestingConfig)
    
    # Store mock components on app for access by other fixtures
    app.mock_db = mock_db
    
    # Create the database tables using the mocked Base
    mock_db.base.metadata.create_all(mock_db.engine)

    with app.app_context():
        yield app

    # Drop the database tables using the mocked Base
    mock_db.base.metadata.drop_all(mock_db.engine)

@pytest.fixture(scope="function")
def db_session(app, mock_db):
    """Create a mocked database session."""
    mock_engine, mock_base, mock_session = mock_db
    
    # Simulate a database transaction
    connection = mock_engine.connect()
    transaction = connection.begin()
    
    # Return the mocked session
    session = mock_session()
    yield session
    
    # Rollback and close the connection after the test
    transaction.rollback()
    connection.close()
    mock_session.remove()

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
        'config': {'multiplayer': False, 'code': [1, 2, 3, 4], 'player_info' : {'player1':
            {'username': 'username', 'user_id': '3'}}},
        'state': {'player1': {'remaining_guesses': 5}}
    }

@pytest.fixture
def multiplayer_session_data():
    """Provide mock multiplayer session data"""
    return {
        'config': {
            'multiplayer': True, 'code': [1,2,3,4], 'player_info': {
                'player1': {'username' : 'username', 'user_id': 3},
                'player2': {'username' : 'username2', 'user_id': 4}
            }},
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

@pytest.fixture
def mock_user_service(mocker):
    mock_user_service = mocker.Mock()
    mock_user_service.update_user_game_stats.return_value = None  # Mock this method to return nothing
    mocker.patch('app.db.user_db.service.UserService', mock_user_service)  # Mock the entire UserService class
    return mock_user_service



@pytest.fixture(scope="function")
def patch_db(app, monkeypatch):
    """Patch database components with mocked versions at function scope."""
    monkeypatch.setattr('app.db.user_db_manager.engine', app.mock_db.engine)
    monkeypatch.setattr('app.db.user_db_manager.Base', app.mock_db.base)
    monkeypatch.setattr('app.db.user_db_manager.Session', app.mock_db.session)

@pytest.fixture(scope="function")
def db_session(app, patch_db):
    """Create a mocked database session."""
    # Simulate a database transaction
    connection = app.mock_db.engine.connect()
    transaction = connection.begin()
    
    # Create a new session instance
    session = app.mock_db.setup_session()
    
    yield session
    
    # Rollback and close the connection after the test
    transaction.rollback()
    connection.close()
    app.mock_db.session.remove()
