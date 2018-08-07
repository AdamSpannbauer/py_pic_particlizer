import cv2
import numpy as np

momentum = [1, 0]
rotate = 0


def pacman_move(pacman, key, canvas, blink_flag, speed=10):
    global momentum
    global rotate
    if key == ord('w'):  # up
        momentum = [0, -1]
        rotate = 270
    elif key == ord('s'):  # down
        momentum = [0, 1]
        rotate = 90
    elif key == ord('a'):  # left
        momentum = [-1, 0]
        rotate = 180
    elif key == ord('d'):  # right
        momentum = [1, 0]
        rotate = 0

    target_x = pacman.location[0] + speed * momentum[0]
    if target_x > canvas.shape[1]:
        target_x = 0
    elif target_x < 0:
        target_x = canvas.shape[1]

    target_y = pacman.location[1] + speed * momentum[1]
    if target_y > canvas.shape[0]:
        target_y = 0
    elif target_y < 0:
        target_y = canvas.shape[0]
    pacman.location = np.array([target_x, target_y])

    if blink_flag:
        cv2.ellipse(canvas,
                    tuple(pacman.location.astype('int')),
                    (pacman.radius, pacman.radius),
                    rotate, 45, 315, pacman.color, -1)
    else:
        cv2.circle(canvas,
                   tuple(pacman.location.astype('int')),
                   pacman.radius, pacman.color, -1)


def pacman_game(canvas, pacman, particles, blink_flag, key_pressed):
    pacman_move(pacman, key_pressed, canvas, blink_flag)

    particle_hit_count = 0
    for particle in particles:
        particle.check_hit(pacman.location, pacman.radius + 3)
        if particle.is_hit:
            particle.color = (50, 50, 50)
            particle_hit_count += 1

        particle.update(canvas, mouse_loc=None)
        particle.show(canvas)

    game_mode = True
    if particle_hit_count == len(particles):
        game_mode = False
    else:
        cv2.putText(canvas,
                    'Eaten {} of {}'.format(particle_hit_count, len(particles)),
                    (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), thickness=1)

        cv2.putText(canvas,
                    '(use WASD keys to move)',
                    (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), thickness=1)

    return canvas, game_mode
