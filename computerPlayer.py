# ---- constants:
X, O = 0, 1

# boardState offsets
CROSS_OFFSET = 0
DOWN_OFFSET = 3
NEG_OFFSET = 6
POS_OFFSET = 7

# ---- main class:
class AI:
    """ computer player """
    placeValues = {
        'side' : 2,
        'corner' : 3,
        'middle' : 4,
        'block2' : 2,
        'make2' : 2
    }

    # ---- constructor:
    def __init__(self, player):
        self.boardState = [
            # ROW(3) X COL(3) X DOWN(3), CROSS(3), NEG(1), POS(1) X #x's, #o's
            [[[0, 0] for k in range(8)] for j in range(3)] for i in range(3)]
        if player == 'x':
            self.player = X
            self.other = O
        else:
            self.player = O
            self.other = X

    # ---- macros:
    def coordToPlayVals(self, k, l):
        if k + l % 2 != 0:
            return self.placeValues['side']
        elif k == l == 1:
            return self.placeValues['middle']
        else:
            return self.placeValues['corner']

    def coordToOffsets(self, k, l):
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


    # ---- main player:
    def playMove(self, i, j, board):

        bestScore, bestMove = -1, None
        for k in range(3):
            for l in range(3):
                if not board[i][j][k][l]:
                    # check for win, or lose:
                    terminal = False
                    for x in self.coordToOffsets(k, l):
                        if self.boardState[i][j][x][self.player] == 2:
                            return (k, l)
                        for threat in self.boardState[k][l]:
                            if threat[self.player] == 0 and threat[self.other] == 2:
                                terminal = True
                                break
                    if terminal:
                        continue

                    # evaluate play:
                    score = self.coordToPlayVals(k, l)
                    for x in self.coordToOffsets(k, l):
                        if self.boardState[i][j][x][self.player] == 1 and \
                                        self.boardState[i][j][x][self.other] == 0:
                            score *= self.placeValues['make2']
                        if self.boardState[i][j][x][self.other] == 2:
                            score *= self.placeValues['block2']

                    if score > bestScore:
                        bestScore, bestMove = score, (k, l)

        if bestScore > -1:
            return bestMove
        else:
            for k in range(3):
                for l in range(3):
                    if not board[i][j][k][l]:
                        return (k, l)

    # ---- turnly updater. player is boolean denoting if is AI or the other guy
    def update(self, i, j, k, l, player):
        for x in self.coordToOffsets(k, l):
            self.boardState[i][j][x][self.player if player else self.other] += 1