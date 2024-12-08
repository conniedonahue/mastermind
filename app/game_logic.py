import requests
import logging

logger = logging.getLogger(__name__)

def generate_code(code_length=4):
    """
    Fetches a random 4-digit code ( between `min` and `max`) using Random.org API.
    Random.org API returns a string column of numbers (e.g. '3/n4/n2/n1')
    Returns that response as list of ints (e.g. [3, 4, 2, 1]) 
    
    """
    logger.debug("Generating a code of length %d.", code_length)
    url = "https://www.random.org/integers"
    params = {
        "num": code_length,
        "min": 0,
        "max": 7,
        "col": 1,
        "base": 10,
        "format": "plain",
        "rnd": "new"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        numbers = list(map(int, response.text.split()))
        return numbers
    except requests.exceptions.RequestException as e:
        print(f"HTTP error occurred while fetching code: {e}")
        return None

def clean_and_validate_guess(raw_guess, code_length=4):
    """Cleans and validates the guess input."""
    # Remove spaces and validate the input
    cleaned_guess = "".join(raw_guess.split())
    if not cleaned_guess.isdigit() or len(cleaned_guess) != code_length:
        raise ValueError(f"Invalid input. Please enter exactly {code_length} digits between 0 and 7.")
    
    # Convert the cleaned string to a list of integers
    guess = [int(digit) for digit in cleaned_guess]

    # Ensure all numbers are in the range 0-7
    if any(d < 0 or d > 7 for d in guess):
        raise ValueError("Invalid input. Numbers must be between 0 and 7.")

    return guess


def evaluate_guess(code, guess):
    """Evaluates the player's guess and returns feedback.
    """
    logger.info("Evaluating guess: %s against code: %s", guess, code)
    correct_numbers, correct_positions = 0, 0
    
    for num in set(guess):
        correct_numbers += min(code.count(num), guess.count(num))
    
    for c, g in zip(code, guess):
        if c == g:
            correct_positions += 1

    return correct_numbers, correct_positions

def check_win_lose_conditions(correct_numbers, correct_positions, session_data, player):
    multiplayer = session_data['config']['multiplayer']
    code = session_data['config']['code']
    player1_remaining_guesses = session_data['state']['player1']['remaining_guesses']
    status = "active"

    print(f"{player}: nums: {correct_numbers}, pos: {correct_positions}")

    if multiplayer:
        player2_remaining_guesses = session_data['state']['player2']['remaining_guesses']

        won = (correct_positions == len(code))
        print('won?: ', won)
            
        if won:
            other_player = 'player2' if player == 'player1' else 'player1'
            status = f"{player}_wins_{other_player}_loses"
        
        if player1_remaining_guesses <= 0 and player2_remaining_guesses <= 0:
            status = 'both_players_lose'


    else:
        if correct_positions == len(session_data['config']['code']):
            status = 'won'

        if session_data['state']['player1']['remaining_guesses'] <= 0:
            status = 'lost'
    
    return status