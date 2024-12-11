from flask import Blueprint, request, jsonify, render_template, url_for, current_app
from .game_logic import generate_code, evaluate_guess, clean_and_validate_guess, check_win_lose_conditions
from .db.session_manager import initialize_session
from .db.user_db.service import UserService
from app import create_app 
import logging

game_routes = Blueprint('game_routes', __name__)
logger = logging.getLogger(__name__) 

@game_routes.route('/')
def home():
    """Renders the Welcome Page"""

    logger.info("Serving the home page.")
    return render_template('welcome.html')


@game_routes.route('/game', methods=['POST'])
def create_game():
    """
    Creates a new game session.
    
    Returns:
        flask.Response: JSON response containing:
            - message: Success message
            - session_id: Unique session identifier
            - join_link: Link for multiplayer games
            - session_state: Initial game state
        
    Raises:
        500: If game creation fails
    """

    logger.debug("Creating game with form data: %s", request.form.to_dict())
    try: 
        session_manager = current_app.session_manager
        config = extract_game_data(request.form)

        user_service = current_app.user_service
        user_id = user_service.create_or_get_user(
            username=config['player_info']['player1']['username']
        )
        config['player_info']['player1']['user_id'] = user_id
        config['code'] = generate_code(config['code_length'])

        logger.debug("Game config:  %s", config)

        # Initialize session
        session_id, session_state = initialize_session(session_manager, config)
        logger.info("Session created successfully with session ID: %s", session_id)

        join_link = f"/game/join/{session_id}" if config['multiplayer'] else None

        return jsonify({
            'message': 'Game created successfully!',
            "session_id": session_id,
            "join_link": join_link,
            "session_state": session_state
        }), 201 

    except Exception as e:
        logger.error("Error creating game: %s", e)
        return jsonify({'error': 'Failed to create game'}), 500


@game_routes.route('/game/<session_id>', methods=['GET'])
def render_game_page(session_id):
    """
    Renders the game page for a given session.
    
    Args:
        session_id (str): Unique session identifier
        
    Returns:
        flask.Response: Rendered game template with game state
        
    Raises:
        404: If session not found
    """

    logger.info("Accessing game page for session: %s", session_id)
    session_manager = current_app.session_manager
    session_data = session_manager.get_session(session_id)
    if not session_data:
        logger.warning("Session not found: %s ", session_id)
        return jsonify({"error": "Session not found"}), 404

    is_multiplayer = session_data['config'].get('multiplayer', False)
    template = 'multiplayer_game.html' if is_multiplayer else 'game.html'

    logger.info("Rendering game page for session %s, is_multiplayer = %s", session_id, is_multiplayer)
    return render_template(template, 
                            session_id="session", 
                            game_state=session_data['state'], 
                            is_multiplayer=is_multiplayer,
                            join_link=f"/game/join/{session_id}" if is_multiplayer else None)


@game_routes.route('/game/join/<session_id>', methods=['GET'])
def render_join_page(session_id):
    """
    Renders the join page for multiplayer games.
    
    Args:
        session_id (str): Unique session identifier
        
    Returns:
        flask.Response: Rendered join_game.html template
        
    Raises:
        404: If session not found
    """

    session_manager = current_app.session_manager
    session_data = session_manager.get_session(session_id)

    if not session_data:
        logger.warning("Game not found or not multiplayer for session %s", session_id)
        return "Session not found", 404

    return render_template('join_game.html', session_id=session_id, session_data=session_data)


