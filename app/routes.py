from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from .game_logic import generate_code, evaluate_guess
game_routes = Blueprint('game_routes', __name__)

@game_routes.route('/')
def home():
    return render_template('welcome.html')

@game_routes.route('/create_game', methods=['POST'])
def create_game():
        allowed_attempts = int(request.form.get('allowed_attempts', 10))
        code_length = int(request.form.get('code_length', 4))
        wordleify = request.form.get('wordleify') is not None
        code = generate_code(code_length)

        session['code'] = code
        session['allowed_attempts'] = allowed_attempts
        session['code_length'] = code_length
        session['wordleify'] = wordleify

        return redirect(url_for('game_routes.play_game'))


@game_routes.route('/play_game', methods=['GET', 'POST'])
def play_game():
    if request.method == 'POST':
        # Collect the settings from the form
        print("post!")
        allowed_attempts = int(request.form.get('allowed_attempts', 10))
        code_length = int(request.form.get('code_length', 4))
        wordleify = request.form.get('wordleify') is not None
        
        # Store these settings in the session for use in the game
        session['allowed_attempts'] = allowed_attempts
        session['code_length'] = code_length
        session['wordleify'] = wordleify
        
        # Redirect to the game screen with the new settings
        return redirect(url_for('game_routes.game'))
    else:
        print('GET')

    # For GET request, retrieve the settings from the session
    allowed_attempts = session.get('allowed_attempts', 10)
    code_length = session.get('code_length', 4)
    wordleify = session.get('wordleify', False)
    remaining_guesses = session.get('remaining_guesses', allowed_attempts)

    return render_template('game.html', allowed_attempts=allowed_attempts, code_length=code_length, wordleify=wordleify, code=code, remaining_guesses=remaining_guesses)


@game_routes.route('/generate_code', methods=['GET'])
def generate_code_route():
    """Generates a random 4-digit code."""
    code = generate_code()
    if code is None:
        return jsonify({"error": "Failed to fetch random code from API"}), 500
    return jsonify({"code": code})

@game_routes.route('/guess', methods=['POST'])
def guess_route():
    """Handles a guess attempt."""
    data = request.get_json()

    # Validate the input
    if not data or 'guess' not in data:
        return jsonify({"error": "Missing guess in request data"}), 400

    guess = data['guess']
    if len(guess) != 4 or any(x < 0 or x > 7 for x in guess):
        return jsonify({"error": "Invalid input. Provide 4 integers between 0 and 7."}), 400

    # Game logic
    code = generate_code()  # Here, it would be better to save the code in a session or a database for persistent game state
    correct_numbers, correct_positions = evaluate_guess(code, guess)

    if correct_positions == 4:
        return jsonify({"message": "Congratulations! You guessed the code!"})
    else:
        return jsonify({
            "correct_numbers": correct_numbers,
            "correct_positions": correct_positions,
            "message": "Try again!"
        })
