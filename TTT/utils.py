from random import choice
from typing import Any, Dict, List, NoReturn, Optional, Tuple, Union

EMPTYCELL: str = '.'
NEWBOARD: str = EMPTYCELL * 9
LABELLEDBOARD = ''.join(map(str, range(9)))

XMARK: str = 'X'
OMARK: str = 'O'

"""
    The board is numbered as follows.
                0 1 2
                3 4 5
                6 7 8
"""

CENTER: int = 4
CORNERS: List[int] = [0, 2, 6, 8]
SIDES: List[int] = [1, 3, 5, 7]


def getColAt(pos: int) -> Tuple[int, int, int]:
    """
    Return a tuple of the indices for the column that includes pos.
    :param pos:
    :return:
    """
    colStart = pos % 3
    col = (colStart, colStart + 3, colStart + 6)
    return col


def getRowAt(pos: int) -> Tuple[int, int, int]:
    """
    Return a tuple of the indices for the row that includes pos.
    :param pos:
    :return:
    """
    rowStart = (pos // 3) * 3
    row = (rowStart, rowStart + 1, rowStart + 2)
    return row


majDiag = (0, 4, 8)
minDiag = (2, 4, 6)

# These are the eight three-element sequences that could make a win.
possibleWinners: List[Tuple[int, int, int]] = [majDiag, minDiag,
                                               getRowAt(0), getRowAt(3), getRowAt(6),
                                               getColAt(0), getColAt(1), getColAt(2)]


# Alpha is the learning rate. It declines with more games.
# Select the function for alpha, which is based on player, and return alpha for a given n (game number)
# noinspection PyShadowingNames
def alpha(pctTrained: float, playerMark: str) -> float:
    alpha_fn = {'X': lambda: min(0.5, pow(0.99, 250 * pctTrained)),
                'O': lambda: min(0.75, pow(0.99, 200 * pctTrained))}[playerMark]
    return alpha_fn()


def argmax(aDict: Dict) -> Any:
    bestKeys = argmaxList(aDict)
    return choice(bestKeys)


def argmaxList(aDict: Dict) -> [Any]:
    bestVal = max(aDict.values())
    bestKeys = [key for (key, val) in aDict.items() if val == bestVal]
    return bestKeys


def emptyCellsCount(board: str) -> int:
    # Do it this way rather than commit to a constant value empty cell
    return 9 - board.count('X') - board.count('O')


def formatBoard(board: str) -> str:
    # A Board showing unused cells and their labels
    labelledBoardList = [' ' if cell in 'XO' else label for (label, cell) in zip(LABELLEDBOARD, board)]
    labelledBoard = ''.join(labelledBoardList)
    # Get rows for both labelledBoard and Board
    labelledRows = make_rows(labelledBoard)
    boardRows = make_rows(board)
    # Combine the rows with a spacer between
    combinedRows = [labels + '     ' + row for (labels, row) in zip(labelledRows, boardRows)]
    boardString = '\n'.join(combinedRows)
    return boardString


# Gamma is the discount rate for future results.
def gamma(playerMark: str) -> float:
    return {'X': 0.9, 'O': 0.95}[playerMark]


def isAvailable(board: str, pos: int) -> bool:
    return board[pos] in NEWBOARD


def make_rows(board: str):
    row_separator = "---+---+---"
    return [make_row(board, 0), row_separator,
            make_row(board, 1), row_separator,
            make_row(board, 2)]


def make_row(board: str, row: int) -> str:
    """
    A row looks like this:
    _0_|_1_|_2_  (The _ stands for a blank space.)
    """
    return ' ' + ' | '.join(board[row * 3:(row + 1) * 3]) + ' '


def marksAtTriple(board: str, triple: Tuple[int, int, int]):
    return [board[i] for i in triple]


def oppositeCorner(pos: int) -> int:
    return {0: 8, 2: 6, 6: 2, 8: 0}[pos]


def otherMark(mark: str) -> str:
    return {'X': 'O', 'O': 'X'}[mark]


def render(board: str) -> NoReturn:
    print(formatBoard(board))


def roundDict(dct: Dict[Any, float]) -> Dict[Any, float]:
    """
    Round a dictionary's values to 2 decimal places.
    :param dct:
    :return:
    """
    roundedDict = {k: round(v, 2) for (k, v) in dct.items()}
    return roundedDict


def setMove(board: str, move: int, mark: str) -> str:
    """
    Puts mark at position move in board. Works even if move is (max) 8. board[9:] is ''
    Since strings are immutable, a copy is made.
    :param board:
    :param move:
    :param mark:
    :return: the updated board
    """
    return board[0:move] + mark + board[move + 1:]


def theWinner(board: str) -> Optional[str]:
    """
    Is there a winner? If so return its mark. Otherwise, return None.
    """
    for triple in possibleWinners:
        (mark, y, z) = marksAtTriple(board, triple)
        if mark in 'XO' and mark == y == z:
            return mark
    return None


def validMoves(board: str) -> List[int]:
    valids = [i for i in range(9) if isAvailable(board, i)]
    return valids


def weightedAvg(low: Union[float, int], weight: float, high: Union[float, int]) -> float:
    return (1 - weight) * low + weight * high


def whoseMove(board: str) -> str:
    return OMARK if board.count(XMARK) > board.count(OMARK) else XMARK
