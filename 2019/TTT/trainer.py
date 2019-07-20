from gameManager import GameManager
from itertools import zip_longest
from matplotlib import pyplot as plt
# noinspection PyUnresolvedReferences
from players import (HardWiredPlayer, HumanPlayer, LearningPlayer, MinimaxPlayer,
                     Player, WinsBlocksPlayer, WinsBlocksCornersPlayer)
from qTable import qTable
from typing import ClassVar, Dict, List, Optional, NoReturn
from utils import XMARK, OMARK, NEWBOARD, alpha, formatBoard, gamma, weightedAvg


class Trainer(GameManager):

    def __init__(self, N: int = 5000, trainingSegments: int = 100) -> NoReturn:
        # Total number of games to play
        self.N = N
        # Which of the N games are we playing
        self.n = 0
        # The number of training games between test games
        self.trainingSegments = trainingSegments
        self.cycleLength = round(self.N / trainingSegments)
        super().__init__()

    def playAGame(self, xPlayerClass: ClassVar, oPlayerClass: ClassVar, isATestGame: bool = True) -> NoReturn:
        super().playAGame(xPlayerClass, oPlayerClass, isATestGame)
        self.updateFromSarsList(self.XDict['player'])
        self.updateFromSarsList(self.ODict['player'])

    def playATestGame(self,
                      xORoMark: str,
                      opponentClass: ClassVar,
                      scores: Dict[str, List[Optional[float, int]]],
                      XorO: Dict[str, Optional[str, float, Player]]) -> NoReturn:
        (XClass, OClass) = (LearningPlayer, opponentClass) if xORoMark == XMARK else (opponentClass, LearningPlayer)
        self.playAGame(XClass, OClass, isATestGame=True)
        scores['scores'].append(XorO['cachedReward'])
        scores['avgs'].append(weightedAvg(scores['avgs'][-1], 0.05, scores['scores'][-1]))

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

    def train(self) -> NoReturn:
        xScores = {'scores': [], 'avgs': [-100]}
        oScores = {'scores': [], 'avgs': [-100]}
        for segmentNbr in range(self.trainingSegments):
            for self.n in range(self.cycleLength):
                self.playAGame(LearningPlayer, WinsBlocksPlayer, isATestGame=False)
                self.playAGame(WinsBlocksPlayer, LearningPlayer, isATestGame=False)
                self.playAGame(WinsBlocksPlayer, LearningPlayer, isATestGame=False)
            self.playATestGame(XMARK, WinsBlocksPlayer, xScores, self.XDict)
            self.playATestGame(OMARK, WinsBlocksPlayer, oScores, self.ODict)
            print(f'{"=" * 80}')
            print(
                f'End of segment {segmentNbr + 1}.  {self.cycleLength * (segmentNbr + 1) * 3} training games played. ',
                end='')
            print(f'  {XMARK} avg: {round(xScores["avgs"][-1], 2)}  {OMARK} avg: {round(oScores["avgs"][-1], 2)}')
        print(f'{"=" * 80}\nEnd of training. Beginning of tournament.')
        print(f'{"=" * 80}')
        for _ in range(3):
            (finalBoard, result) = super().playAGame(LearningPlayer, WinsBlocksPlayer, isATestGame=True)
            self.printReplay(finalBoard, result)
            (finalBoard, result) = super().playAGame(WinsBlocksPlayer, LearningPlayer, isATestGame=True)
            self.printReplay(finalBoard, result)
        print(f'\n{"=" * 80}\nEnd of tournament.\n{"=" * 80}')
        qTable.printQTable()

        plt.plot(xScores["avgs"], 'b')
        plt.plot(oScores["avgs"], 'r')

        plt.title(f'Running averages - X/O ({int(round(xScores["avgs"][-1]))}/{int(round(oScores["avgs"][-1]))})')

        plt.show()
        self.playATestGame(XMARK, WinsBlocksCornersPlayer, xScores, self.XDict)
        self.playATestGame(XMARK, WinsBlocksCornersPlayer, xScores, self.XDict)
        self.playATestGame(XMARK, WinsBlocksCornersPlayer, xScores, self.XDict)

        #        Compute new value for Q[state][action]
        #        Qs = Q[s]
        #
        #        Qnext is the state to which Qs goes after taking move
        #        max_Qnext is the current estimate of the best possible result from Qnext
        #        Qsav is the current value of Q[s][a]
        #        Qsav' will be the updated value of Q[s][a]

        #        Transform the traditional formula to the alpha-weighted formula.
        #        Qsav' += alpha * (reward + gamma * max_Qnext - Qsav)  -- Traditional formula
        #        Qsav' =  Qsav + alpha * (reward + gamma * max_Qnext - Qsav)
        #        Qsav' =  Qsav + alpha * (reward + gamma * max_Qnext) - alpha * Qsav
        #        Formula in terms of weights.
        #        Qsav' =  (1 - alpha) * Qsav  +  alpha * (reward + gamma * max_Qnext)

    def update(self,
               typeName: str,
               mark: str,
               board: str,
               move: int,
               reward: float,
               nextBoard: Optional[str]) -> NoReturn:
        # When done, there is no next state.
        assert reward is not None, f'reward: {reward}; nextBoard: {nextBoard}'
        done = nextBoard is None
        nextStateBestQValue = 0 if done else qTable.getBestQValue(nextBoard, typeName)
        newQValue = reward + gamma(mark) * nextStateBestQValue
        assert newQValue <= 100, f'nextBoard: {nextBoard}; reward: {reward}; nextStateBestQValue: {nextStateBestQValue}'
        qTable.updateQValue(board, typeName, move, alpha(self.n / self.N, mark), newQValue)

    def updateFromSarsList(self, player: Player) -> NoReturn:
        typeName = player.typeName
        mark = player.myMark
        for (board, move, reward, nextBoard) in reversed(player.sarsList):
            self.update(typeName, mark, board, move, reward, nextBoard)


if __name__ == '__main__':
    Trainer().train()
    # qTable.printQTable()
    # Trainer().playAGame(LearningPlayer, HumanPlayer, isATestGame=False)
    # Trainer().playAGame(LearningPlayer, HumanPlayer, isATestGame=False)
    # qTable.printQTable()
    # Trainer().playAGame(HumanPlayer, LearningPlayer, isATestGame=False)
    # qTable.printQTable()
