#author: hanshiqiang365 （微信公众号）
import sys
import time
import pygame
import random
from collections import namedtuple
from pygame.locals import *

SIZE = 30
BLOCK_HEIGHT = 20
BLOCK_WIDTH = 10
BORDER_WIDTH = 4
BORDER_COLOR = (20, 240, 20)
SCREEN_WIDTH = SIZE * (BLOCK_WIDTH + 5)
SCREEN_HEIGHT = SIZE * BLOCK_HEIGHT
BG_COLOR = (20, 120, 20)
BLACK = (0, 0, 0)
RED = (255, 20, 20) 

Point = namedtuple('Point', 'X Y')
Shape = namedtuple('Shape', 'X Y Width Height')
Block = namedtuple('Block', 'template start_pos end_pos name next')

S_BLOCK = [Block(['.OO',
                  'OO.',
                  '...'], Point(0, 0), Point(2, 1), 'S', 1),
           Block(['O..',
                  'OO.',
                  '.O.'], Point(0, 0), Point(1, 2), 'S', 0)]

Z_BLOCK = [Block(['OO.',
                  '.OO',
                  '...'], Point(0, 0), Point(2, 1), 'Z', 1),
           Block(['.O.',
                  'OO.',
                  'O..'], Point(0, 0), Point(1, 2), 'Z', 0)]

I_BLOCK = [Block(['.O..',
                  '.O..',
                  '.O..',
                  '.O..'], Point(1, 0), Point(1, 3), 'I', 1),
           Block(['....',
                  '....',
                  'OOOO',
                  '....'], Point(0, 2), Point(3, 2), 'I', 0)]

O_BLOCK = [Block(['OO',
                  'OO'], Point(0, 0), Point(1, 1), 'O', 0)]

J_BLOCK = [Block(['O..',
                  'OOO',
                  '...'], Point(0, 0), Point(2, 1), 'J', 1),
           Block(['.OO',
                  '.O.',
                  '.O.'], Point(1, 0), Point(2, 2), 'J', 2),
           Block(['...',
                  'OOO',
                  '..O'], Point(0, 1), Point(2, 2), 'J', 3),
           Block(['.O.',
                  '.O.',
                  'OO.'], Point(0, 0), Point(1, 2), 'J', 0)]

L_BLOCK = [Block(['..O',
                  'OOO',
                  '...'], Point(0, 0), Point(2, 1), 'L', 1),
           Block(['.O.',
                  '.O.',
                  '.OO'], Point(1, 0), Point(2, 2), 'L', 2),
           Block(['...',
                  'OOO',
                  'O..'], Point(0, 1), Point(2, 2), 'L', 3),
           Block(['OO.',
                  '.O.',
                  '.O.'], Point(0, 0), Point(1, 2), 'L', 0)]

T_BLOCK = [Block(['.O.',
                  'OOO',
                  '...'], Point(0, 0), Point(2, 1), 'T', 1),
           Block(['.O.',
                  '.OO',
                  '.O.'], Point(1, 0), Point(2, 2), 'T', 2),
           Block(['...',
                  'OOO',
                  '.O.'], Point(0, 1), Point(2, 2), 'T', 3),
           Block(['.O.',
                  'OO.',
                  '.O.'], Point(0, 0), Point(1, 2), 'T', 0)]

BLOCKS = {'O': O_BLOCK,
          'I': I_BLOCK,
          'Z': Z_BLOCK,
          'T': T_BLOCK,
          'L': L_BLOCK,
          'S': S_BLOCK,
          'J': J_BLOCK}


def get_block():
    block_name = random.choice('OIZTLSJ')
    b = BLOCKS[block_name]
    idx = random.randint(0, len(b) - 1)
    return b[idx]


def get_next_block(block):
    b = BLOCKS[block.name]
    return b[block.next]



def print_text(screen, font, x, y, text, fcolor=(255, 255, 255)):
    imgText = font.render(text, True, fcolor)
    screen.blit(imgText, (x, y))


