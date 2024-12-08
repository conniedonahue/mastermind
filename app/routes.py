from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app, make_response
from .game_logic import generate_code, evaluate_guess, clean_and_validate_guess, check_win_lose_conditions
from .db.session_manager import initialize_session
from app import create_app 
import uuid

game_routes = Blueprint('game_routes', __name__)

@game_routes.route('/')
def home():
    return render_template('welcome.html')


@game_routes.route('/game', methods=['POST'])
def create_game():
    session_manager = current_app.session_manager
    # Extract data from the request
    allowed_attempts = int(request.form.get('allowed_attempts', 10))
    code_length = int(request.form.get('code_length', 4))
    wordleify = 'wordleify' in request.form
    multiplayer = 'multiplayer' in request.form

    code = generate_code(code_length)

    config = {
        'allowed_attempts': allowed_attempts,
        'code_length': code_length,
        'wordleify': wordleify,
        'multiplayer': multiplayer,
        'code': [0,0,0,0]
    }

    print("config: ", config)

    # Initialize session
    session_id, session_state = initialize_session(session_manager, config)

    join_link = f"/game/join/{session_id}" if multiplayer else None

    return jsonify({
        'message': 'Game created successfully!',
        "session_id": session_id,
        "join_link": join_link,
        "session_state": session_state
    }), 201 

@game_routes.route('/game/<session_id>', methods=['GET'])
def render_game_page(session_id):
    session_manager = current_app.session_manager
    print('sessionID: ', session_id)
    session_data = session_manager.get_session(session_id)
    print("session_data: ", session_data)
    if not session_data:
        return jsonify({"error": "Session not found"}), 404

    is_multiplayer = session_data['config'].get('multiplayer', False)

    return render_template('game.html', session_id="session", 
                            game_state=session_data['state'], 
                            is_multiplayer=is_multiplayer)

@game_routes.route('/multiplayer-game/<session_id>', methods=['GET'])
def render_multiplayer_game_page(session_id):
    session_manager = current_app.session_manager
    session_data = session_manager.get_session(session_id)
    if not session_data:
        return jsonify({"error": "Session not found"}), 404

    is_multiplayer = session_data['config'].get('multiplayer', False)

    return render_template('multiplayer_game.html', 
                            session_id="session", 
                            game_state=session_data['state'], 
                            is_multiplayer=is_multiplayer   ,
                            join_link=f"/game/join/{session_id}" if is_multiplayer else None)

@game_routes.route('/multiplayer-game/join/<session_id>', methods=['GET'])
def render_join_page(session_id):
    session_manager = current_app.session_manager
    session_data = session_manager.get_session(session_id)

    if not session_data:
        return "Session not found", 404

    return render_template('join_game.html', session_id=session_id, session_data=session_data)

@game_routes.route('/multiplayer-game/join/<session_id>/', methods=['POST'])
def join_multiplayer_game(session_id):
    session_manager = current_app.session_manager
    session_data = session_manager.get_session(session_id)

    if not session_data or not session_data['config'].get('multiplayer'):
        return jsonify({"error": "Game not found or not multiplayer"}), 404

    # Add player 2 to the session
    if 'player2' not in session_data['state']:
        player2_name = request.form.get('player2_name', 'Player 2')
        session_data['state']['player2'] = {
            'name': player2_name,
            'remaining_guesses': session_data['config']['allowed_attempts'],
            'guesses': []
        }
        session_manager.update_session(session_id, session_data)
        return jsonify({"message": f"{player2_name} joined game successfully"}), 200
    else:
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
    session_manager = current_app.session_manager
    raw_guess = request.form['guess']
    print('player', request.form.get('player',))  # Default to player1

    player = request.form.get('player', 'player1')
    session_data = session_manager.get_session(session_id)
    code = session_data['config']['code']

    try:
        guess = clean_and_validate_guess(raw_guess, session_data['config']['code_length'])
        
        correct_numbers, correct_positions = evaluate_guess(
            code, 
            guess
        )

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

        # # Check win/loss conditions
        # if session_data['config'].get('multiplayer', False):
        #     player1_won = (correct_positions == len(session_data['config']['code']))
            
        #     # Check if game is in multiplayer mode and requires both players to guess
        #     if player1_won:
        #         session_data['state']['status'] = 'player1_wins'
                
        #         # If player2 exists, they must also guess correctly to win
        #         if 'player2' in session_data['state']:
        #             # If player2 hasn't finished, they lose
        #             if session_data['state']['player2']['remaining_guesses'] <= session_data['state']['player1']['remaining_guesses']:
        #                 session_data['state']['status'] = 'player1_wins_player2_loses'
        # else:
        #     if correct_positions == len(session_data['config']['code']):
        #         session_data['state']['status'] = 'won'

        #     if session_data['state']['player1']['remaining_guesses'] <= 0:
        #         session_data['state']['status'] = 'lost'

        # Update session
        session_manager.update_session(session_id, session_data)

        return jsonify({
            "result" : session_data['state']
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400

