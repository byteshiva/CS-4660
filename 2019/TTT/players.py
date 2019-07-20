from qTable import qTable
from random import choice
from typing import List, NoReturn, Optional, Set, Tuple
from utils import CENTER, CORNERS, LABELLEDBOARD, OMARK, SIDES, XMARK, \
    emptyCellsCount, formatBoard, isAvailable, marksAtTriple, possibleWinners, \
    oppositeCorner, otherMark, setMove, theWinner, validMoves, whoseMove

# A list of (board, move, reward, nextBoard) tuples for a game.
SarsList = List[Tuple[str, int, float, Optional[str]]]


# noinspection PyUnusedLocal
class Player:
    """
    The board is numbered as follows.
    0 1 2
    3 4 5
    6 7 8
    """

    def __init__(self, myMark: str) -> NoReturn:
        self.isATestGame = None
        self.myMark = myMark
        self.opMark = otherMark(myMark)
        # The previous board and move before being entered into the SarsList.
        self.prevBoardMove: Optional[Tuple[str, int]] = None
        self.sarsList: SarsList = []

        self.typeName = type(self).__name__

    def finalReward(self, reward: float) -> SarsList:
        """
        This is called after the game is over to inform the player of its final reward.
        :param reward: The final reward for the game.
        :return: SarsList
        """
        (board, move) = self.prevBoardMove
        self.sarsList.append((board, move, reward, None))
        return self.sarsList

    def makeAMove(self, reward: float, board: str, isATestGame: bool = True) -> int:
        """
        Called by the GameManager to get this player's move.
        :param reward: The reward from the previous move.
        :param board: The board after the previous move.
        :param isATestGame:
        :return: A move
        """
        self.isATestGame = isATestGame
        # self._makeAMove selects the move.
        move = self._makeAMove(board)
        self.updateSarsList(reward, board, move)
        return move

    def _makeAMove(self, board: str) -> int:
        """ Select and return a move. Overridden by subclasses. """
        # If not overridden, make a random valid move.
        move = choice(validMoves(board))
        return move

    def reset(self) -> NoReturn:
        self.prevBoardMove = None
        self.sarsList = []

    def updateSarsList(self, reward: float, curBoard: str, curMove: int) -> NoReturn:
        if self.prevBoardMove is not None:
            (board, move) = self.prevBoardMove
            self.sarsList.append((board, move, reward, curBoard))
        self.prevBoardMove = (curBoard, curMove)


class HumanPlayer(Player):

    def _makeAMove(self, board: str) -> int:
        c = '?'
        while c not in LABELLEDBOARD or not isAvailable(board, int(c)):
            print()
            if c in LABELLEDBOARD and not isAvailable(board, int(c)):
                print(f'Cell {c} is taken.')
            if c != '?' and c not in LABELLEDBOARD:
                print(f'Invalid move: "{c}".')
            print(formatBoard(board))
            # Keep only last character.
            c = input(f'{self.myMark} to move > ')
            c = c[-1] if len(c) > 0 else '?'
        move = int(c)
        return move


class LearningPlayer(Player):

    def _makeAMove(self, board: str) -> int:
        """
        Update qValues and select a move based on representative board from this board's equivalence class.
        Should not be random like the following.
        """
        # Either a random move or the move with the highest QValue for this state.
        move = qTable.getBestMove(board, self.typeName) if self.isATestGame else choice(validMoves(board))
        return move


