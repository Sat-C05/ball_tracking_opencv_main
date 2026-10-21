import cv2
import time
from collections import deque

from config import SMOOTHING_ALPHA, MAX_MISSING_FRAMES
from detector import detect_ball
from game import BallGame, GameState


def draw_centered_text(frame, text, y, scale, color, thickness=2):
    font = cv2.FONT_HERSHEY_SIMPLEX

    (text_w, _), _ = cv2.getTextSize(
        text, font, scale, thickness
    )

    x = (frame.shape[1] - text_w) // 2

    cv2.putText(
        frame, text, (x, y),
        font, scale, color, thickness,
        cv2.LINE_AA
    )


def draw_overlay(frame, opacity=0.65):
    overlay = frame.copy()
    overlay[:] = (20, 20, 30)

    cv2.addWeighted(
        overlay, opacity,
        frame, 1 - opacity,
        0, frame
    )


def draw_start_button(frame, game):
    left, top, right, bottom = game.start_zone()

    progress = game.hold_progress()
    active = progress > 0

    color = (0, 200, 0) if active else (0, 160, 255)

    cv2.rectangle(
        frame,
        (left, top),
        (right, bottom),
        color,
        3
    )

    draw_centered_text(
        frame,
        "START",
        (top + bottom) // 2 + 12,
        1.1,
        (255, 255, 255),
        3
    )

    if active:
        bar_y = bottom + 12
        bar_width = right - left

        cv2.rectangle(
            frame,
            (left, bar_y),
            (right, bar_y + 8),
            (70, 70, 70),
            -1
        )

        cv2.rectangle(
            frame,
            (left, bar_y),
            (left + int(bar_width * progress), bar_y + 8),
            (0, 255, 0),
            -1
        )


