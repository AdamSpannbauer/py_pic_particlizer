from datetime import datetime
import cv2
import numpy as np
from .particle_class import Particle
from .round_up_game import round_up_game, increment_blinker
from .pacman_game import pacman_game


def image_to_particles(image, canvas, every_n=20, radius=4, thresh_args=(), background_color=(50, 50, 50)):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if not thresh_args:
        thresh_args = (5, 255, 0)
    _, threshed = cv2.threshold(gray, *thresh_args)

    _, contours, _ = cv2.findContours(threshed, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    canvas_area = canvas.shape[0] * canvas.shape[1]
    contour_points = []
    contour_colors = []
    for c in contours:
        if cv2.contourArea(c) >= .95 * canvas_area:
            continue
        color = get_contour_color(c, image, background_color)
        if not color == background_color:
            contour_colors.append(color)
            contour_points.append(down_sample_points(c, every_n))

    particles = create_particles(contour_points,
                                 contour_colors,
                                 image,
                                 rand_location=True,
                                 radius=radius,
                                 background_color=background_color)

    return particles


def down_sample_points(contour, every_n=20):
    return contour[::every_n]


def get_contour_color(contour, image, background_color=(50, 50, 50)):
    moments = cv2.moments(contour)
    if not sum(list(moments.values())):
        return background_color
    cx = int(moments["m10"] / moments["m00"])
    cy = int(moments["m01"] / moments["m00"])

    color = image[cy, cx]

    if sum(color) <= 30:
        mask = np.zeros(image.shape[:2], dtype='uint8')
        cv2.drawContours(mask, [contour], -1, 255, -1)

        masked = cv2.bitwise_and(image, image, mask=mask)
        non_zero = np.where(masked != 0)
        if non_zero:
            color_pool = masked[non_zero[0], non_zero[1], :]
            color = np.mean(color_pool, axis=0)

    return tuple(int(x) for x in color)


def create_particles(contour_points, contour_colors, canvas, rand_location=True, radius=4,
                     background_color=(50, 50, 50)):
    particles = []
    for i, points in enumerate(contour_points):
        color = contour_colors[i]
        for point in points:
            location = target = tuple(point.flatten())
            if rand_location:
                location = tuple(np.random.randint(1, canvas.shape[1], 1)) + \
                           tuple(np.random.randint(1, canvas.shape[0], 1))
            particle = Particle(location, target, radius, color, background_color=background_color)
            particles.append(particle)

    return particles


mouse_x = float('inf')
mouse_y = float('inf')


def get_mouse_xy(event, x, y, flags, param):
    global mouse_x
    global mouse_y
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x = x
        mouse_y = y


def particlize(image, background_color=(50, 50, 50), *args):
    canvas = np.zeros(image.shape, dtype='uint8') + np.array(background_color, dtype='uint8')
    particles = image_to_particles(image, canvas, every_n=20, radius=4, thresh_args=args)

    window_name = 'Press R to randomize, G to toggle game mode, ESC to quit'
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, get_mouse_xy)

    game_mode = False
    game_ind = 0
    blink_counter = 0
    blink_flag = False
    key = 103
    pacman = Particle((0, 0), (0, 0), radius=10, color=(0, 255, 255))
    game_start = datetime.now()
    game_time = 0
    best_time = best_round_up_game_time = best_pacman_game_time = 999
    while True:
        canvas_i = canvas.copy()
        if game_mode:
            blink_counter, blink_flag = increment_blinker(blink_counter, blink_flag)
            if game_ind == 0:
                canvas_i, game_mode = round_up_game(canvas_i,
                                                    particles,
                                                    blink_flag,
                                                    (mouse_x, mouse_y))
                game_time = datetime.now() - game_start
                game_time = game_time.total_seconds()

                if not game_mode:
                    best_round_up_game_time = min([best_round_up_game_time, game_time])
                best_time = best_round_up_game_time

            elif game_ind == 1:
                canvas_i, game_mode = pacman_game(canvas_i, pacman, particles, blink_flag, key)

                game_time = datetime.now() - game_start
                game_time = game_time.total_seconds()

                if not game_mode:
                    best_pacman_game_time = min([best_pacman_game_time, game_time])
                best_time = best_pacman_game_time

            cv2.putText(canvas_i,
                        '{0:.{1}f} (BEST: {2:.{3}f})'.format(game_time, 2, best_time, 1),
                        (10, canvas.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (30, 30, 200), thickness=3)

        else:
            for particle in particles:
                particle.color = particle.og_color
                particle.is_hit = False
                particle.update(canvas_i, (mouse_x, mouse_y))
                particle.show(canvas_i)

        cv2.imshow(window_name, canvas_i)
        key = cv2.waitKey(10)

        if key == 27:
            break
        elif key == ord('r'):
            for particle in particles:
                particle.location = tuple(np.random.randint(1, canvas.shape[1], 1)) + \
                                    tuple(np.random.randint(1, canvas.shape[0], 1))
        elif key == ord('g'):
            game_start = datetime.now()
            game_mode = not game_mode
            game_ind = np.random.randint(0, 2)
            pacman = Particle((0, 0), (0, 0), radius=15, color=(0, 255, 255))
