import pygame as pg
import numpy as np

from copy import deepcopy
from numba import njit

# window and grid settings
RES = WIDTH, HEIGHT = 1600, 900
TILE = 10
W, H = WIDTH // TILE, HEIGHT // TILE
FPS = 60

# some global variables
STATE = 'stop'
CELL_COLOR = 'magenta'
DO_STEP = False

# pygame init
pg.init()
surface = pg.display.set_mode(RES)
clock = pg.time.Clock()

# res and fields
start_res = []
current_res = []
current_field = np.array([[0 for i in range(W)] for j in range(H)])
next_field = np.array([[0 for i in range(W)] for j in range(H)])


@njit(fastmath=True)
def check_cells(current_field, next_field):
    res = []
    for x in range(1, W - 1):
        for y in range(1, H - 1):
            count = 0
            for j in range(y - 1, y + 2):
                for i in range(x - 1, x + 2):
                    if current_field[j][i] == 1:
                        count += 1

            if current_field[y][x] == 1:
                count -= 1
                if count == 2 or count == 3:
                    next_field[y][x] = 1
                    res.append((x, y))
                else:
                    next_field[y][x] = 0
            else:
                if count == 3:
                    next_field[y][x] = 1
                    res.append((x, y))
                else:
                    next_field[y][x] = 0

    return next_field, res


def get_mouse_click():
    x, y = pg.mouse.get_pos()
    grid_x, grid_y = x // TILE, y // TILE
    click = pg.mouse.get_pressed()
    return (grid_x, grid_y, 'l' if click[0] else 'r' if click[2] else '') if (click[0] or click[2]) else False


def draw_field(res):
    [pg.draw.rect(surface, pg.Color(CELL_COLOR), (x * TILE + 1, y * TILE + 1, TILE - 1, TILE - 1)) for x, y in res]


def save_pattern():
    file_name = input('Enter file name, \'q\' to exit: ')
    if file_name.lower() == 'q':
        return
    with open(file_name + '.txt', 'w') as f:
        for line in start_res:
            f.write(f'{str(line[0])}, {str(line[1])}\n')
        print(f'File \'{file_name}\' successfully saved.')
        f.close()


def open_pattern():
    global current_field
    file_name = input('Enter file name, \'q\' to exit: ')
    if file_name.lower() == 'q':
        return
    try:
        with open(file_name + '.txt', 'r') as f:
            current_res.clear()
            current_field = np.array([[0 for i in range(W)] for j in range(H)])
            for line in f.readlines():
                t = line.split(',')
                x, y = int(t[0]), int(t[1])
                current_field[y][x] = 1
                start_res.append((x, y))
            print(f'File \'{file_name}\' successfully opened.')
            f.close()
    except FileNotFoundError:
        print(f'Can not open this file {file_name}')


while True:
    surface.fill(pg.Color('black'))
    # draw grid
    [pg.draw.line(surface, pg.Color('dimgray'), (x, 0), (x, HEIGHT)) for x in range(0, WIDTH, TILE)]
    [pg.draw.line(surface, pg.Color('dimgray'), (0, y), (WIDTH, y)) for y in range(0, HEIGHT, TILE)]

    # handle keys
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()
        if event.type == pg.KEYDOWN:
            if event.key == 13 and (STATE == 'stop' or STATE == 'pause'):
                STATE = 'start'
                current_field = np.array([[1 if (i, j) in current_res else 0 for i in range(W)] for j in range(H)])
            elif event.key == pg.K_c and STATE == 'stop':
                start_res = []
                current_field = np.array([[0 for i in range(W)] for j in range(H)])
            elif event.key == pg.K_p:
                STATE = 'pause'
                current_field = np.array([[1 if (i, j) in current_res else 0 for i in range(W)] for j in range(H)])
            elif event.key == pg.K_r:
                STATE = 'stop'
            elif event.key == pg.K_RIGHT and STATE == 'pause':
                DO_STEP = True
            elif event.key == pg.K_s and STATE == 'stop':
                save_pattern()
            elif event.key == pg.K_o and STATE == 'stop':
                open_pattern()

    # create start field
    if STATE == 'stop':
        mouse_pos = get_mouse_click()
        if mouse_pos:
            if mouse_pos[2] == 'l':
                if (mouse_pos[0], mouse_pos[1]) not in start_res:
                    start_res.append((mouse_pos[0], mouse_pos[1]))
            elif mouse_pos[2] == 'r':
                try:
                    start_res.remove((mouse_pos[0], mouse_pos[1]))
                except ValueError:
                    pass
        current_res = start_res
    # start a game
    elif STATE == 'start':
        next_field, res = check_cells(current_field, next_field)
        current_res = res
        current_field = deepcopy(next_field)
    # pause
    elif STATE == 'pause':
        if DO_STEP:
            next_field, res = check_cells(current_field, next_field)
            current_res = res
            current_field = deepcopy(next_field)
            DO_STEP = False

    # draw life
    draw_field(current_res)
    pg.display.flip()
    clock.tick(FPS)
    # print(clock.get_fps())

# Left mouse click to create cell
# Right mouse click to delete cell
# 'c' to clear the field
# 'p' to pause te game
# 'r' to restart the game
# 's' to save pattern
# 'o' to open pattern
# 'right arrow' to make one step forward(first go to 'pause')
# 'ENTER' to start the game
