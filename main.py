import cv2

from config import SMOOTHING_ALPHA, MAX_MISSING_FRAMES
from detector import detect_ball


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        cap.release()
        raise RuntimeError("Could not open webcam")

    smooth_center = None
    smooth_radius = None
    missing_frames = 0

    try:
        while True:
            success, frame = cap.read()

            if not success:
                print("Unable to read webcam frame.")
                break

            # Mirror the webcam
            frame = cv2.flip(frame, 1)

            # Detect the tennis ball
            detection, mask = detect_ball(frame)

            if detection is not None:
                missing_frames = 0

                area, x, y, radius, circularity, contour = detection

                # Initialize or update EMA smoothing
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

                # Draw contour, circle and center
                cv2.drawContours(
                    frame, [contour], -1, (0, 255, 255), 2
                )
                cv2.circle(frame, (sx, sy), sr, (0, 255, 0), 2)
                cv2.circle(frame, (sx, sy), 4, (0, 0, 255), -1)

                cv2.putText(
                    frame,
                    f"Ball ({sx}, {sy}) C:{circularity:.2f}",
                    (max(0, sx - 80), max(20, sy - sr - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2
                )

            else:
                missing_frames += 1

                if missing_frames > MAX_MISSING_FRAMES:
                    smooth_center = None
                    smooth_radius = None

            cv2.imshow("Ball Detector", frame)
            cv2.imshow("HSV Mask", mask)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
