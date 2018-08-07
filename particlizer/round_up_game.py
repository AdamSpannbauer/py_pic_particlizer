import cv2
import numpy as np


def increment_blinker(blink_counter, blink_flag, blink_duration=8):
    blink_counter += 1
    if blink_counter >= blink_duration * 2:
        blink_flag = True
        blink_counter = 0
    elif blink_counter >= blink_duration:
        blink_flag = False

    return blink_counter, blink_flag


def round_up_game(canvas, particles, blink_flag, mouse_loc):
    game_mouse_size = 100
    mouse_x, mouse_y = mouse_loc

    game_mouse_color = (150, 100, 30)
    if mouse_x != float('inf') and mouse_y != float('inf'):
        cv2.circle(canvas, (mouse_x, mouse_y),
                   radius=game_mouse_size,
                   color=game_mouse_color,
                   thickness=-1)

    particle_hit_count = 0
    for particle in particles:
        particle.check_hit((mouse_x, mouse_y), game_mouse_size)
        if not particle.is_hit and np.linalg.norm(particle.location - particle.game_target) <= 30:
            if blink_flag:
                particle.color = (30, 30, 200)
            else:
                particle.color = (100, 100, 150)
            game_target = \
                tuple(np.random.randint(1, canvas.shape[1], 1)) + \
                tuple(np.random.randint(1, canvas.shape[0], 1))
            particle.game_target = np.array(game_target)
        elif particle.is_hit:
            particle_hit_count += 1

        particle.update(canvas,
                        mouse_loc=None,
                        target=particle.game_target)
        particle.show(canvas)

    game_mode = True
    if particle_hit_count == len(particles):
        game_mode = False
    else:
        cv2.putText(canvas,
                    'Caught {} of {}'.format(particle_hit_count, len(particles)),
                    (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), thickness=1)

        cv2.putText(canvas,
                    '(mouse over the particles)',
                    (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), thickness=1)

    return canvas, game_mode
