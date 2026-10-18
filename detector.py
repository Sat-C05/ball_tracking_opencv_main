import cv2
import numpy as np

from config import LOWER_HSV, UPPER_HSV, BLUR_SIZE, KERNEL, MIN_AREA, MIN_CIRCULARITY, MIN_RADIUS 


def detect_ball(frame):
    blurred = cv2.GaussianBlur(frame, BLUR_SIZE, 0)

    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, LOWER_HSV, UPPER_HSV)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, KERNEL)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL)

    contours, _ = cv2.findContours(
    mask,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
    )


    candidates = []

    for contour in contours:
        area = cv2.contourArea(contour)

        if area < MIN_AREA:
            continue

        perimeter = cv2.arcLength(contour, True)

        if perimeter == 0:
            continue

        circularity = 4 * np.pi * area / (perimeter ** 2)

        if circularity < MIN_CIRCULARITY:
            continue

        (x, y), radius = cv2.minEnclosingCircle(contour)

        if radius < MIN_RADIUS:
            continue

        candidates.append((area, x, y, radius, circularity, contour))
        print(f"Candidate: Area={area:.0f}, Circularity={circularity:.2f}, Radius={radius:.1f}")


    if not candidates:
        return None, mask

    best = max(candidates, key=lambda item: item[0])

    return best, mask


