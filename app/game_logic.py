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

def evaluate_guess(code, guess):
    """Evaluates the player's guess and returns feedback."""
    correct_positions = sum(1 for c, g in zip(code, guess) if c == g)
    correct_numbers = sum(min(code.count(x), guess.count(x)) for x in set(guess)) - correct_positions
    return correct_numbers, correct_positions