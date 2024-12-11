from .interface import SessionManagerInterface as SessionManager

def initialize_session(session_manager: SessionManager, session_config: dict) -> str:
    """
    Initialize a new session.

    Args:
        session_manager (SessionManager): The session manager instance
        session_config (dict): Session configuration containing:
            - allowed_attempts: Number of allowed guesses
            - code_length: Length of secret code
            - wordleify: Whether to use Wordle-style feedback
            - multiplayer: Whether game is multiplayer
            - code: The secret code to guess
        
    Returns:
        Tuple[str, dict]: A tuple containing:
            - session_id: Unique session identifier
            - session_state: Initial game state
        
    Raises:
        ValueError: If required configuration keys are missing
    """
    
    required_keys = ['allowed_attempts', 'code_length', 'wordleify', 'multiplayer', 'code']
    missing_keys = [key for key in required_keys if session_config.get(key) is None]

    if missing_keys:
        raise ValueError(f"Error adopting config, missing {', '.join(missing_keys)}")
    
    if not session_config['multiplayer']:
        session_state = {
            'status': 'active',
             'player1' : {
                'username': session_config['player_info']['player1']['username'],
                'remaining_guesses': session_config['allowed_attempts'],
                'guesses': []
            },
        }
    else:
        session_state = {
            'status': 'active_waiting',
            'player1' : {
                'username': session_config['player_info']['player1']['username'],
                'remaining_guesses': session_config['allowed_attempts'],
                'guesses': []
            }
        }

    session_data = {"config" : session_config, "state" : session_state}


    session_id = session_manager.create_session(session_data)
    return session_id, session_state