class WinsBlocksForksPlayer(Player):

    def _makeAMove(self, board: str) -> int:
        (myWins, otherWins, myForks, otherForks) = self.winsBlocksForks(board)
        availCorners = [pos for pos in CORNERS if isAvailable(board, pos)]
        availCenter = [pos for pos in [CENTER] if isAvailable(board, pos)]
        availSides = [pos for pos in SIDES if isAvailable(board, pos)]
        myOppositeCorners = [pos for pos in CORNERS if
                             isAvailable(board, pos) and board[oppositeCorner(pos)] == self.myMark]
        move = choice([self.findEmptyCell(board, myWin) for myWin in myWins] if myWins else
                      [self.findEmptyCell(board, otherWin) for otherWin in otherWins] if otherWins else
                      myForks if myForks else
                      # If emptyCellsCount(board) == 6, I'm playing 'O'. If a diagonal is XOX, don't take corner.
                      availSides if board[CENTER] == self.myMark and emptyCellsCount(board) == 6 else
                      otherForks if otherForks else
                      availCorners if availCorners and self.myMark == 'X' and len(availCorners) % 2 == 0 else
                      availCenter if availCenter else
                      myOppositeCorners if board[CENTER] == self.opMark and myOppositeCorners else
                      availCorners if availCorners else
                      validMoves(board)
                      )
        return move

    @staticmethod
    def findEmptyCell(board: str, threeInRow: Tuple[int, int, int]) -> int:
        """
        Return a choice of the EMPTYCELL positions in threeInRow. (There is guaranteed to be one.)
        :param board:
        :param threeInRow:
        :return:
        """
        emptyCells = [index for index in threeInRow if isAvailable(board, index)]
        return choice(emptyCells)

    @staticmethod
    def findForks(board: str, singletons: List[Tuple[int, int, int]]) -> List[int]:
        """
        Finds moves that create forks
        :param board:
        :param singletons: A list of triples containing one non-empty cell for a given player.
        :return:
        """
        countSingletons = len(singletons)
        forkCells = {pos for idx1 in range(countSingletons - 1) for idx2 in range(idx1 + 1, countSingletons)
                     for pos in singletons[idx1] if isAvailable(board, pos) and pos in singletons[idx2]}
        return list(forkCells)

    def winsBlocksForks(self, board: str) -> Tuple[List[Tuple[int, int, int]],
                                                   List[Tuple[int, int, int]],
                                                   List[int],
                                                   List[int]
                                                   ]:
        myWins = []
        mySingletons = []
        otherWins = []
        otherSingletons = []
        empties = []
        myForks = []
        otherForks = []
        for threeInRow in possibleWinners:
            marks = marksAtTriple(board, threeInRow)
            emptyCellCount = marks.count('.')
            if emptyCellCount == 3:
                empties.append(threeInRow)
            if emptyCellCount == 1:
                if marks.count(self.myMark) == 2:
                    myWins.append(threeInRow)
                if marks.count(self.opMark) == 2:
                    otherWins.append(threeInRow)
            if emptyCellCount == 2:
                if marks.count(self.myMark) == 1:
                    mySingletons.append(threeInRow)
                if marks.count(self.opMark) == 1:
                    otherSingletons.append(threeInRow)
        if not myWins and not otherWins:
            if mySingletons:
                myForks = self.findForks(board, mySingletons)
            if otherSingletons:
                otherForks = self.findForks(board, otherSingletons)
        return (myWins, otherWins, myForks, otherForks)


class WinsBlocksPlayer(WinsBlocksForksPlayer):

    def _makeAMove(self, board: str) -> int:
        (myWins, otherWins, _, _) = self.winsBlocksForks(board)
        move = choice([self.findEmptyCell(board, myWin) for myWin in myWins] if myWins else
                      [self.findEmptyCell(board, otherWin) for otherWin in otherWins] if otherWins else
                      validMoves(board)
                      )
        return move


class HardWiredPlayer(WinsBlocksForksPlayer):
    """
    Plays as well as possible. Uses a hard-wired strategy.
    """

    def _makeAMove(self, board: str) -> int:
        """
        If this player can win, it will.
        If not, it blocks if the other player can win.
        Otherwise it makes a random valid move.
        :param board:
        :return: selected move
        """

        (myWins, otherWins, _, _) = self.winsBlocksForks(board)
        move = choice([self.findEmptyCell(board, myWin) for myWin in myWins] if myWins else
                      [self.findEmptyCell(board, otherWin) for otherWin in otherWins] if otherWins else
                      list(self.otherMove(board, emptyCellsCount(board)))
                      )
        return move

    @staticmethod
    def otherMove(board: str, emptyCells: int) -> Set[int]:
        """
        Special case moves.
        :param board:
        :param emptyCells: number of empty cells
        :return: Selected move
        """

        availableCorners = {pos for pos in CORNERS if isAvailable(board, pos)}
        if emptyCells == 9:
            return availableCorners
        if emptyCells == 8:
            return {CENTER} if isAvailable(board, CENTER) else availableCorners
        # The following is for X's second move. It applies only if X's first move was to a corner.
        if emptyCells == 7 and board.index(XMARK) in CORNERS:
            oFirstMove = board.index(OMARK)
            # If O's first move is a side cell, X should take the center.
            # Otherwise, X should take the corner opposite its first move.
            if oFirstMove in SIDES:
                return {CENTER}
            if oFirstMove == CENTER:
                opCorner = oppositeCorner(board.index(XMARK))
                return {opCorner}
            return availableCorners
        # If this is O's second move and X has diagonal corners, O should take a side move.
        # If X has two adjacent corners, O blocked (above). So, if there are 2 available corners
        # they are diagonal.
        if emptyCells == 6 and len(availableCorners) == 2:
            return {pos for pos in SIDES if isAvailable(board, pos)}
        # If none of the special cases apply, take the center if available,
        # otherwise a corner, otherwise any valid move.
        return ({CENTER} if isAvailable(board, CENTER) else
                availableCorners if availableCorners else
                validMoves(board)
                )


class MinimaxPlayer(HardWiredPlayer):

    def _makeAMove(self, board: str) -> int:
        # The first few moves are hard-wired into HardWiredPlayer.
        move = (super()._makeAMove(board) if emptyCellsCount(board) >= 7 else
                # minimax returns (val, move, count). Extract move.
                self.minimax(board)[1])
        return move
