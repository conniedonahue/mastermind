import pytest
from app.game_logic import generate_code, clean_and_validate_guess, evaluate_guess, check_win_lose_conditions

def test_generate_code(mock_generate_code):
    code = generate_code(4)
    assert code == mock_generate_code

def test_clean_and_validate_guess_valid():
    guess = clean_and_validate_guess("1 2 3 4", 4)
    assert guess == [1, 2, 3, 4]

def test_clean_and_validate_guess_invalid_length():
    with pytest.raises(ValueError):
        clean_and_validate_guess("12", 4)

def test_evaluate_guess():
    code = [1, 2, 3, 4]
    guess = [1, 2, 4, 5]
    correct_numbers, correct_positions = evaluate_guess(code, guess)
    assert correct_numbers == 3
    assert correct_positions == 2

def test_check_win_lose_conditions_singleplayer_wins(singleplayer_session_data):
    singleplayer_session_data['config']['code'] = [1, 2, 3, 4]
    status = check_win_lose_conditions(4, 4, singleplayer_session_data, 'player1')
    assert status == 'won'

def test_check_win_lose_conditions_singleplayer_loses(singleplayer_session_data):
    singleplayer_session_data['state']['player1']['remaining_guesses'] = 0
    status = check_win_lose_conditions(4, 3, singleplayer_session_data, 'player1')
    assert status == 'lost'

def test_check_win_lose_conditions_multiplayer_player2_wins(multiplayer_session_data):
    status = check_win_lose_conditions(4, 4, multiplayer_session_data, 'player2')
    assert status == 'player2_wins_player1_loses'