@game_routes.route('/game/join/<session_id>/', methods=['POST'])
def join_multiplayer_game(session_id):
    """
    Handles a player joining a multiplayer game.
    
    Args:
        session_id (str): Unique session identifier
        
    Returns:
        flask.Response: JSON response with success/error message
        
    Raises:
        404: If game not found or not multiplayer
        400: If game is already full
    """

    logger.info("Player attempting to join multiplayer game: %s", session_id)

    session_manager = current_app.session_manager
    session_data = session_manager.get_session(session_id)

    if not session_data or not session_data['config'].get('multiplayer'):
        logger.warning("Game not found or not multiplayer for session %s", session_id)
        return jsonify({"error": "Game not found or not multiplayer"}), 404

    # Add player 2 to the session
    user_service = current_app.user_service

    if "player2" not in session_data['state']:
        player2_username = request.form.get('player2_name', 'Player 2')
        logger.info("Adding %s to the session", player2_username)
        session_data['state']['player2'] = {
            'username': player2_username,
            'remaining_guesses': session_data['config']['allowed_attempts'],
            'guesses': []
        }
        player2_user_id = user_service.create_or_get_user(player2_username)
        session_data['config']['player_info']['player2'] = {'username' : player2_username,'user_id' : player2_user_id  }
        session_data['state']['status'] = 'active'
        session_manager.update_session(session_id, session_data)
        logger.info("%s joined game %s successfully", player2_username, session_id)
        return jsonify({"message": f"{player2_username} joined game successfully"}), 200
    else:
        logger.warning("Game is full for session %s", session_id)
        return jsonify({"error": "Game is full"}), 400


@game_routes.route('/game/<session_id>/state', methods=['GET'])
def get_game_state(session_id):
    """
    Retrieves current game state.
    
    Args:
        session_id (str): Unique session identifier
        
    Returns:
        flask.Response: JSON response containing game state
        
    Raises:
        404: If session not found
    """

    session_manager = current_app.session_manager
    session_data = session_manager.get_session(session_id)

    if not session_data:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify({
        'game_state': session_data['state']
    }), 200


@game_routes.route('/game/<session_id>', methods=['POST'])
def guess(session_id):
    """
    Processes a player's guess.
    
    Args:
        session_id (str): Unique session identifier
        
    Returns:
        flask.Response: JSON response containing updated game state
        
    Raises:
        400: If guess is invalid
        404: If session not found
    """

    logger.info("Player %s making a guess for session %s", request.form.get('player', 'player1'), session_id)
    session_manager = current_app.session_manager
    user_service = current_app.user_service
    raw_guess = request.form['guess']
    logger.debug("Raw guess: %s", raw_guess)

    player = request.form.get('player', 'player1')
    session_data = session_manager.get_session(session_id)
    code = session_data['config']['code']

    try:
        guess = clean_and_validate_guess(raw_guess, session_data['config']['code_length'])
        logger.info("Validated guess: %s", guess)

        
        correct_numbers, correct_positions = evaluate_guess(
            code, 
            guess
        )
        logger.debug("Correct numbers: %s, Correct positions: %s", correct_numbers, correct_positions )

        # Update session state
        if player == 'player1' or 'player2' not in session_data['state']:
            session_data['state']['player1']['remaining_guesses'] -= 1
            session_data['state']['player1']['guesses'].append({
                'guess': guess,
                'correct_numbers': correct_numbers,
                'correct_positions': correct_positions
            })
        else:
            session_data['state']['player2']['remaining_guesses'] -= 1
            session_data['state']['player2']['guesses'].append({
                'guess': guess,
                'correct_numbers': correct_numbers,
                'correct_positions': correct_positions
            })
        session_data['state']['status'] = check_win_lose_conditions(correct_numbers, correct_positions, session_data, player, user_service)

        session_manager.update_session(session_id, session_data)
        logger.info("Updated game state for session %s", session_id)
        return jsonify({
            "result" : session_data['state']
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400


def extract_game_data(form):
    """
    Helper function to extract game-related data from Reqeuest.

    Args:
        form (ImmutableMultiDict): Game config data from request.

    Returns:
        dict: Game configuration containing:
            - player_info[str]: Player username and details
            - allowed_attempts[int]: Number of allowed guesses
            - code_length[int]: Length of secret code
            - wordleify[bool]: Whether to use Wordle-style feedback
            - multiplayer[bool]: Whether game is multiplayer
    """

    return {
        'player_info': {
            'player1' : {
               'username': form.get('username')}
            },
        'allowed_attempts': int(form.get('allowed_attempts', 10)),
        'code_length': int(form.get('code_length', 4)),
        'wordleify': 'wordleify' in form,
        'multiplayer': 'multiplayer' in form,
    }