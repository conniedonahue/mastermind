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
        logger.debug("Sending request to Random.org with params: %s", params)
        response = requests.get(url, params=params)
        response.raise_for_status()
        code = list(map(int, response.text.split()))
        logger.info("Successfully generated code: %s", code)
        return code
    except requests.exceptions.RequestException as e:
        logger.error("HTTP error occurred while fetching code: %s", e)
        return None

def clean_and_validate_guess(raw_guess, code_length=4):
    """Cleans and validates the guess input."""
    # Remove spaces and validate the input
    cleaned_guess = "".join(raw_guess.split())
    logger.debug("Cleaning and validating raw guess: %s", raw_guess)
    if not cleaned_guess.isdigit() or len(cleaned_guess) != code_length:
        logger.warning("Invalid guess length or non-digit characters found: %s", raw_guess)
        raise ValueError(f"Invalid input. Please enter exactly {code_length} digits between 0 and 7.")
    
    # Convert the cleaned string to a list of integers
    guess = [int(digit) for digit in cleaned_guess]

    # Ensure all numbers are in the range 0-7
    if any(d < 0 or d > 7 for d in guess):
        logger.warning("Guess contains invalid digits: %s", guess)
        raise ValueError("Invalid input. Numbers must be between 0 and 7.")

    logger.info("Validated guess: %s", guess)
    return guess


def evaluate_guess(code, guess):
    """Evaluates the player's guess and returns feedback.
    """
    logger.debug("Evaluating guess: %s against code: %s", guess, code)
    correct_numbers, correct_positions = 0, 0
    
    for num in set(guess):
        correct_numbers += min(code.count(num), guess.count(num))
    
    for c, g in zip(code, guess):
        if c == g:
            correct_positions += 1
        
    logger.info("Evaluation result: correct_numbers = %d, correct_positions = %d", correct_numbers, correct_positions)
    return correct_numbers, correct_positions

def check_win_lose_conditions(correct_numbers, correct_positions, session_data, player, user_service):
    logger.debug("Checking win/lose conditions for player: %s", player)
    multiplayer = session_data['config']['multiplayer']
    code = session_data['config']['code']
    player1_remaining_guesses = session_data['state']['player1']['remaining_guesses']
    status = "active"

    logger.debug("Player %s guessed: nums: %d, pos: %d", player, correct_numbers, correct_positions)

    if multiplayer:
        player2_remaining_guesses = session_data['state']['player2']['remaining_guesses']
        player1_username = session_data['config']['player_info']['player1']['username']
        player2_username = session_data['config']['player_info']['player2']['username']

        won = (correct_positions == len(code))
        logger.debug("Multiplayer mode: player %s won: %s", player, won)
            
        if won:
            other_player = 'player2' if player == 'player1' else 'player1'
            status = f"{player}_wins_{other_player}_loses"
            logger.info("Player %s wins, status set to %s", player, status)
            user_service.update_user_game_stats(session_data['config']['player_info'][player]['username'], True)
            user_service.update_user_game_stats(session_data['config']['player_info'][other_player]['username'], True)

            
        
        if player1_remaining_guesses <= 0 and player2_remaining_guesses <= 0:
            status = 'both_players_lose'
            logger.info("Both players ran out of guesses, setting status to %s", status)
            user_service.update_user_game_stats(player1_username, False)
            user_service.update_user_game_stats(player2_username, False)



    else:
        username = session_data['config']['player_info']['player1']['username']
        if correct_positions == len(session_data['config']['code']):
            status = 'won'
            logger.info("Singleplayer mode: player %s wins", player)
            user_service.update_user_game_stats(username, True)

        if session_data['state']['player1']['remaining_guesses'] <= 0:
            status = 'lost'
            logger.info("Singleplayer mode: player %s loses", player)
            user_service.update_user_game_stats(username, False)
    
    return status