def test_game_session_creation(db_session):
    from app.db.models import GameSession
    game = GameSession(allowed_attempts=10, code_length=4, multiplayer=False, code="1234")
    db_session.add(game)
    db_session.commit()
    assert game.id is not None
