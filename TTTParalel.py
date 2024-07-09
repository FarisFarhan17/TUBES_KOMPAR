from enum import Enum
import time
import random
import multiprocessing as mp

# Variabel untuk pemain, komputer, dan status kosong
PLAYER = 'X'
COMPUTER = 'O'
EMPTY = '_'
BOARD_SIZE = 5
NUMBER_OF_PLAYERS = 1
TRANSPOSITION_TABLE = {}

# Exception jika posisi tidak kosong
class NoneEmptyPosition(Exception):
    pass

# Exception jika posisi diluar range
class OutOfRange(Exception):
    pass

# Status permainan
class GameState(Enum):
    tie = 'Tie'  
    notEnd = 'notEnd'  
    o = 'O' 
    x = 'X'  

# Board Game
class Board:
    def __init__(self, size):
        self.mSize = size
        self.mBoard = [[EMPTY for x in range(size)] for y in range(size)]
        self.lastMove = None

    # Fungsi untuk mencetak board
    def print(self):
        for i in range(self.mSize):
            for j in range(self.mSize):
                if j < self.mSize-1:
                    print(self.mBoard[i][j], end='|')
                else:
                    print(self.mBoard[i][j], end='')
            print()

    # Fungsi untuk mendapatkan posisi papan dari indeks
    def getBoardPosition(self, position):
        column = position % self.mSize
        row = position // self.mSize
        return row, column

    def getLastMove(self):
        return self.lastMove

    def getRow(self, numberOfRow):
        return self.mBoard[numberOfRow]

    def getColumn(self, numberOFColumn):
        return [row[numberOFColumn] for row in self.mBoard]

    def getDiagonal(self):
        diagonal1 = [self.mBoard[i][i] for i in range(self.mSize)]
        diagonal2 = []
        j = 0
        for i in reversed(range(self.mSize)):
            diagonal2.append(self.mBoard[i][j])
            j += 1
        return diagonal1, diagonal2

    def getMainDiagonal(self):
        return [self.mBoard[i][i] for i in range(self.mSize)]

    def getSecondaryDiagonal(self):
        diagonal = []
        j = 0
        for i in reversed(range(self.mSize)):
            diagonal.append(self.mBoard[i][j])
            j += 1
        return diagonal

    def checkIfOnMainDiagonal(self, position):
        return position % (self.mSize + 1) == 0

    def checkIfOnSecondaryDiagonal(self, position):
        return position % (self.mSize - 1) == 0

    # Gambar X di papan
    def drawX(self, position):
        self.lastMove = position
        (row, column) = self.getBoardPosition(position)
        self.mBoard[row][column] = PLAYER

    def drawEmpty(self, position):
        (row, column) = self.getBoardPosition(position)
        self.mBoard[row][column] = EMPTY

    # Gambar O di papan
    def drawO(self, position):
        self.lastMove = position
        (row, column) = self.getBoardPosition(position)
        self.mBoard[row][column] = COMPUTER

    def checkIfRubricEmpty(self, position):
        (row, column) = self.getBoardPosition(position)
        return self.mBoard[row][column] == EMPTY

    
    def all_same(self, listToBeChecked, char):
        return all(x == char for x in listToBeChecked)

# Fungsi minimax untuk AI dengan menggunakan deep iteration 
def iterative_deepening(board, depth, alpha, beta):
    best_move = None
    for d in range(1, depth + 1):
        score, move = minimax(board, d, True, alpha, beta)
        if score == 10*(board.mSize + 1) or score == -10*(board.mSize + 1):
            return score, move
        if move is not None:
            best_move = move
    return score, best_move

# Fungsi minimax untuk AI
def minimax(board, depth, isMax, alpha, beta):
    board_key = str(board.mBoard)
    if board_key in TRANSPOSITION_TABLE:
        return TRANSPOSITION_TABLE[board_key]

    moves = [i for i in range(board.mSize ** 2) if board.checkIfRubricEmpty(i)]
    score = evaluate(board)
    position = None

    if not moves or depth == 0:
        gameResult = checkGameState(board)
        if gameResult == GameState.x:
            return -10**(board.mSize + 1), position
        elif gameResult == GameState.o:
            return 10**(board.mSize + 1), position
        elif gameResult == GameState.tie:
            return 0, position
        return score, position

    if isMax:
        best = -float('inf')
        for move in moves:
            board.drawO(move)
            score, _ = minimax(board, depth - 1, not isMax, alpha, beta)
            board.drawEmpty(move)
            if score > best:
                best = score
                position = move
            alpha = max(alpha, best)
            if beta <= alpha:
                break
    else:
        best = float('inf')
        for move in moves:
            board.drawX(move)
            score, _ = minimax(board, depth - 1, not isMax, alpha, beta)
            board.drawEmpty(move)
            if score < best:
                best = score
                position = move
            beta = min(beta, best)
            if beta <= alpha:
                break

    TRANSPOSITION_TABLE[board_key] = (best, position)
    return best, position

# Fungsi evaluasi untuk menghitung skor
def evaluate(board):
    score = 0
    for i in range(board.mSize):
        score += getScoreLine(board.getRow(i))
        score += getScoreLine(board.getColumn(i))

    diagonals = board.getDiagonal()
    for i in range(2):
        score += getScoreLine(diagonals[i])
    return score

# Fungsi untuk mendapatkan skor dari satu baris/kolom
def getScoreLine(line):
    score = 0
    oSum, xSum, emptySum = calculateLine(line)
    if xSum == 0 and oSum != 0:
        score += 10 ** (oSum - 1)
    if oSum == 0 and xSum != 0:
        score += -(10 ** (xSum - 1))
    return score

