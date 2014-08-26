import itertools
import pygame
from computerPlayers import computerPlayer, baseAI
from constants import *

noPlayer = True

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

class GraphicsManager():

    def __init__(self):

        self.startPromptText = pygame.font.SysFont('', 30).render('1-player vs. AI or 2-player?', 0, (0, 0, 0))
        self.singleplayerButton = pygame.Rect(
            (SCREEN_WIDTH * 3) // 4 + PROMPT_BUTTON_SEP_WIDTH // 2 - BUTTON_WIDTH // 2,
            SCREEN_WIDTH + (CONSOLE_HEIGHT - 2 * BUTTON_HEIGHT) // 3,
            BUTTON_WIDTH, BUTTON_HEIGHT)
        self.multiplayerButton = pygame.Rect(
            (SCREEN_WIDTH * 3) // 4 + PROMPT_BUTTON_SEP_WIDTH // 2 - BUTTON_WIDTH // 2,
            SCREEN_WIDTH + 2 * ((CONSOLE_HEIGHT - 2 * BUTTON_HEIGHT) // 3) + BUTTON_HEIGHT,
            BUTTON_WIDTH, BUTTON_HEIGHT)
        self.singleplayerText = pygame.font.SysFont('', 30).render('single player mode', 0, (0, 0, 0))
        self.multiplayerText = pygame.font.SysFont('', 30).render('multiplayer mode', 0, (0, 0, 0))

        self.boardBacks = [[
            # (0, 1, 2) X (0, 1, 2)
            pygame.Rect(PRM_SEP_WIDTH + i * (SUB_WIDTH + PRM_SEP_WIDTH),
                        PRM_SEP_WIDTH + j * (SUB_WIDTH + PRM_SEP_WIDTH),
                        SUB_WIDTH, SUB_WIDTH)
            for j in range(3)] for i in range(3)]

        self.prmSeperators = [
            # (0, 1) X (0, 1, 2, 3) primaries:
            [pygame.Rect(i * (PRM_SEP_WIDTH + SUB_WIDTH), 0,
                         PRM_SEP_WIDTH, SCREEN_WIDTH)
             for i in range(4)],
            [pygame.Rect(0, i * (PRM_SEP_WIDTH + SUB_WIDTH),
                         SCREEN_WIDTH, PRM_SEP_WIDTH)
             for i in range(4)]]

        self.secSeperators = [[[[
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

        self.boardSymbols = {
            'x' : pygame.font.SysFont('', 70).render('X', 0, (0, 0, 0)),
            'o' : pygame.font.SysFont('', 70).render('O', 0, (0, 0, 0))
        }

        self.consoleTexts = {
            'x-turn' : pygame.font.SysFont('', 50).render('X\'s move', 0, (0, 0, 0)),
            'o-turn' : pygame.font.SysFont('', 50).render('O\'s move', 0, (0, 0, 0)),
            'x-win' : pygame.font.SysFont('', 50).render('X has won', 0, (0, 0, 0)),
            'o-win' : pygame.font.SysFont('', 50).render('O has won', 0, (0, 0, 0)),
            'draw' : pygame.font.SysFont('', 50).render('stalemate', 0, (0, 0, 0))
        }

    def highlightRegion(self, screen, i, j):
        pygame.draw.rect(screen, (139, 255, 190), self.boardBacks[i][j])

    def _yieldPrmSeps(self):
        for i, j in itertools.product(range(2), range(4)):
            yield self.prmSeperators[i][j]
    def _yieldSecSeps(self):
        for i, j, k, l in itertools.product(range(3), range(3), range(2), range(2)):
            yield self.secSeperators[i][j][k][l]
    def layLines(self, screen):
        for line in self._yieldPrmSeps():
            pygame.draw.rect(screen, (255, 0, 0), line)
        for line in self._yieldSecSeps():
            pygame.draw.rect(screen, (0, 0, 255), line)

    def posToBox(self, pos):
        # validate:
        x, y = pos
        if not x in range(SCREEN_WIDTH) or y not in range(SCREEN_WIDTH):
            return False, None
        for line in itertools.chain(self._yieldPrmSeps(), self._yieldSecSeps()):
            if line.collidepoint(x, y):
                return False, None
        return True, (
            x // (PRM_SEP_WIDTH + SUB_WIDTH),
            y // (PRM_SEP_WIDTH + SUB_WIDTH),
            ((x - PRM_SEP_WIDTH) % (PRM_SEP_WIDTH + SUB_WIDTH)) // (SEC_SEP_WIDTH + BLOCK_WIDTH),
            ((y - PRM_SEP_WIDTH) % (PRM_SEP_WIDTH + SUB_WIDTH)) // (SEC_SEP_WIDTH + BLOCK_WIDTH))

    def _yieldBoardAndCoords(self, board):
        for i, j, k, l in itertools.product(range(3), range(3), range(3), range(3)):
            yield board[i][j][k][l], i, j, k, l

    def _boxIndexToCenterPos(self, i, j, k, l):
        x = PRM_SEP_WIDTH + i * (SUB_WIDTH + PRM_SEP_WIDTH) + \
            k * (BLOCK_WIDTH + SEC_SEP_WIDTH) + (BLOCK_WIDTH // 2)
        y = PRM_SEP_WIDTH + j * (SUB_WIDTH + PRM_SEP_WIDTH) + \
            l * (BLOCK_WIDTH + SEC_SEP_WIDTH) + (BLOCK_WIDTH // 2)
        return x, y

    def placeCharsFromBoard(self, screen, board):
        for char, i, j, k, l in self._yieldBoardAndCoords(board):
            if char == 'x' or char == 'o':
                width, height = self.boardSymbols[char].get_size()
                _x, _y = self._boxIndexToCenterPos(i, j, k, l)
                screen.blit(self.boardSymbols[char], (_x - width // 2, _y - height // 2))

    def _flipSurfaceCenteredAtCoords(self, screen, surface, x, y):
        width, height = surface.get_size()
        screen.blit(surface, (x - width // 2, y - height // 2))

    def printMove(self, screen, move):
        self._flipSurfaceCenteredAtCoords(
            screen, self.consoleTexts['x-turn' if move == X else 'o-turn'],
            SCREEN_WIDTH // 2, SCREEN_WIDTH + CONSOLE_HEIGHT // 2)

    def printStartPtompt(self, screen):
        pygame.draw.rect(screen, (82, 198, 255), self.singleplayerButton)
        pygame.draw.rect(screen, (255, 112, 68), self.multiplayerButton)

        self._flipSurfaceCenteredAtCoords(
            screen, self.startPromptText,
            (SCREEN_WIDTH - PROMPT_BUTTON_SEP_WIDTH) // 4 + PROMPT_BUTTON_SEP_WIDTH // 2,
            SCREEN_WIDTH + CONSOLE_HEIGHT // 2)

        self._flipSurfaceCenteredAtCoords(
            screen, self.singleplayerText,
            (SCREEN_WIDTH * 3) // 4 + PROMPT_BUTTON_SEP_WIDTH // 2,
            SCREEN_WIDTH + (CONSOLE_HEIGHT - 2 * BUTTON_HEIGHT) // 3 + BUTTON_HEIGHT // 2)

        self._flipSurfaceCenteredAtCoords(
            screen, self.multiplayerText,
            (SCREEN_WIDTH * 3) // 4 + PROMPT_BUTTON_SEP_WIDTH // 2,
            SCREEN_WIDTH + 2 * ((CONSOLE_HEIGHT - 2 * BUTTON_HEIGHT) // 3) + (3 * BUTTON_HEIGHT) // 2)

    def printGameEnd(self, screen, player = None):
        if player == None:
            key = 'draw'
        elif player == X:
            key = 'x-win'
        else:
            key = 'o-win'
        self._flipSurfaceCenteredAtCoords(
            screen, self.consoleTexts[key],
            SCREEN_WIDTH // 2, SCREEN_WIDTH + CONSOLE_HEIGHT // 2)

    def draw3inRowLine(self, screen, i, j, k1, l1, k2, l2):
        pygame.draw.line(screen, (0, 255, 0),
                         self._boxIndexToCenterPos(i, j, k1, l1),
                         self._boxIndexToCenterPos(i, j, k2, l2), 10)

def main():

    # ---- engine init:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('UltimateToe')
    clock = pygame.time.Clock()

    # ---- draw init:
    graph = GraphicsManager()

    # ---- logic init:
    board = [[[[
        # PRM ROW X PRM COL X SEC ROW X SEC COL
        None for l in range(3)] for k in range(3)]
        for j in range(3)] for i in range(3)]

    AI, boundedMove, coords = None, None, None

    move, turn, won = X, 0, False

    started, singlePlayer = False, False

    if noPlayer:
        started = True
        kwargs1 = {
            'side' : 2,
            'corner' : 1,
            'middle' : 1,
            'block2' : 1,
            'freesquare' : 1,
            'make2' : 4,
            'locksquare' : 4,
        }
        AI1 = baseAI.BaseAI(X, **kwargs1)
        kwargs2 = {
            'side' : 1,
            'corner' : 1,
            'middle' : 1,
            'block2' : 1.5,
            'freesquare' : 2,
            'make2' : 1.5,
            'locksquare' : 2,
        }
        AI2 = baseAI.BaseAI(O, **kwargs2)
        boundedMove = False

    # ---- game loop
    while turn < 81:

        # ---- input:
        validInput = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if started and (not singlePlayer or move == X):
                    print(event.pos)
                    validInput, coords = graph.posToBox(event.pos)
                    if validInput:
                        print('golden', coords)
                else:
                    if graph.singleplayerButton.collidepoint(event.pos):
                        singlePlayer = True
                        AI = baseAI.BaseAI(O)
                        started = True
                    elif graph.multiplayerButton.collidepoint(event.pos):
                        singlePlayer = False
                        started = True
                    boundedMove = False

        # ---- no play logic:
        if noPlayer:
            validInput = False
            if move == X:
                if boundedMove:
                    (i, j, k, l) = AI1.getMove(board, i = boundTile[0], j = boundTile[1])
                else:
                    (i, j, k, l) = AI1.getMove(board)
                board[i][j][k][l] = 'x'
            else:
                if boundedMove:
                    (i, j, k, l) = AI2.getMove(board, i = boundTile[0], j = boundTile[1])
                else:
                    (i, j, k, l) = AI2.getMove(board)
                board[i][j][k][l] = 'o'
            AI1.update(i, j, k, l, move)
            AI2.update(i, j, k, l, move)
            won, direct = checkWin(i, j, k, l, board)
            if won:
                break
            # check for minor-draw:
            boundedMove = True
            boundTile = k, l
            for x, y in itertools.product(range(3), range(3)):
                if not board[i][j][x][y]:
                    break
            else:
                boundedMove = False
            move, turn = (move + 1) % 2, turn + 1

        # ---- logic:
        if validInput:
            i, j, k, l = coords
            if (boundedMove and (i, j) != boundTile) or board[i][j][k][l]:
                validInput = False
        elif singlePlayer and move == O:
            if boundedMove:
                (i, j, k, l) = AI.getMove(board, i = boundTile[0], j = boundTile[1])
            else:
                (i, j, k, l) = AI.getMove(board)
            validInput = True

        if validInput:
            # we're in business
            board[i][j][k][l] = 'x' if move == X else 'o'
            if singlePlayer:
                AI.update(i, j, k, l, move)
            won, direct = checkWin(i, j, k, l, board)
            if won:
                break
            # check for minor-draw:
            boundedMove = True
            boundTile = k, l
            for x, y in itertools.product(range(3), range(3)):
                if not board[i][j][x][y]:
                    break
            else:
                boundedMove = False
            move, turn = (move + 1) % 2, turn + 1

        # ---- drawing:
        screen.fill((255, 255, 255))
        if started and boundedMove:
            graph.highlightRegion(screen, *boundTile)
        graph.layLines(screen)
        graph.placeCharsFromBoard(screen, board)
        if started:
            graph.printMove(screen, move)
        else:
            graph.printStartPtompt(screen)
        pygame.display.flip()

        # ---- iterate:
        clock.tick(15)

    # ---- final drawing:
    screen.fill((255, 255, 255))
    graph.layLines(screen)
    graph.placeCharsFromBoard(screen, board)
    if won:
        if direct == 'cross':
            start_x, start_y, end_x, end_y = 0, l, 2, l
        elif direct == 'down':
            start_x, start_y, end_x, end_y = k, 0, k, 2
        elif direct == 'neg':
            start_x, start_y, end_x, end_y = 0, 0, 2, 2
        else:
            start_x, start_y, end_x, end_y = 0, 2, 2, 0
        graph.draw3inRowLine(screen, i, j, start_x, start_y, end_x, end_y)
    graph.printGameEnd(screen, move if won else None)

    pygame.display.flip()

    # ---- game over
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        clock.tick(30)

if __name__ == '__main__':
    main()
