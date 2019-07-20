from itertools import zip_longest
# noinspection PyUnresolvedReferences
from players import HardWiredPlayer, HumanPlayer, LearningPlayer, MinimaxPlayer, \
    Player, WinsBlocksPlayer, WinsBlocksForksPlayer
from typing import ClassVar, Dict, NoReturn, Optional, Union
from utils import NEWBOARD, XMARK, OMARK, \
    emptyCellsCount, formatBoard, isAvailable, render, setMove, theWinner, whoseMove

PlayerDict = Dict[str, Union[int, str, float, Player]]
# PlayerDict {player:playerObject, cachedReward:rewardFromPreviousMove, mark:XorO}
# See reset()


class GameManager:

    def __init__(self) -> None:

        self.XDict: Optional[PlayerDict] = None
        self.ODict: Optional[PlayerDict] = None

    def gameLoop(self, isATestGame: bool = True) -> (PlayerDict, str):
        board = NEWBOARD

        # X always makes the first move.
        currentPlayerDict: PlayerDict = self.XDict
        winnerDict: Optional[PlayerDict] = None
        done = False
        while not done:
            player: Player = currentPlayerDict['player']
            reward: int = currentPlayerDict['cachedReward']
            move: int = player.makeAMove(reward, board, isATestGame)
            (winnerDict, board) = self.step(board, move)
            done = winnerDict is not None or emptyCellsCount(board) == 0
            currentPlayerDict = self.otherDict(currentPlayerDict)

        # Tell the players the final reward for the game.
        currentPlayerDict['player'].finalReward(currentPlayerDict['cachedReward'])
        otherPlayerDict = self.otherDict(currentPlayerDict)
        otherPlayerDict['player'].finalReward(otherPlayerDict['cachedReward'])
        return (winnerDict, board)

    def otherDict(self, aPlayerDict: PlayerDict) -> PlayerDict:
        return self.ODict if aPlayerDict is self.XDict else self.XDict

    def playAGame(self, xPlayerClass: ClassVar, oPlayerClass: ClassVar, isATestGame: bool = True) -> (str, str):
        self.reset(xPlayerClass, oPlayerClass)
        (winnerDict, finalBoard) = self.gameLoop(isATestGame)
        result1 = f'{self.XDict["player"].typeName} (X) vs {self.ODict["player"].typeName} (O).\n'
        result2 = 'Tie game.' if winnerDict is None else f'{winnerDict["mark"]} ({winnerDict["player"].typeName}) wins.'
        result = result1 + result2
        if HumanPlayer in [type(self.XDict['player']), type(self.ODict['player'])]:
            print('\n\n' + result)
            render(finalBoard)
        # Print a replay if the games does not involve a HumanPlayer.
        if HumanPlayer not in {xPlayerClass, oPlayerClass}:
            self.printReplay(finalBoard, result)
        return (finalBoard, result)

    def printReplay(self, finalBoard: str, result: str) -> NoReturn:
        xMoves = self.XDict['player'].sarsList
        oMoves = self.ODict['player'].sarsList
        print(f'\n\nReplay: {self.XDict["player"].typeName} (X) vs {self.ODict["player"].typeName} (O)')
        # xMoves will be one longer than oMoves unless O wins. Make an extra oMove (None, None, None) if necessary.
        zippedMoves = list(zip_longest(xMoves, oMoves, fillvalue=(None, None, None, None)))
        for xoMoves in zippedMoves:
            ((xBoard, xMove, _, _), (oBoard, oMove, _, _)) = xoMoves
            # Don't print the initial empty board.
            print("" if xBoard == NEWBOARD else formatBoard(xBoard) + "\n", f'\nX -> {xMove}')
            if oBoard is not None:
                print(f'{formatBoard(oBoard)}\n\nO -> {oMove}')
        print(f'{formatBoard(finalBoard)}\n{result}')

    def reset(self, xPlayerClass: ClassVar, oPlayerClass: ClassVar) -> NoReturn:
        # Create the players
        xPlayer: Player = xPlayerClass(XMARK)
        oPlayer: Player = oPlayerClass(OMARK)
        self.XDict: PlayerDict = {'mark': XMARK, 'cachedReward': None, 'player': xPlayer}
        self.ODict: PlayerDict = {'mark': OMARK, 'cachedReward': None, 'player': oPlayer}
        xPlayer.reset()
        oPlayer.reset()

    def step(self, board: str, move: int) -> (Optional[PlayerDict], str):
        """
        Make the move and return (winnerDict, updatedBoard).
        If no winner, winnerDict will be None.
        :param board:
        :param move:
        :return: (winnerDict, updatedBoard)
        """
        currentPlayerDict: PlayerDict = self.XDict if whoseMove(board) is XMARK else self.ODict
        otherPlayerDict: PlayerDict = self.otherDict(currentPlayerDict)

        # The following are all game-ending cases.
        if not isAvailable(board, move):
            # Illegal move. currentPlayerDict loses.
            # Illegal moves should be blocked and should not occur.
            currentPlayerDict['cachedReward'] = -100
            otherPlayerDict['cachedReward'] = 100
            print(f'\n\nInvalid move by {currentPlayerDict["mark"]}: {move}.', end='')
            return (otherPlayerDict, board)

        updatedBoard = setMove(board, move, currentPlayerDict['mark'])
        if theWinner(updatedBoard):
            # The current player just won the game with its current move.
            currentPlayerDict['cachedReward'] = 100
            otherPlayerDict['cachedReward'] = -100
            return (currentPlayerDict, updatedBoard)

        if emptyCellsCount(updatedBoard) == 0:
            # The game is over. It's a tie.
            currentPlayerDict['cachedReward'] = 0
            otherPlayerDict['cachedReward'] = 0
            return (None, updatedBoard)

        # The game is not over.
        # Get a reward for extending the game.
        currentPlayerDict['cachedReward'] = 1
        return (None, updatedBoard)


if __name__ == '__main__':
    GameManager().playAGame(MinimaxPlayer, HumanPlayer)
