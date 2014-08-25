import itertools, copy
from constants import X, O

# boardstate offsets:
CROSS_OFFSET = 0
DOWN_OFFSET = 3
NEG_OFFSET = 6
POS_OFFSET = 7

defaultValues = {
    'side' : 2,
    'corner' : 3,
    'middle' : 4,
    'block2' : 1.5,
    'freesquare' : 1.5,
    'make2' : 1.5,
    'locksquare' : 1.5,
}

def coordToOffsets(k, l):
    load = []
    # down:
    load.append(DOWN_OFFSET + k)
    # cross:
    load.append(CROSS_OFFSET + l)
    # neg:
    if k == l:
        load.append(NEG_OFFSET)
    # pos:
    if k + l == 2:
        load.append(POS_OFFSET)
    return load

class BaseAI:

    def __init__(self, player, **kwargs):
        """ kwargs are custom valuations in the playValues dictionary """
        self.boardState = [
            # ROW(3) X COL(3) X DOWN(3), CROSS(3), NEG(1), POS(1) X (#x's, #o's)
            [[[0, 0] for k in range(8)] for j in range(3)] for i in range(3)]
        self.locks = [
            # ROW(3) X COL(3) X (#x's, #o's)
            [[False, False] for j in range(3)] for i in range(3)]
        self.totals = [
            # ROW(3) X COL(3) X (total)
            [0 for j in range(3)] for i in range(3)]
        self.player = player
        self.other = (player + 1) % 2

        self.playValues = copy.deepcopy(defaultValues)
        for key, customValue in kwargs.iteritems():
            self.playValues[key] = customValue
        # get win/lose:
        prod = 1
        for key, value in self.playValues.iteritems():
            prod *= value
        self.playValues['win'] = abs(prod)
        self.playValues['loss'] = - abs(prod)

    def coordToBaseVals(self, k, l):
        if k + l % 2 != 0:
            return self.playValues['side']
        elif k == l == 1:
            return self.playValues['middle']
        else:
            return self.playValues['corner']

    def getMove(self, board, i = None, j = None, retScore = False):
        if i == None or j == None:
            return self.unboundedMove(board)

        bestScore, bestMove = -1, None
        for k, l in itertools.product(range(3), range(3)):
            if not board[i][j][k][l]:
                # check for win, or lose:
                terminal = False
                for x in coordToOffsets(k, l):
                    if self.boardState[i][j][x][self.player] == 2:
                        return (i, j, k, l, self.playValues['win']) \
                            if retScore else (i, j, k, l)
                    if (i, j) != (k, l) and self.locks[k][l][self.other]:
                        terminal = True
                        break
                    elif (i, j) == (k, l):
                        for y, threat in enumerate(self.boardState[k][l]):
                            if threat[self.player] == 0 and threat[self.other] == 2 \
                                    and not y in coordToOffsets(k, l):
                                terminal = True
                                break
                    if self.totals[k][l] == 9:
                        terminal = True
                        break
                if terminal:
                    continue

                # evaluate play:
                score = self.coordToBaseVals(k, l)
                for x in coordToOffsets(k, l):
                    if self.boardState[i][j][x][self.player] == 1 and \
                                    self.boardState[i][j][x][self.other] == 0:
                        score *= self.playValues['make2']
                        if not self.locks[i][j][self.player]:
                            score *= self.playValues['locksquare']
                    if self.boardState[i][j][x][self.other] == 2:
                        score *= self.playValues['block2']
                        if self.locks[i][j][self.other]:
                            score *= self.playValues['freesquare']

                if score > bestScore:
                    bestMove, bestScore = (i, j, k, l), score

        if bestScore > -1:
            return (bestMove + (bestScore,)) if retScore else bestMove
        else: # find a loss play:
            for k, l in itertools.product(range(3), range(3)):
                if not board[i][j][k][l]:
                    return (i, j, k, l, self.playValues['loss']) \
                        if retScore else (i, j, k, l)
        # no plays:
        return None, -1 if retScore else None

    def unboundedMove(self, board):
        for i, j in itertools.product(range(3), range(3)):
            if self.locks[i][j][self.player]:
                for k, l in itertools.product(range(3), range(3)):
                    for x in coordToOffsets(k, l):
                        if self.boardState[i][j][x][self.player] == 2 \
                                and self.boardState[i][j][x][self.player] == 0:
                            return (i, j, k, l)
        if not board[1][1][1][1]:
            return (1, 1, 1, 1)
        bestScore, bestMove = -1, None
        for i, j in itertools.product(range(3), range(3)):
            if self.totals[i][j] < 9:
                move, score = self.getMove(board, i, j, True)
                if score > bestScore:
                    bestScore = score
                    bestMove = move
        return bestMove

    def update(self, i, j, k, l, player):
        self.totals[i][j] += 1
        for x in coordToOffsets(k, l):
            self.boardState[i][j][x][player] += 1

        for state in self.boardState[i][j]:
            if state[X] == 2 and state[O] == 0:
                self.locks[i][j][X] = True
                break
        else:
            self.locks[i][j][X] = False

        for state in self.boardState[i][j]:
            if state[O] == 2 and state[X] == 0:
                self.locks[i][j][O] = True
                break
        else:
            self.locks[i][j][O] = False
