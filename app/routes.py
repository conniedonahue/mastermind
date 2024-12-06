from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
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
    print('In router')
    # Extract data from the request
    allowed_attempts = int(request.form.get('allowed_attempts', 10))
    code_length = int(request.form.get('code_length', 4))
    wordleify = request.form.get('wordleify') is not None
    code = generate_code(code_length)


    # Initialize session
    session_id = str(uuid.uuid4())
    session = {
       'config': {
            'session_id': session_id,
            'allowed_attempts': allowed_attempts,
            'code_length': code_length,
            'wordleify': wordleify,
            'code': [1234],
        },
        'state': {
            'status': "active",
            'remaining_guesses': allowed_attempts,
        }
    }
    cache.create_session(session_id, session) 

    print("session created: ", session_id)


    return jsonify({
        'message': 'Game created successfully!',
        "session_id": session_id,
        "join_link": f"https://example.com/sessions/{session_id}",
        "session_state": session['config']
    }), 201  


@game_routes.route('/game/<session_id>', methods=['GET'])
def render_game_page(session_id):
    cache = current_app.cache
    print('sessionID: ', session_id)
    session_data = cache.get_session(session_id)
    print("session_data: ", session_data)
    if not session_data:
        return "Session not found", 404
    return render_template('game.html', session_id="session")


@game_routes.route('/game/<session_id>', methods=['POST'])
def guess(session_id):
    print("sessionID in guess: ", session_id)
    cache = current_app.cache
    print('guessRequest: ', request.form)
    try:
        # Extract guess input and clean/validate it
        raw_guess = request.form.get('guess', '').strip()
        print("raw_guess: ", raw_guess)
        session = cache.get_session(session_id)
        print("session: ", session)
        # code = session['config']['code']
        # print('code: ', code)
        # remaining_guesses = session.get('remaining_guesses', 0)
        # print('remaining')

        # Clean input (e.g., remove spaces, split digits)
        guess = clean_and_validate_guess(raw_guess, session["code_length"])
        print("cleaned guess: ", guess)

        # Evaluate the guess
        correct_numbers, correct_positions = evaluate_guess(code, guess)

        # Update game state
        session['remaining_guesses'] -= 1
        session['guesses'].append({
            'guess': guess,
            'correct_numbers': correct_numbers,
            'correct_positions': correct_positions
        })

        print("updated!")

        # Check win/loss conditions
        if correct_positions == len(code):
            session['status'] = 'won'

        if session['remaining_guesses'] <= 0:
            session['status'] = 'lost'

        print("about to redirect!")
        # Continue game
        return jsonify({
            'game_state': {
                'remaining_guesses': session['remaining_guesses'],
                'guesses': session['guesses'],
                'status': session['status']
            }
        }), 200

    except ValueError as e:
        # flash(str(e))
        return jsonify({
            'error': str(e)
        }), 400

