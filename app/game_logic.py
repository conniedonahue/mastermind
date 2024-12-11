import requests
import logging

logger = logging.getLogger(__name__)

def generate_code(code_length=4):
    """
    Fetches a random code using Random.org API, with fallback to Python's random module.

    Args:
        code_length (int, optional): Length of the code to generate. Defaults to 4.
        
    Returns:
        List[int]: List of random digits between 0-7, or None if request fails
        
    Raises:
        requests.exceptions.RequestException: If HTTP request to Random.org fails
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
        # API returns a string column of numbers (e.g. '3/n4/n2/n1')
        logger.debug("Sending request to Random.org with params: %s", params)
        response = requests.get(url, params=params)
        response.raise_for_status()
        code = list(map(int, response.text.split()))
        logger.info("Successfully generated code: %s", code)
        return code
    except requests.exceptions.RequestException as e:
        logger.warning("HTTP error occurred while fetching code: %s. Using fallback random generator.", e)
        code = [random.randint(0, 7) for _ in range(code_length)]
        logger.info("Generated fallback code: %s", code)
        return code


def clean_and_validate_guess(raw_guess, code_length=4):
    """
    Cleans and validates the guess input.

    Args:
        raw_guess (str): The raw guess input from user
        code_length (int, optional): Expected length of the guess. Defaults to 4.
        
    Returns:
        List[int]: Cleaned and validated list of digits
        
    Raises:
        ValueError: If input is not exactly code_length digits or contains numbers outside 0-7
    """

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
    """
    Evaluates the player's guess against the secret code.
    
    Args:
        code (List[int]): The secret code
        guess (List[int]): The player's guess
        
    Returns:
        Tuple[int, int]: A tuple containing (correct_numbers, correct_positions)
            correct_numbers: Total number of correct digits regardless of position
            correct_positions: Number of digits in correct position
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
    """
    Checks if the game has been won or lost based on the latest guess.
    
    Args:
        correct_numbers (int): Number of correct digits in the guess
        correct_positions (int): Number of digits in correct position
        session_data (dict): Current game session data
        player (str): Current player ('player1' or 'player2')
        user_service (UserService): Service for updating user statistics
        
    Returns:
        str: Game status - one of:
            - 'active': Game continues
            - 'won': Single player victory
            - 'lost': Single player loss
            - 'player1_wins_player2_loses': Multiplayer player 1 victory
            - 'player2_wins_player1_loses': Multiplayer player 2 victory
            - 'both_players_lose': Multiplayer both players lost
    """

    logger.debug("Checking win/lose conditions for player: %s with this session_data: %s", player, session_data)
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
            user_service.update_user_game_stats(session_data['config']['player_info'][other_player]['username'], False)  
        
        if player1_remaining_guesses <= 0 and player2_remaining_guesses <= 0:
            status = 'both_players_lose'
            logger.info("Both players ran out of guesses, setting status to %s", status)
            user_service.update_user_game_stats(player1_username, False)
            user_service.update_user_game_stats(player2_username, False)

    # single player:        
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