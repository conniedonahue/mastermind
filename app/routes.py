from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app, make_response
from .game_logic import generate_code, evaluate_guess, clean_and_validate_guess
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
    print("allowed attempts: ", int(request.form.get('allowed_attempts')))
    # Extract data from the request
    allowed_attempts = int(request.form.get('allowed_attempts', 10))
    code_length = int(request.form.get('code_length', 4))
    wordleify = 'wordleify' in request.form
    config = {
        'allowed_attempts': allowed_attempts,
        'code_length': code_length,
        'wordleify': wordleify,
    }

    code = generate_code(code_length)


    # Initialize session
    session_id = initialize_session(session_manager, config)
    # session = {
    #    'config': {
    #         'allowed_attempts': allowed_attempts,
    #         'code_length': code_length,
    #         'wordleify': wordleify,
    #         'code': [1234],
    #     },
    #     'state': {
    #         'status': "active",
    #         'remaining_guesses': allowed_attempts,
    #         'guesses': []
    #     }
    # }
    # session_id = session_manager.create_session(session) 

    print("session created: ", session_id)
    return jsonify({
        'message': 'Game created successfully!',
        "session_id": session_id,
        "join_link": f"https://example.com/sessions/{session_id}",
        "session_state": session['state']
    }), 201 

@game_routes.route('/game/<session_id>', methods=['GET'])
def render_game_page(session_id):
    session_manager = current_app.session_manager
    print('sessionID: ', session_id)
    session_data = session_manager.get_session(session_id)
    print("session_data: ", session_data)
    if not session_data:
        return jsonify({"error": "Session not found"}), 404
    return render_template('game.html', session_id="session", game_state=session_data['state'])


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
    session_data = session_manager.get_session(session_id)

    try:
        guess = clean_and_validate_guess(raw_guess, session_data['config']['code_length'])
        
        print('cleaned guess: ', guess)
        # Existing game logic for evaluating guess
        correct_numbers, correct_positions = evaluate_guess(
            session_data['config']['code'], 
            guess
        )

        # Update session state
        session_data['state']['remaining_guesses'] -= 1
        session_data['state']['guesses'].append({
            'guess': guess,
            'correct_numbers': correct_numbers,
            'correct_positions': correct_positions
        })

        # Check win/loss conditions
        if correct_positions == len(session_data['config']['code']):
            session_data['state']['status'] = 'won'

        if session_data['state']['remaining_guesses'] <= 0:
            session_data['state']['status'] = 'lost'

        # Update session
        session_manager.update_session(session_id, session_data)

        return jsonify({
            "result" : session_data['state']
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400

