from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app, make_response
from .game_logic import generate_code, evaluate_guess, clean_and_validate_guess
from app import create_app 
import uuid

game_routes = Blueprint('game_routes', __name__)

@game_routes.route('/')
def home():
    return render_template('welcome.html')


@game_routes.route('/game', methods=['POST'])
def create_game():
    cache = current_app.cache
    print("allowed attempts: ", int(request.form.get('allowed_attempts')))
    # Extract data from the request
    allowed_attempts = int(request.form.get('allowed_attempts', 10))
    code_length = int(request.form.get('code_length', 4))
    wordleify = 'wordleify' in request.form
    code = generate_code(code_length)


    # Initialize session
    session = {
       'config': {
            'allowed_attempts': allowed_attempts,
            'code_length': code_length,
            'wordleify': wordleify,
            'code': [1234],
        },
        'state': {
            'status': "active",
            'remaining_guesses': allowed_attempts,
            'guesses': []
        }
    }
    session_id = cache.create_session(session) 

    print("session created: ", session_id)
    return jsonify({
        'message': 'Game created successfully!',
        "session_id": session_id,
        "join_link": f"https://example.com/sessions/{session_id}",
        "session_state": session['state']
    }), 201 

    # response.set_cookie("session_id", session_id, httponly=True, samesite='None')



    return response


@game_routes.route('/game/<session_id>', methods=['GET'])
def render_game_page(session_id):
    cache = current_app.cache
    print('sessionID: ', session_id)
    session_data = cache.get_session(session_id)
    print("session_data: ", session_data)
    if not session_data:
        return jsonify({"error": "Session not found"}), 404
    return render_template('game.html', session_id="session", game_state=session_data['state'])


@game_routes.route('/game/<session_id>/state', methods=['GET'])
def get_game_state(session_id):
    cache = current_app.cache
    session_data = cache.get_session(session_id)

    if not session_data:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify({
        'game_state': session_data['state']
    }), 200


@game_routes.route('/game/<session_id>', methods=['POST'])
def guess(session_id):
    cache = current_app.cache
    raw_guess = request.form['guess']
    session_data = cache.get_session(session_id)

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
        cache.update_session(session_id, session_data)

        return jsonify({
            "result" : session_data['state']
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400

