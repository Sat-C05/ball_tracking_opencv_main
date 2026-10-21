import time
import random
import math
from enum import Enum, auto


class GameState(Enum):
    READY = auto()
    COUNTDOWN = auto()
    PLAYING = auto()
    HIT_FEEDBACK = auto()
    FINISHED = auto()
    ABORTED = auto()


class BallGame:
    def __init__(self):
        self.state = GameState.READY
        self.score = 0
        self.duration = 60
        self.start_time = None
        self.active_target = None

        self.width = 640
        self.height = 480

        self.target_width = 110
        self.target_height = 90
        self.screen_margin = 20
        self.min_target_distance = 180

        self.feedback_duration = 0.2
        self.hit_time = None
        self.last_ball_position = None

        # Gesture-controlled start
        self.start_width = 170
        self.start_height = 80
        self.hold_duration = 0.5
        self.hold_start = None

        # Countdown
        self.countdown_duration = 3
        self.countdown_start = None

    def start_zone(self):
        """Return START rectangle boundaries."""
        cx = self.width // 2
        cy = self.height // 2

        half_w = self.start_width // 2
        half_h = self.start_height // 2

        return (
            cx - half_w,
            cy - half_h,
            cx + half_w,
            cy + half_h
        )

    def ball_in_start(self, ball):
        if ball is None:
            return False

        x, y, radius = ball
        left, top, right, bottom = self.start_zone()

        return (
            left <= x <= right
            and top <= y <= bottom
            and radius <= min(
                self.start_width,
                self.start_height
            ) * 0.4
        )

    def handle_start_gesture(self, ball):
        """Require the ball to remain in START for 0.5s."""
        if self.state not in (
            GameState.READY,
            GameState.FINISHED
        ):
            return

        if not self.ball_in_start(ball):
            self.hold_start = None
            return

        now = time.monotonic()

        if self.hold_start is None:
            self.hold_start = now

        if now - self.hold_start >= self.hold_duration:
            self.begin_countdown()

    def hold_progress(self):
        if self.hold_start is None:
            return 0.0

        elapsed = time.monotonic() - self.hold_start
        return min(1.0, elapsed / self.hold_duration)

    def begin_countdown(self):
        self.state = GameState.COUNTDOWN
        self.countdown_start = time.monotonic()
        self.hold_start = None
        self.active_target = None
        self.start_time = None
        self.hit_time = None
        self.last_ball_position = None

    def countdown_value(self):
        if self.countdown_start is None:
            return self.countdown_duration

        elapsed = time.monotonic() - self.countdown_start
        remaining = self.countdown_duration - elapsed

        return max(0, math.ceil(remaining))

    def start(self):
        """Start a new timed round."""
        self.state = GameState.PLAYING
        self.score = 0
        self.start_time = time.monotonic()
        self.hit_time = None
        self.last_ball_position = None
        self.hold_start = None
        self.countdown_start = None
        self.spawn_target()

    def time_left(self):
        if self.start_time is None:
            return self.duration

        elapsed = time.monotonic() - self.start_time
        return max(0.0, self.duration - elapsed)

    def update(self):
        if self.state == GameState.COUNTDOWN:
            if self.countdown_value() == 0:
                self.start()
            return

        if self.state not in (
            GameState.PLAYING,
            GameState.HIT_FEEDBACK
        ):
            return

        if self.time_left() <= 0:
            self.state = GameState.FINISHED
            self.active_target = None
            self.hold_start = None
            return

        if self.state == GameState.HIT_FEEDBACK:
            elapsed = time.monotonic() - self.hit_time

            if elapsed >= self.feedback_duration:
                self.spawn_target(self.last_ball_position)
                self.hit_time = None
                self.state = GameState.PLAYING

    def spawn_target(self, ball_position=None):
        half_w = self.target_width // 2
        half_h = self.target_height // 2

        min_x = half_w + self.screen_margin
        max_x = self.width - half_w - self.screen_margin

        min_y = half_h + self.screen_margin
        max_y = self.height - half_h - self.screen_margin

        if min_x > max_x or min_y > max_y:
            raise ValueError("Screen too small for target")

        distance = self.min_target_distance

        while distance >= 0:
            for _ in range(50):
                x = random.randint(min_x, max_x)
                y = random.randint(min_y, max_y)

                if ball_position is not None:
                    bx, by = ball_position

                    separation = math.dist(
                        (x, y), (bx, by)
                    )

                    if separation < distance:
                        continue

                    if (
                        abs(x - bx) <= half_w
                        and abs(y - by) <= half_h
                    ):
                        continue

                self.active_target = (x, y)
                return self.active_target

            distance -= 20

        raise RuntimeError("Could not generate a valid target")

    def is_hit(self, ball):
        if ball is None or self.active_target is None:
            return False

        ball_x, ball_y, ball_radius = ball
        target_x, target_y = self.active_target

        half_w = self.target_width / 2
        half_h = self.target_height / 2

        inside = (
            abs(ball_x - target_x) <= half_w
            and abs(ball_y - target_y) <= half_h
        )

        valid_size = (
            ball_radius <= min(half_w, half_h) * 0.8
        )

        return inside and valid_size

    def register_hit(self, ball):
        if self.state != GameState.PLAYING:
            return False

        if self.time_left() <= 0 or not self.is_hit(ball):
            return False

        self.score += 1
        self.state = GameState.HIT_FEEDBACK
        self.hit_time = time.monotonic()
        self.last_ball_position = (ball[0], ball[1])

        return True