def main():
    pygame.init()

    gameIcon = pygame.image.load("game_icon.jpg")
    pygame.display.set_icon(gameIcon)

    pygame.mixer.init()
    pygame.mixer.music.load("game_bgm.wav")
    pygame.mixer.music.play(-1)
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetris Game  - Developed by hanshiqiang365')

    font1 = pygame.font.SysFont('SimHei', 24)
    font2 = pygame.font.Font(None, 72)
    font_pos_x = BLOCK_WIDTH * SIZE + BORDER_WIDTH + 10 
    gameover_size = font2.size('GAME OVER')
    font1_height = int(font1.size('得分')[1])

    cur_block = None
    next_block = None
    block_color = (20, 255, 20)  
    cur_pos_x, cur_pos_y = 0, 0

    game_area = None
    game_over = True
    start = False
    score = 0
    orispeed = 0.5
    speed = orispeed
    pause = False
    last_drop_time = None
    last_press_time = None

    def _dock():
        nonlocal cur_block, next_block, game_area, cur_pos_x, cur_pos_y, game_over, score, speed
        for _i in range(cur_block.start_pos.Y, cur_block.end_pos.Y + 1):
            for _j in range(cur_block.start_pos.X, cur_block.end_pos.X + 1):
                if cur_block.template[_i][_j] != '.':
                    game_area[cur_pos_y + _i][cur_pos_x + _j] = '0'
        if cur_pos_y + cur_block.start_pos.Y <= 0:
            game_over = True
        else:
            remove_idxs = []
            for _i in range(cur_block.start_pos.Y, cur_block.end_pos.Y + 1):
                if all(_x == '0' for _x in game_area[cur_pos_y + _i]):
                    remove_idxs.append(cur_pos_y + _i)
                    
            if remove_idxs:
                remove_count = len(remove_idxs)
                if remove_count == 1:
                    score += 100
                elif remove_count == 2:
                    score += 300
                elif remove_count == 3:
                    score += 700
                elif remove_count == 4:
                    score += 1500
                speed = orispeed - 0.03 * (score // 10000)
                
                _i = _j = remove_idxs[-1]
                while _i >= 0:
                    while _j in remove_idxs:
                        _j -= 1
                    if _j < 0:
                        game_area[_i] = ['.'] * BLOCK_WIDTH
                    else:
                        game_area[_i] = game_area[_j]
                    _i -= 1
                    _j -= 1
            cur_block = next_block
            next_block = get_block()
            cur_pos_x, cur_pos_y = (BLOCK_WIDTH - cur_block.end_pos.X - 1) // 2, -1 - cur_block.end_pos.Y

    def _judge(pos_x, pos_y, block):
        nonlocal game_area
        for _i in range(block.start_pos.Y, block.end_pos.Y + 1):
            if pos_y + block.end_pos.Y >= BLOCK_HEIGHT:
                return False
            for _j in range(block.start_pos.X, block.end_pos.X + 1):
                if pos_y + _i >= 0 and block.template[_i][_j] != '.' and game_area[pos_y + _i][pos_x + _j] != '.':
                    return False
        return True

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if game_over:
                        start = True
                        game_over = False
                        score = 0
                        last_drop_time = time.time()
                        last_press_time = time.time()
                        game_area = [['.'] * BLOCK_WIDTH for _ in range(BLOCK_HEIGHT)]
                        cur_block = get_block()
                        next_block = get_block()
                        cur_pos_x, cur_pos_y = (BLOCK_WIDTH - cur_block.end_pos.X - 1) // 2, -1 - cur_block.end_pos.Y
                elif event.key == K_SPACE:
                    if not game_over:
                        pause = not pause
                elif event.key in (K_w, K_UP):
                    if 0 <= cur_pos_x <= BLOCK_WIDTH - len(cur_block.template[0]):
                        _next_block = get_next_block(cur_block)
                        if _judge(cur_pos_x, cur_pos_y, _next_block):
                            cur_block = _next_block

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                if not game_over and not pause:
                    if time.time() - last_press_time > 0.1:
                        last_press_time = time.time()
                        if cur_pos_x > - cur_block.start_pos.X:
                            if _judge(cur_pos_x - 1, cur_pos_y, cur_block):
                                cur_pos_x -= 1
            if event.key == pygame.K_RIGHT:
                if not game_over and not pause:
                    if time.time() - last_press_time > 0.1:
                        last_press_time = time.time()
                        if cur_pos_x + cur_block.end_pos.X + 1 < BLOCK_WIDTH:
                            if _judge(cur_pos_x + 1, cur_pos_y, cur_block):
                                cur_pos_x += 1
            if event.key == pygame.K_DOWN:
                if not game_over and not pause:
                    if time.time() - last_press_time > 0.1:
                        last_press_time = time.time()
                        if not _judge(cur_pos_x, cur_pos_y + 1, cur_block):
                            _dock()
                        else:
                            last_drop_time = time.time()
                            cur_pos_y += 1

        screen.fill(BG_COLOR)
        pygame.draw.line(screen, BORDER_COLOR,
                         (SIZE * BLOCK_WIDTH + BORDER_WIDTH // 2, 0),
                         (SIZE * BLOCK_WIDTH + BORDER_WIDTH // 2, SCREEN_HEIGHT), BORDER_WIDTH)

        if game_area:
            for i, row in enumerate(game_area):
                for j, cell in enumerate(row):
                    if cell != '.':
                        pygame.draw.rect(screen, block_color, (j * SIZE, i * SIZE, SIZE, SIZE), 0)

        for x in range(BLOCK_WIDTH):
            pygame.draw.line(screen, BLACK, (x * SIZE, 0), (x * SIZE, SCREEN_HEIGHT), 1)
        for y in range(BLOCK_HEIGHT):
            pygame.draw.line(screen, BLACK, (0, y * SIZE), (BLOCK_WIDTH * SIZE, y * SIZE), 1)

        if not game_over:
            cur_drop_time = time.time()
            if cur_drop_time - last_drop_time > speed:
                if not pause:
                    if not _judge(cur_pos_x, cur_pos_y + 1, cur_block):
                        _dock()
                    else:
                        last_drop_time = cur_drop_time
                        cur_pos_y += 1
        else:
            if start:
                print_text(screen, font2,
                           (SCREEN_WIDTH - gameover_size[0]) // 2, (SCREEN_HEIGHT - gameover_size[1]) // 2,'GAME OVER', RED)

        if cur_block:
            for i in range(cur_block.start_pos.Y, cur_block.end_pos.Y + 1):
                for j in range(cur_block.start_pos.X, cur_block.end_pos.X + 1):
                    if cur_block.template[i][j] != '.':
                        pygame.draw.rect(screen, block_color,
                                         ((cur_pos_x + j) * SIZE, (cur_pos_y + i) * SIZE, SIZE, SIZE), 0)

        print_text(screen, font1, font_pos_x, 10, f'得分: ')
        print_text(screen, font1, font_pos_x, 10 + font1_height + 6, f'{score}')
        print_text(screen, font1, font_pos_x, 20 + (font1_height + 6) * 2, f'速度: ')
        print_text(screen, font1, font_pos_x, 20 + (font1_height + 6) * 3, f'{score // 10000}')
        print_text(screen, font1, font_pos_x, 30 + (font1_height + 6) * 4, f'下一个：')

        if next_block:
            _h = 30 + (font1_height + 6) * 5
            for i in range(next_block.start_pos.Y, next_block.end_pos.Y + 1):
                for j in range(next_block.start_pos.X, next_block.end_pos.X + 1):
                    if next_block.template[i][j] != '.':
                        pygame.draw.rect(screen, block_color, (font_pos_x + j * SIZE, _h + i * SIZE, SIZE, SIZE), 0)

        pygame.display.flip()


if __name__ == '__main__':
    main()
