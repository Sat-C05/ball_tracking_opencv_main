from game import BallGame, GameState


def test_gesture_start():
    game = BallGame()

    cx = game.width // 2
    cy = game.height // 2
    ball = (cx, cy, 20)

    assert game.state == GameState.READY

    game.handle_start_gesture(ball)
    assert game.state == GameState.READY

    game.hold_start -= 0.6
    game.handle_start_gesture(ball)

    assert game.state == GameState.COUNTDOWN
    print("Gesture start passed!")


def test_countdown():
    game = BallGame()
    game.begin_countdown()

    assert game.countdown_value() == 3

    game.countdown_start -= 3.1
    game.update()

    assert game.state == GameState.PLAYING
    assert game.score == 0
    assert game.active_target is not None
    assert game.time_left() > 59

    print("Countdown passed!")


def test_scoring():
    game = BallGame()
    game.start()

    x, y = game.active_target

    assert game.register_hit((x, y, 20))
    assert game.score == 1
    assert game.state == GameState.HIT_FEEDBACK

    assert not game.register_hit((x, y, 20))
    assert game.score == 1

    game.hit_time -= 0.3
    game.update()

    assert game.state == GameState.PLAYING
    assert game.score == 1

    print("Scoring passed!")


def test_game_over():
    game = BallGame()
    game.start()

    game.start_time -= 61
    game.update()

    assert game.state == GameState.FINISHED
    assert game.active_target is None

    print("Game over passed!")


def test_restart():
    game = BallGame()
    game.start()

    x, y = game.active_target
    game.register_hit((x, y, 20))

    assert game.score == 1

    game.begin_countdown()
    game.countdown_start -= 3.1
    game.update()

    assert game.state == GameState.PLAYING
    assert game.score == 0

    print("Restart passed!")


if __name__ == "__main__":
    test_gesture_start()
    test_countdown()
    test_scoring()
    test_game_over()
    test_restart()

    print("\nALL TESTS PASSED!")