def draw_game_screen(frame, game, fps, trail):
    height, width = frame.shape[:2]

    # Draw movement trail
    for i in range(1, len(trail)):
        cv2.line(
            frame,
            trail[i - 1],
            trail[i],
            (255, 200, 0),
            2
        )

    # Draw target
    if game.active_target is not None:
        tx, ty = game.active_target

        half_w = game.target_width // 2
        half_h = game.target_height // 2

        color = (
            (0, 255, 0)
            if game.state == GameState.HIT_FEEDBACK
            else (255, 0, 255)
        )

        cv2.rectangle(
            frame,
            (tx - half_w, ty - half_h),
            (tx + half_w, ty + half_h),
            color,
            3
        )

        if game.state == GameState.HIT_FEEDBACK:
            cv2.putText(
                frame,
                "+1",
                (tx - 20, max(30, ty - half_h - 12)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )

    # Small translucent HUD panels
    overlay = frame.copy()

    # Score panel - top left
    cv2.rectangle(
        overlay, (8, 8), (135, 44),
        (25, 25, 25), -1
    )

    # Timer panel - top right
    cv2.rectangle(
        overlay, (width - 145, 8), (width - 8, 44),
        (25, 25, 25), -1
    )

    cv2.addWeighted(
        overlay, 0.55,
        frame, 0.45,
        0, frame
    )

    cv2.putText(
        frame,
        f"SCORE {game.score}",
        (17, 33),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    remaining = game.time_left()

    timer_color = (
        (0, 80, 255)
        if remaining <= 10
        else (255, 255, 255)
    )

    cv2.putText(
        frame,
        f"{remaining:.0f}s",
        (width - 115, 33),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        timer_color,
        2,
        cv2.LINE_AA
    )

    # Tiny FPS indicator in bottom-left
    cv2.putText(
        frame,
        f"{fps:.0f} FPS",
        (10, height - 12),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (200, 200, 200),
        1,
        cv2.LINE_AA
    )



def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        cap.release()
        raise RuntimeError("Could not open webcam")

    smooth_center = None
    smooth_radius = None
    missing_frames = 0

    trail = deque(maxlen=25)

    previous_frame_time = time.monotonic()
    fps = 0.0

    game = BallGame()
    debug = False
    previous_state = game.state

    try:
        while True:
            success, frame = cap.read()

            if not success:
                print("Unable to read webcam frame.")
                game.state = GameState.ABORTED
                break

            now = time.monotonic()
            delta = now - previous_frame_time
            previous_frame_time = now

            if delta > 0:
                instant_fps = 1.0 / delta
                fps = 0.8 * fps + 0.2 * instant_fps

            frame = cv2.flip(frame, 1)
            height, width = frame.shape[:2]

            game.width = width
            game.height = height

            game.update()

            # Clear old trail when a new round begins
            if (
                previous_state == GameState.COUNTDOWN
                and game.state == GameState.PLAYING
            ):
                trail.clear()
                smooth_center = None
                smooth_radius = None
                missing_frames = 0

            previous_state = game.state

            detection, mask = detect_ball(frame)
            ball = None

            if detection is not None:
                missing_frames = 0

                area, x, y, radius, circularity, contour = detection

                if smooth_center is None:
                    smooth_center = (x, y)
                    smooth_radius = radius
                else:
                    old_x, old_y = smooth_center
                    alpha = SMOOTHING_ALPHA

                    smooth_center = (
                        alpha * x + (1 - alpha) * old_x,
                        alpha * y + (1 - alpha) * old_y
                    )

                    smooth_radius = (
                        alpha * radius
                        + (1 - alpha) * smooth_radius
                    )

                sx, sy = map(int, smooth_center)
                sr = int(smooth_radius)

                ball = (sx, sy, sr)

                if game.state in (
                    GameState.PLAYING,
                    GameState.HIT_FEEDBACK
                ):
                    trail.append((sx, sy))

                # Ball visualization
                cv2.drawContours(
                    frame, [contour], -1,
                    (0, 255, 255), 2
                )

                cv2.circle(
                    frame, (sx, sy), sr,
                    (0, 255, 0), 2
                )

                cv2.circle(
                    frame, (sx, sy), 4,
                    (0, 0, 255), -1
                )

                if game.state == GameState.PLAYING:
                    game.register_hit(ball)

            else:
                missing_frames += 1

                if missing_frames > MAX_MISSING_FRAMES:
                    smooth_center = None
                    smooth_radius = None
                    trail.clear()

            # Gesture start
            game.handle_start_gesture(ball)

            # Render by game state
            if game.state in (
                GameState.READY,
                GameState.FINISHED
            ):
                draw_overlay(frame)

                if game.state == GameState.READY:
                    draw_centered_text(
                        frame,
                        "HIT THE TARGET",
                        height // 4,
                        1.2,
                        (255, 255, 255),
                        3
                    )

                    draw_centered_text(
                        frame,
                        "Move ball into START",
                        height // 4 + 40,
                        0.65,
                        (220, 220, 220)
                    )

                else:
                    draw_centered_text(
                        frame,
                        "TIME UP!",
                        height // 4,
                        1.5,
                        (0, 100, 255),
                        3
                    )

                    draw_centered_text(
                        frame,
                        f"FINAL SCORE: {game.score}",
                        height // 4 + 45,
                        0.9,
                        (255, 255, 255),
                        2
                    )

                draw_start_button(frame, game)

            elif game.state == GameState.COUNTDOWN:
                draw_overlay(frame, 0.5)

                count = game.countdown_value()

                draw_centered_text(
                    frame,
                    str(count),
                    height // 2,
                    3.5,
                    (0, 255, 255),
                    6
                )

                draw_centered_text(
                    frame,
                    "GET READY!",
                    height // 2 + 65,
                    0.8,
                    (255, 255, 255),
                    2
                )

            else:
                draw_game_screen(frame, game, fps, trail)

            cv2.imshow("Hit the Target", frame)

            if debug:
                cv2.imshow("HSV Mask", mask)
            else:
                try:
                    cv2.destroyWindow("HSV Mask")
                except cv2.error:
                    pass

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            elif key == ord("r"):
                game.begin_countdown()
                trail.clear()
                smooth_center = None
                smooth_radius = None
                missing_frames = 0

            elif key == ord("d"):
                debug = not debug

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