def calculateLine(line):
    oSum = line.count(COMPUTER)
    xSum = line.count(PLAYER)
    emptySum = line.count(EMPTY)
    return oSum, xSum, emptySum

# Cek status permainan
def checkGameState(board):
    if checkForWin(board, 0):
        return GameState.x

    if checkForWin(board, 1):
        return GameState.o

    if checkForTie(board):
        return GameState.tie

    return GameState.notEnd

# Cek apakah ada yang menang
def checkForWin(board, turn):
    char = PLAYER if turn % 2 == 0 else COMPUTER
    lastMove = board.getLastMove()
    row, col = board.getBoardPosition(lastMove)

    if board.all_same(board.getRow(row), char) or \
            board.all_same(board.getColumn(col), char):
        return True

    if board.checkIfOnMainDiagonal(lastMove):
        if board.all_same(board.getMainDiagonal(), char):
            return True

    if board.checkIfOnSecondaryDiagonal(lastMove):
        if board.all_same(board.getSecondaryDiagonal(), char):
            return True

    return False

# Cek apakah permainan berakhir seri
def checkForTie(board):
    for i in range(board.mSize ** 2):
        if board.checkIfRubricEmpty(i):
            return False
    return True

class Game:
    def __init__(self, numberOfPlayers, boardSize):
        self.mBoard = Board(boardSize)
        self.mBoardSize = boardSize
        self.mNumberOfPlayers = numberOfPlayers
        self.mNamesList = [' '] * numberOfPlayers
        self.mTurn = None
        self.mComputerFirstPosition = None
        self.coinFlip()
        self.mBestMove = 0

    # Penentuan giliran pertama
    def coinFlip(self):
        turn = random.choice(['computer', 'player'])
        if turn == 'computer':
            self.mComputerFirstPosition = random.randrange(self.mBoard.mSize ** 2)
            self.mTurn = 1
        else:
            self.mTurn = 0

    # Input nama player
    def getPlayersNames(self):
        counter = 1
        while counter <= self.mNumberOfPlayers:
            try:
                playerName = input('please enter the name of player' + str(counter))
                if not playerName:
                    raise ValueError("field cannot be empty, please enter name")
                if not playerName.isalpha():
                    raise ValueError("only letters are allowed")
                if playerName in self.mNamesList:
                    raise ValueError("name already chosen please choose different name")

                self.mNamesList[counter - 1] = playerName
                counter += 1
            except ValueError as e:
                print(e)
            except Exception:
                print("unknown error")

    # Fungsi untuk mendapatkan gerakan pemain
    def getPlayerMove(self):
        while True:
            try:
                playerMove = int(input(self.mNamesList[self.mTurn] + ' please select rubric'))
                if not (0 <= playerMove <= (self.mBoardSize ** 2 - 1)):
                    raise OutOfRange("Wrong position, please insert different position")
                if not self.mBoard.checkIfRubricEmpty(playerMove):
                    raise NoneEmptyPosition("Rubric is none empty, please insert different position")
                self.mBoard.drawX(playerMove)
                return
            except NoneEmptyPosition as e:
                print(e)
            except OutOfRange as e:
                print(e)
            except ValueError:
                print("Only numbers are allowed")
            except Exception:
                print("unknown error")

    # Fungsi untuk menghasilkan semua gerakan yang mungkin
    def generate(self):
        return [i for i in range(self.mBoardSize ** 2) if self.mBoard.checkIfRubricEmpty(i)]

    # Fungsi pencarian minimax dengan multiprocessing
    def minimaxSearch(self):
        # Mendapatkan semua gerakan yang mungkin
        moves = self.generate()
        # Membuat pool proses sebanyak jumlah CPU yang tersedia
        with mp.Pool(mp.cpu_count()) as pool:
            # Menjalankan evaluasi gerakan secara paralel
            results = pool.starmap(self.evaluateMove, [(move, 4) for move in moves])
        # Memilih gerakan dengan skor terbaik
        best_score, best_move = max(results)
        return best_move

    # Fungsi untuk mengevaluasi satu gerakan
    def evaluateMove(self, move, depth):
        # Menggambar O di posisi gerakan
        self.mBoard.drawO(move)
        # Menjalankan minimax untuk mendapatkan skor
        score, _ = minimax(self.mBoard, depth, False, -float('inf'), float('inf'))
        # Mengosongkan kembali posisi tersebut
        self.mBoard.drawEmpty(move)
        return score, move

    # Memulai permainan
    def start(self):
        self.getPlayersNames()
        while True:
            self.mBoard.print()
            self.mTurn %= 2
            if self.mTurn % 2 == 0:
                self.getPlayerMove()
            else:
                print('computer please select rubric')
                start_time = time.time()
                if self.mComputerFirstPosition is not None:
                    computerMove = self.mComputerFirstPosition
                    self.mComputerFirstPosition = None
                else:
                    computerMove = self.minimaxSearch()
                end_time = time.time()
                print(f"Computer's move took {end_time - start_time:.6f} seconds.")
                self.mBoard.drawO(computerMove)

            gameResult = checkGameState(self.mBoard)
            if gameResult != GameState.notEnd:
                self.mBoard.print()
                if gameResult == GameState.tie:
                    print('The game is a tie')
                else:
                    if self.mTurn % 2 == 0:
                        print(self.mNamesList[self.mTurn] + ' is the winner!')
                    else:
                        print('computer is the winner!')
                break
            self.mTurn += 1

if __name__ == "__main__":
    game = Game(NUMBER_OF_PLAYERS, BOARD_SIZE)
    game.start()
