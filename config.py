import numpy as np

# HSV color range for the tennis ball
LOWER_HSV = np.array([20, 40, 40])
UPPER_HSV = np.array([85, 255, 255])

# Image preprocessing
BLUR_SIZE = (5, 5)
KERNEL = np.ones((5, 5), dtype=np.uint8)

# Detection constraints
MIN_AREA = 600
MIN_CIRCULARITY = 0.55
MIN_RADIUS = 10

# Position smoothing
SMOOTHING_ALPHA = 0.75

MAX_MISSING_FRAMES = 5
