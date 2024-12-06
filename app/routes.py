from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from .game_logic import generate_code, evaluate_guess, clean_and_validate_guess
from db.cache.development import Cache
import uuid

game_routes = Blueprint('game_routes', __name__)
sessions_routes = Blueprint('sessions', __name__)

@sessions.route('/sessions', methods=['POST'])
def create_session():
    data = request.json
    session_id = str(uuid.uuid4())
    Cache.create_session(session_id, {
        "gameType": data.get("gameType"),
        "players": [{"id": data["hostPlayer"]["id"], "name": data["hostPlayer"]["name"]}],
        "status": "waiting_for_players"
    })
    return jsonify({"sessionId": session_id, "joinLink": f"https://example.com/sessions/{session_id}"})

@game_routes.route('/')
def home():
    return render_template('welcome.html')

@game_routes.route('/game/<session_id>')
def render_game_page():
    session_data = Cache.get_session(session_id)
    if not session_data:
        return "Session not found", 404
    return render_template('game.html', session_id="session")

@game_routes.route('/game', methods=['POST'])
def create_game():
    print('In router')
    # Extract data from the request
    allowed_attempts = int(request.form.get('allowed_attempts', 10))
    code_length = int(request.form.get('code_length', 4))
    wordleify = request.form.get('wordleify') is not None
    code = generate_code(code_length)


    # Initialize session
    session['code'] = code
    session['allowed_attempts'] = allowed_attempts
    session['remaining_guesses'] = allowed_attempts
    session['code_length'] = code_length
    session['wordleify'] = wordleify
    session['guesses'] = []
    session['status'] = 'active'

    return jsonify({
        'message': 'Game created successfully!',
        'game_state': {
            'game_id': '1111',
            'remaining_guesses': allowed_attempts,
            'code_length': code_length,
            'wordleify': wordleify,
            'status': session.get('status')
        }
    }), 201  

# @game_routes.route('/game.html')
# def game_page():
#     return render_template('play_game.html')

@game_routes.route('/play_game', methods=['GET'])
def play_game():
    remaining_guesses=session.get('remaining_guesses', 0)
    code_length=session.get('code_length', 4)
    wordleify=session.get('wordleify', False)

    # return render_template('game.html', remaining_guesses=remaining_guesses)

    return jsonify({
        'game_state': {
            'remaining_guesses': remaining_guesses,
            'code_length': code_length,
            'wordleify': wordleify,
            'guesses': session.get('guesses', [])
        }
    }), 200

@game_routes.route('/guess', methods=['POST'])
def guess():
    try:
        # Extract guess input and clean/validate it
        raw_guess = request.form.get('guess', '').strip()
        print("raw_guess: ", raw_guess)
        code = session.get('code', [])
        print("code")
        remaining_guesses = session.get('remaining_guesses', 0)
        print('remaining')

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

