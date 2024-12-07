from .interface import SessionManagerInterface as SessionManager

def initialize_session(session_manager: SessionManager, session_config: dict) -> str:
    """
    Initialize a new session and return its session ID.

    Args:
        session_manager (SessionManager): The session manager instance to use.
        session_data (dict): Data to store in the session.

    Returns:
        str: The generated session ID.
    """

    required_keys = ['allowed_attempts', 'code_length', 'wordleify', 'code']
    missing_keys = [key for key in required_keys if session_config.get(key) is None]

    if missing_keys:
        raise ValueError(f"Error adopting config, missing {', '.join(missing_keys)}")
    
    session_state = {
        'status': "active",
        'remaining_guesses': session_config['allowed_attempts'],
        'guesses': []
    }

    session_data = {"config" : session_config, "state" : session_state}

    print('session_data in logic: ', session_data)

    session_id = session_manager.create_session(session_data)
    return session_id, session_state

