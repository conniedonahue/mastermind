import requests

def generate_code(code_length=4):
    """Fetches a random 4-digit code ( between 0 and 7) using Random.org API."""
    url = "https://www.random.org/integers"
    params = {
        "num": 4,
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
    """Evaluates the player's guess and returns feedback."""
    correct_positions = sum(1 for c, g in zip(code, guess) if c == g)
    correct_numbers = sum(min(code.count(x), guess.count(x)) for x in set(guess)) - correct_positions
    return correct_numbers, correct_positions