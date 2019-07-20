from collections import defaultdict
from functools import lru_cache
from random import choice
from typing import Dict, List, NoReturn, Tuple
from utils import NEWBOARD, \
    argmaxList, emptyCellsCount, formatBoard, isAvailable, roundDict, setMove, weightedAvg, whoseMove


class QTable:
    """
    This class represents boards that can be associated with equivalence classes of boards.
    The equivalence class of a board are all the boards it can transform into by rotations and flips.
    """

    def __init__(self) -> NoReturn:
        """
        Boards are numbered as follows.

            0 1 2
            3 4 5
            6 7 8

        The rotate pattern puts: the item originally in cell 6 into cell 0
                                 the item originally in cell 3 into cell 1
                                 the item originally in cell 0 into cell 2
                                 etc.
        In other words, it rotates the board 90 degrees clockwise.
        The flip pattern flips the board horizontally about its center column.
        See transformAux() to see these patterns in action.

        0 to 3 rotates and  0 or 1 flip generates all the equivalent boards.
        See representative() to see how all the equivalent boards are generated.
        """

        # self.rotatePattern = [6, 3, 0,
        #                       7, 4, 1,
        #                       8, 5, 2]
        self.rotatePattern = ('630' +
                              '741' +
                              '852')
        # self.flipPattern = [2, 1, 0,
        #                     5, 4, 3,
        #                     8, 7, 6]
        self.flipPattern = ('210' +
                            '543' +
                            '876')

        # The initial q-values of each Q[state]: {0:0, 1:0, ... , 8:0}
        # Don't access this directly. For each new state, make a copy.
        self._i_state = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}

        # The Q states. They are added as encountered.
        # For each state, there is a dictionary of typeNames.
        # Each is a dictionary of moves and their q-values. See self._i_state.
        self.qTable = defaultdict(lambda: defaultdict(lambda: self._i_state.copy()))

    # ============================================================================
    # The following methods require both the board and the typename of the requester.
    # These are the external interface to the QTable.
    def getBestMove(self, board: str, typeName: str) -> int:
        (qBoard, r, f) = self.getQBoardWithRF(board)
        bestQMoves = self.getBestQMovesFromQBoard(qBoard, typeName)
        bestQMove = choice(bestQMoves)
        bestMove = self.reverseTransformMove(bestQMove, r, f)
        return bestMove

    def getBestQMovesFromQBoard(self, qBoard: str, typeName: str) -> List[int]:
        qValues = self.qTable[qBoard][typeName]
        availableQValues = {i: val for (i, val) in qValues.items() if isAvailable(qBoard, i)}
        bestQMoves = argmaxList(availableQValues)
        return bestQMoves

    def getBestQValue(self, board: str, typeName: str) -> float:
        bestQValue = max(self.getQValueDict(board, typeName).values())
        return bestQValue

    def getQValueDict(self, board: str, typeName: str) -> Dict[int, float]:
        qBoard = self.getQBoard(board)
        qValueDict = self.qTable[qBoard][typeName]
        return qValueDict

    def updateQValue(self, board: str, typeName: str, move: int, alpha: float, newQValue: float) -> NoReturn:
        # qBoard = self.getQBoard(board)
        qValueDict = self.getQValueDict(board, typeName)
        qMove = self.getQMove(board, move)
        # print(f'\n\nBefore: board: {board} qBoard: {qBoard} move: {qMove} newQValue: {newQValue} qValues: {qValues}')
        qValueDict[qMove] = weightedAvg(qValueDict[qMove], alpha, newQValue)

    # =================================================================================
    # The following methods transform a board or move to their q-version equivalents
    # These are also available to external users.
    def getQBoard(self, board: str) -> str:
        (qBoard, _, _) = self.getQBoardWithRF(board)
        return qBoard

    @lru_cache(maxsize=None)
    def getQBoardWithRF(self, board: str) -> Tuple[str, int, int]:
        """
        Generate the equivalence class of boards and select the lexicographically smallest.
        :param board:
        :return: (board, rotations, flips); rotations will be in range(4); flips will be in range(2)
                 The rotations and flips are returned so that they can be undone later.
        """
        sortedTransformation = sorted([(self.transform(board, r, f), r, f) for r in range(4) for f in range(2)])
        return sortedTransformation[0]

    def getQMove(self, board: str, move: int) -> int:
        (_, r, f) = self.getQBoardWithRF(board)
        tempBoard = setMove(NEWBOARD, move, 'M')
        qTempBoard = self.transform(tempBoard, r, f)
        qMove = qTempBoard.index('M')
        return qMove

    # =================================================================================
    # Print the Q Table
    def printQTable(self) -> NoReturn:
        print(f'\n\nQTable contains {len(self.qTable)} entries.')
        for (qBoard, qValuesDicts) in sorted(self.qTable.items(), key=lambda bv: 9 - emptyCellsCount(bv[0])):
            self.printQValuesForPattern(qBoard, qValuesDicts)

    @staticmethod
    def printQValuesForPattern(qBoard: str, qValuesDicts: Dict[str, Dict[int, float]]) -> NoReturn:
        print(f'\n{formatBoard(qBoard)}')
        print(f'{whoseMove(qBoard)} to move')
        for (typeName, qValueDict) in sorted(qValuesDicts.items()):
            availableQValues = {i: val for (i, val) in qValueDict.items() if isAvailable(qBoard, i)}
            bestQMoves = argmaxList(availableQValues)
            print(f'{f"{typeName}" + ": ":<25}{roundDict(availableQValues)}. Best moves: {bestQMoves}')

    # =================================================================================
    # The following methods transform a board to its equivalent -- or back.
    @staticmethod
    @lru_cache(maxsize=None)
    def applyPattern(board: str, pattern: str) -> str:
        return ''.join([board[int(i)] for i in pattern])

    def restore(self, board: str, r: int, f: int) -> str:
        """
        Unflip and then unrotate the board
        :param board:
        :param r:
        :param f:
        :return:
        """
        # unflipping is the same as flipping a second time.
        unflipped = self.transformAux(board, self.flipPattern, f)
        # unrotating is the same as rotating 4 - r times.
        unrotateedAndFlipped = self.transformAux(unflipped, self.rotatePattern, 4 - r)
        return unrotateedAndFlipped

    def reverseTransformMove(self, move: int, r: int, f: int) -> int:
        """
        Unflip and then unrotate the move position.
        :param move:
        :param r:
        :param f:
        :return:
        """
        board = NEWBOARD
        # board[move] = 'M'
        updatedBoard = setMove(board, move, 'M')
        restoredBoard = self.restore(updatedBoard, r, f)
        nOrig = restoredBoard.index('M')
        return nOrig

    @lru_cache(maxsize=None)
    def transform(self, board: str, r: int, f: int) -> str:
        """
        Perform r rotations and then f flips on the board
        :param board:
        :param r: number of rotations
        :param f: number of flips
        :return: the rotated and flipped board
        """
        rotated = self.transformAux(board, self.rotatePattern, r)
        rotatedAndFlipped = self.transformAux(rotated, self.flipPattern, f)
        return rotatedAndFlipped

    def transformAux(self, board: str, pattern: str, n: int) -> str:
        """
        Rotate or flip the board (according to the pattern) n times.
        :param board:
        :param pattern:
        :param n:
        :return: the transformed board
        """
        # Recursive version
        # board if n == 0 else self.transformAux(self.applyPattern(board, pattern), pattern, n - 1)

        # "Pythonic" version. Uses a mutable variable.
        transformedBoard = board
        for _ in range(n):
            transformedBoard = self.applyPattern(transformedBoard, pattern)
        return transformedBoard


qTable = QTable()

if __name__ == '__main__':
    # Test the board transformer.
    # from gameManager import GameManager
    # from players import Player

    def render(caption: str, bd: str) -> NoReturn:
        print(f'\n{caption}\n{formatBoard(bd)}')


    qTable = QTable()

    b = ''.join([str(i) for i in range(9)])
    render("b", b)

    b10 = qTable.transform(b, 1, 0)
    render("b10 = transform(b, 1, 0)", b10)
    render("restore(b10, 1, 0)", qTable.restore(b10, 1, 0))

    b21 = qTable.transform(b, 2, 1)
    render("b21 = transform(b, 2, 1)", b21)
    render("restore(b21, 2, 1)", qTable.restore(b21, 2, 1))
