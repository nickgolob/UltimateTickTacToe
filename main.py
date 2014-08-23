import pygame
import itertools

# ---- constants:
BLOCK_WIDTH = 70
SEC_SEP_WIDTH = 3
PRM_SEP_WIDTH = 10
CONSOLE_WIDTH = 80
SUB_WIDTH = 3 * BLOCK_WIDTH + 2 * SEC_SEP_WIDTH
SCREEN_WIDTH = 4 * PRM_SEP_WIDTH + 3 * SUB_WIDTH
SCREEN_HEIGHT = SCREEN_WIDTH + CONSOLE_WIDTH

X, O = True, False

def yieldPrmSeps(prmSeps):
    for i in range(2):
        for j in range(4):
            yield prmSeps[i][j]
def yieldSecSeps(secSeps):
    for i in range(3):
        for j in range(3):
            for k in range(2):
                for l in range(2):
                    yield secSeps[i][j][k][l]
def yieldBoardAndCoords(board):
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(3):
                    yield board[i][j][k][l], i, j, k, l

def posToBox(pos, invalids):
    # validate:
    x, y = pos
    if not x in range(SCREEN_WIDTH) or y not in range(SCREEN_WIDTH):
        return False, None
    for line in invalids:
        if line.collidepoint(x, y):
            return False, None
    return True, (
        x // (PRM_SEP_WIDTH + SUB_WIDTH),
        y // (PRM_SEP_WIDTH + SUB_WIDTH),
        (x % (PRM_SEP_WIDTH + SUB_WIDTH)) // (SEC_SEP_WIDTH + BLOCK_WIDTH),
        (y % (PRM_SEP_WIDTH + SUB_WIDTH)) // (SEC_SEP_WIDTH + BLOCK_WIDTH))

def boxIndexToCenterPos(i, j, k, l):
    x = PRM_SEP_WIDTH + i * (SUB_WIDTH + PRM_SEP_WIDTH) + \
        k * (BLOCK_WIDTH + SEC_SEP_WIDTH) + (BLOCK_WIDTH // 2)
    y = PRM_SEP_WIDTH + j * (SUB_WIDTH + PRM_SEP_WIDTH) + \
        l * (BLOCK_WIDTH + SEC_SEP_WIDTH) + (BLOCK_WIDTH // 2)
    return x, y

def checkWin(i, j, k, l, board):
    char = board[i][j][k][l]
    for x in range(3):
        if board[i][j][x][l] != char:
            break
    else:
        return (True, 'cross')
    for y in range(3):
        if board[i][j][k][y] != char:
            break
    else:
        return (True, 'down')
    if (k + l) % 2 == 0: # can have diag
        if k - l == 0:
            for x in range(3):
                if board[i][j][x][x] != char:
                    break
            else:
                return (True, 'neg')
        if k - l != 0 or k == 1:
            for x in range(3):
                if board[i][j][x][2 - x] != char:
                    break
            else:
                return (True, 'pos')
    return (False, None)

def main():
    # ---- engine init:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('UltimateToe')
    clock = pygame.time.Clock()

    # ---- draw init:
    boardBacks = [[
        # (0, 1, 2) X (0, 1, 2)
        pygame.Rect(PRM_SEP_WIDTH + i * (SUB_WIDTH + PRM_SEP_WIDTH),
                    PRM_SEP_WIDTH + j * (SUB_WIDTH + PRM_SEP_WIDTH),
                    SUB_WIDTH, SUB_WIDTH)
        for j in range(3)] for i in range(3)]

    prmSeperators = [
        # (0, 1) X (0, 1, 2, 3) primaries:
        [pygame.Rect(i * (PRM_SEP_WIDTH + SUB_WIDTH), 0,
                     PRM_SEP_WIDTH, SCREEN_WIDTH)
         for i in range(4)],
        [pygame.Rect(0, i * (PRM_SEP_WIDTH + SUB_WIDTH),
                     SCREEN_WIDTH, PRM_SEP_WIDTH)
         for i in range(4)]]

    secSeperators = [[[[
        # (0, 1, 2) X (0, 1, 2) X (0, 1) X (0, 1) secondaries:
        pygame.Rect(
            PRM_SEP_WIDTH + i * (SUB_WIDTH + PRM_SEP_WIDTH) + \
            BLOCK_WIDTH + k * (BLOCK_WIDTH + SEC_SEP_WIDTH),
            PRM_SEP_WIDTH + j * (SUB_WIDTH + PRM_SEP_WIDTH),
            SEC_SEP_WIDTH, SUB_WIDTH),
        pygame.Rect(
            PRM_SEP_WIDTH + i * (SUB_WIDTH + PRM_SEP_WIDTH),
            PRM_SEP_WIDTH + j * (SUB_WIDTH + PRM_SEP_WIDTH) + \
            BLOCK_WIDTH + k * (BLOCK_WIDTH + SEC_SEP_WIDTH),
            SUB_WIDTH, SEC_SEP_WIDTH)
        ] for k in range(2)] for j in range(3)] for i in range(3)]

    boardSymbols = {
        'x' : pygame.font.SysFont('', 70).render('X', 0, (0, 0, 0)),
        'o' : pygame.font.SysFont('', 70).render('O', 0, (0, 0, 0))
    }

    consoleTexts = {
        'x-turn' : pygame.font.SysFont('', 50).render('X\'s move', 0, (0, 0, 0)),
        'o-turn' : pygame.font.SysFont('', 50).render('O\'s move', 0, (0, 0, 0)),
        'x-win' : pygame.font.SysFont('', 50).render('X has won', 0, (0, 0, 0)),
        'o-win' : pygame.font.SysFont('', 50).render('O has won', 0, (0, 0, 0)),
        'draw' : pygame.font.SysFont('', 50).render('stalemate', 0, (0, 0, 0))
    }

    # ---- logic init:
    board = [[[[
        # PRM ROW X PRM COL X SEC ROW X SEC COL
        None for l in range(3)] for k in range(3)]
        for j in range(3)] for i in range(3)]

    move, turn, won = X, 0, False

    # ---- game loop
    while turn < 81:

        # ---- input:
        validInput = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(event.pos)
                validInput, coords = posToBox(event.pos,
                    itertools.chain(yieldPrmSeps(prmSeperators),
                                    yieldSecSeps(secSeperators)))
                if validInput:
                    print('golden', coords)

        # ---- logic:
        if validInput:
            i, j, k, l = coords
            if turn == 0 or (i == x and j == y and not board[i][j][k][l]):
                # we're in business
                board[i][j][k][l] = 'x' if move == X else 'o'
                won, direct = checkWin(i, j, k, l, board)
                if won:
                    break
                x, y = k, l
                move, turn = not move, turn + 1

        # ---- drawing:
        screen.fill((255, 255, 255))
        if turn > 0:
            pygame.draw.rect(screen, (139, 255, 190), boardBacks[x][y])
        for line in yieldPrmSeps(prmSeperators):
            pygame.draw.rect(screen, (255, 0, 0), line)
        for line in yieldSecSeps(secSeperators):
            pygame.draw.rect(screen, (0, 0, 255), line)
        for char, i, j, k, l in yieldBoardAndCoords(board):
            if char == 'x' or char == 'o':
                width, height = boardSymbols[char].get_size()
                _x, _y = boxIndexToCenterPos(i, j, k, l)
                screen.blit(boardSymbols[char], (_x - width // 2, _y - height // 2))
        key = 'x-turn' if move == X else 'o-turn'
        width, height = consoleTexts[key].get_size()
        _x, _y = (SCREEN_WIDTH // 2, SCREEN_WIDTH + CONSOLE_WIDTH // 2)
        screen.blit(consoleTexts[key], (_x - width // 2, _y - height // 2))

        pygame.display.flip()

        # ---- iterate:
        clock.tick(30)

    # ---- final drawing:
    screen.fill((255, 255, 255))
    for line in yieldPrmSeps(prmSeperators):
        pygame.draw.rect(screen, (255, 0, 0), line)
    for line in yieldSecSeps(secSeperators):
        pygame.draw.rect(screen, (0, 0, 255), line)
    for char, _i, _j, _k, _l in yieldBoardAndCoords(board):
        if char == 'x' or char == 'o':
            width, height = boardSymbols[char].get_size()
            _x, _y = boxIndexToCenterPos(_i, _j, _k, _l)
            screen.blit(boardSymbols[char], (_x - width // 2, _y - height // 2))
    if won:
        key = 'x-win' if move == X else 'o-win'
        if direct == 'cross':
            start_x, start_y, end_x, end_y = 0, l, 2, l
        elif direct == 'down':
            start_x, start_y, end_x, end_y = k, 0, k, 2
        elif direct == 'neg':
            start_x, start_y, end_x, end_y = 0, 0, 2, 2
        else:
            start_x, start_y, end_x, end_y = 0, 2, 2, 0
        pygame.draw.line(screen, (0, 255, 0),
                         boxIndexToCenterPos(i, j, start_x, start_y),
                         boxIndexToCenterPos(i, j, end_x, end_y), 10)
    else:
        key = 'draw'
    width, height = consoleTexts[key].get_size()
    _x, _y = (SCREEN_WIDTH // 2, SCREEN_WIDTH + CONSOLE_WIDTH // 2)
    screen.blit(consoleTexts[key], (_x - width // 2, _y - height // 2))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        clock.tick(30)

if __name__ == '__main__':
    main()