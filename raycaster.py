import math
import multiprocessing
import pygame

MAP_W = 16
MAP_H = 16
map_data = [
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1,
    1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1,
    1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1,
    1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1,
    1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1,
    1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1,
    1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
]

class player:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle

FOV = 60
NUM_RAYS = FOV
SCREEN_WIDTH = 800
COL_WIDTH = SCREEN_WIDTH // NUM_RAYS

offset = -math.radians(FOV / 2)
angle_step = math.radians(1)


def cast_ray(x, y, angle, num, screen, player_angle):
    dir_x = math.cos(angle)
    dir_y = math.sin(angle)

    map_x = int(x)
    map_y = int(y)

    delta_x = abs(1 / dir_x) if dir_x != 0 else float('inf')
    delta_y = abs(1 / dir_y) if dir_y != 0 else float('inf')

    step_x = 1 if dir_x >= 0 else -1
    step_y = 1 if dir_y >= 0 else -1

    side_x = (map_x + 1 - x) * delta_x if dir_x >= 0 else (x - map_x) * delta_x
    side_y = (map_y + 1 - y) * delta_y if dir_y >= 0 else (y - map_y) * delta_y

    for _ in range(200):
        if side_x < side_y:
            side_x += delta_x
            map_x += step_x
            hit_side = 0
        else:
            side_y += delta_y
            map_y += step_y
            hit_side = 1

        if not (0 <= map_x < MAP_W and 0 <= map_y < MAP_H):
            break

        if map_data[map_y * MAP_W + map_x] == 1:
            if hit_side == 0:
                distance = (map_x - x + (1 - step_x) / 2) / dir_x
            else:
                distance = (map_y - y + (1 - step_y) / 2) / dir_y

            distance = distance * math.cos(angle - player_angle)
            draw_wall(distance, num, screen, hit_side)
            break


def raycast(Player, screen):
    angle = Player.angle + offset
    num = 0
    while angle < Player.angle + math.fabs(offset):
        cast_ray(Player.x, Player.y, angle, num, screen, Player.angle)
        angle += angle_step
        num += 1


def draw_wall(distance, num, screen, hit_side=0):
    if distance <= 0:
        distance = 0.01

    width = COL_WIDTH
    x = width * num
    screen_height = screen.get_height()
    height = int(screen_height / distance)
    y = (screen_height - height) // 2

    shade = max(0, min(255, int(255 / (1 + distance * 0.5))))
    if hit_side == 1:
        shade = shade * 2 // 3
    pygame.draw.rect(screen, (shade, shade, shade), (x, y, width, height))


def dda_hit(x, y, angle):
    dir_x = math.cos(angle)
    dir_y = math.sin(angle)
    map_x = int(x)
    map_y = int(y)
    delta_x = abs(1 / dir_x) if dir_x != 0 else float('inf')
    delta_y = abs(1 / dir_y) if dir_y != 0 else float('inf')
    step_x = 1 if dir_x >= 0 else -1
    step_y = 1 if dir_y >= 0 else -1
    side_x = (map_x + 1 - x) * delta_x if dir_x >= 0 else (x - map_x) * delta_x
    side_y = (map_y + 1 - y) * delta_y if dir_y >= 0 else (y - map_y) * delta_y

    for _ in range(200):
        if side_x < side_y:
            side_x += delta_x
            map_x += step_x
            hit_side = 0
        else:
            side_y += delta_y
            map_y += step_y
            hit_side = 1

        if not (0 <= map_x < MAP_W and 0 <= map_y < MAP_H):
            break

        if map_data[map_y * MAP_W + map_x] == 1:
            if hit_side == 0:
                dist = (map_x - x + (1 - step_x) / 2) / dir_x
            else:
                dist = (map_y - y + (1 - step_y) / 2) / dir_y
            return x + dir_x * dist, y + dir_y * dist

    return x + dir_x * MAP_W, y + dir_y * MAP_H


# --- top-down view process ---

def topdown_process(shared):
    pygame.init()
    CELL = 24
    screen = pygame.display.set_mode((MAP_W * CELL, MAP_H * CELL))
    pygame.display.set_caption("Top-down")
    clock = pygame.time.Clock()

    WALL_COLOR = (180, 180, 180)
    FLOOR_COLOR = (40, 40, 40)
    PLAYER_COLOR = (255, 80, 80)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        px, py, pangle = shared[0], shared[1], shared[2]

        screen.fill(FLOOR_COLOR)

        for row in range(MAP_H):
            for col in range(MAP_W):
                if map_data[row * MAP_W + col] == 1:
                    pygame.draw.rect(screen, WALL_COLOR,
                                     (col * CELL, row * CELL, CELL, CELL))

        # draw FOV rays clipped to wall hit
        angle = pangle + offset
        while angle < pangle + math.fabs(offset):
            hit_x, hit_y = dda_hit(px, py, angle)
            pygame.draw.line(screen, (80, 80, 30),
                             (int(px * CELL), int(py * CELL)),
                             (int(hit_x * CELL), int(hit_y * CELL)), 1)
            angle += angle_step

        # draw player
        pygame.draw.circle(screen, PLAYER_COLOR,
                           (int(px * CELL), int(py * CELL)), 5)
        # draw direction arrow
        arrow_len = 12
        pygame.draw.line(screen, PLAYER_COLOR,
                         (int(px * CELL), int(py * CELL)),
                         (int(px * CELL + math.cos(pangle) * arrow_len),
                          int(py * CELL + math.sin(pangle) * arrow_len)), 2)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def main():
    # shared memory: [x, y, angle]
    shared = multiprocessing.Array('d', [1.5, 1.5, 0.0])

    td = multiprocessing.Process(target=topdown_process, args=(shared,), daemon=True)
    td.start()

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Raycaster")
    P = player(1.5, 1.5, 0)

    MOVE_SPEED = 0.05
    TURN_SPEED = 0.05
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            P.angle -= TURN_SPEED
        if keys[pygame.K_d]:
            P.angle += TURN_SPEED

        dx = math.cos(P.angle) * MOVE_SPEED
        dy = math.sin(P.angle) * MOVE_SPEED

        new_x, new_y = P.x, P.y
        if keys[pygame.K_w]:
            new_x += dx
            new_y += dy
        if keys[pygame.K_s]:
            new_x -= dx
            new_y -= dy

        if map_data[int(new_y) * MAP_W + int(new_x)] == 0:
            P.x, P.y = new_x, new_y

        shared[0], shared[1], shared[2] = P.x, P.y, P.angle

        screen.fill((0, 0, 0))
        raycast(P, screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    main()
