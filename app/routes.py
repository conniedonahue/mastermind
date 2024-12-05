from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from .game_logic import generate_code, evaluate_guess, clean_and_validate_guess
game_routes = Blueprint('game_routes', __name__)

@game_routes.route('/')
def home():
    return render_template('welcome.html')

@game_routes.route('/create_game', methods=['POST'])
def create_game():
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

    return redirect(url_for('game_routes.play_game'))

@game_routes.route('/play_game', methods=['GET'])
def play_game():
    return render_template('game.html', 
    remaining_guesses=session.get('remaining_guesses', 0), 
    code_length=session.get('code_length', 4), 
    wordleify=session.get('wordleify', False))

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
            flash("Congratulations! You've guessed the code!")
            return redirect(url_for('game_routes.create_game'))

        if session['remaining_guesses'] <= 0:
            flash(f"Game over! The correct code was {''.join(map(str, code))}.")
            return redirect(url_for('game_routes.create_game'))

        print("about to redirect!")
        # Continue game
        return redirect(url_for('game_routes.create_game'))

    except ValueError as e:
        flash(str(e))
        return redirect(url_for('game_routes.create_game'))

