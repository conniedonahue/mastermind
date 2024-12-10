from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app, make_response
from .game_logic import generate_code, evaluate_guess, clean_and_validate_guess, check_win_lose_conditions
from .db.session_manager import initialize_session
from .db.user_db.models import User
from .db.user_db.service import UserService
from sqlalchemy import select
from app import create_app 
import asyncio
import logging
import uuid

game_routes = Blueprint('game_routes', __name__)
logger = logging.getLogger(__name__) 

@game_routes.route('/')
def home():
    logger.info("Serving the home page.")
    return render_template('welcome.html')


@game_routes.route('/game', methods=['POST'])
def create_game():
    logger.debug("Creating game with form data: %s", request.form.to_dict())
    try: 
        session_manager = current_app.session_manager
        config = extract_game_data(request.form)

        user_service = UserService(current_app.db_manager)
        user_id = user_service.create_or_get_user(
            username=config['player_info']['player1']['username']
        )
        config['player_info']['player1']['user_id'] = user_id
        config['code'] = [0,0,0,0]


        # Extract data from the request
        # allowed_attempts = int(request.form.get('allowed_attempts', 10))
        # code_length = int(request.form.get('code_length', 4))
        # wordleify = 'wordleify' in request.form
        # multiplayer = 'multiplayer' in request.form

        # code = generate_code(code_length)

        # config = {
        #     'allowed_attempts': allowed_attempts,
        #     'code_length': code_length,
        #     'wordleify': wordleify,
        #     'multiplayer': multiplayer,
        #     'code': [0, 0 , 0 ,0],
        #     'user_id': user_id
        # }

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
    session_manager = current_app.session_manager
    session_data = session_manager.get_session(session_id)

    if not session_data:
        logger.warning("Game not found or not multiplayer for session %s", session_id)
        return "Session not found", 404

    return render_template('join_game.html', session_id=session_id, session_data=session_data)

@game_routes.route('/game/join/<session_id>/', methods=['POST'])
def join_multiplayer_game(session_id):
    logger.info("Player attempting to join multiplayer game: %s", session_id)

    session_manager = current_app.session_manager
    session_data = session_manager.get_session(session_id)

    if not session_data or not session_data['config'].get('multiplayer'):
        logger.warning("Game not found or not multiplayer for session %s", session_id)
        return jsonify({"error": "Game not found or not multiplayer"}), 404

    # Add player 2 to the session
    if "player2" not in session_data['state']:
        player2_name = request.form.get('player2_name', 'Player 2')
        logger.info("Adding %s to the game", player2_name)
        session_data['state']['player2'] = {
            'name': player2_name,
            'remaining_guesses': session_data['config']['allowed_attempts'],
            'guesses': []
        }
        session_data['state']['status'] = 'active'
        session_manager.update_session(session_id, session_data)
        logger.info("%s joined game %s successfully", player2_name, session_id )
        return jsonify({"message": f"{player2_name} joined game successfully"}), 200
    else:
        logger.warning("Game is full for session %s", session_id)
        return jsonify({"error": "Game is full"}), 400

@game_routes.route('/game/<session_id>/state', methods=['GET'])
def get_game_state(session_id):
    session_manager = current_app.session_manager
    session_data = session_manager.get_session(session_id)

    if not session_data:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify({
        'game_state': session_data['state']
    }), 200


@game_routes.route('/game/<session_id>', methods=['POST'])
def guess(session_id):
    logger.info("Player %s making a guess for session %s", request.form.get('player', 'player1'), session_id)
    session_manager = current_app.session_manager
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
        session_data['state']['status'] = check_win_lose_conditions(correct_numbers, correct_positions, session_data, player)

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
        dict: game-related data.
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