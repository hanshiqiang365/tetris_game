#author: hanshiqiang365 （微信公众号）
import sys
import random
import copy,math
import pygame
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal, QUrl
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication, QHBoxLayout, QLabel, QFrame
from PyQt5.QtGui import QColor, QPainter, QPalette, QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

class tetrisShape():
	def __init__(self, shape=0):
		self.shape_empty = 0
		self.shape_I = 1
		self.shape_L = 2
		self.shape_J = 3
		self.shape_T = 4
		self.shape_O = 5
		self.shape_S = 6
		self.shape_Z = 7
		self.shapes_relative_coords = [
                        [[0, 0], [0, 0], [0, 0], [0, 0]],
                        [[0, -1], [0, 0], [0, 1], [0, 2]],
                        [[0, -1], [0, 0], [0, 1], [1, 1]],
                        [[0, -1], [0, 0], [0, 1], [-1, 1]],
                        [[0, -1], [0, 0], [0, 1], [1, 0]],
                        [[0, 0], [0, -1], [1, 0], [1, -1]],
                        [[0, 0], [0, -1], [-1, 0], [1, -1]],
                        [[0, 0], [0, -1], [1, 0], [-1, -1]]
                        ]
		self.shape = shape
		self.relative_coords = self.shapes_relative_coords[self.shape]
		
	def getRotatedRelativeCoords(self, direction):
		if direction == 0 or self.shape == self.shape_O:
			return self.relative_coords

		if direction == 1:
			return [[-y, x] for x, y in self.relative_coords]

		if direction == 2:
			if self.shape in [self.shape_I, self.shape_Z, self.shape_S]:
				return self.relative_coords
			else:
				return [[-x, -y] for x, y in self.relative_coords]

		if direction == 3:
			if self.shape in [self.shape_I, self.shape_Z, self.shape_S]:
				return [[-y, x] for x, y in self.relative_coords]
			else:
				return [[y, -x] for x, y in self.relative_coords]

	def getAbsoluteCoords(self, direction, x, y):
		return [[x+i, y+j] for i, j in self.getRotatedRelativeCoords(direction)]

	def getRelativeBoundary(self, direction):
		relative_coords_now = self.getRotatedRelativeCoords(direction)
		xs = [i[0] for i in relative_coords_now]
		ys = [i[1] for i in relative_coords_now]
		return min(xs), max(xs), min(ys), max(ys)

class InnerBoard():
	def __init__(self, width=10, height=22):
		self.width = width
		self.height = height
		self.reset()

	def ableMove(self, coord, direction=None):
		assert len(coord) == 2
		if direction is None:
			direction = self.current_direction
		for x, y in self.current_tetris.getAbsoluteCoords(direction, coord[0], coord[1]):
			if x >= self.width or x < 0 or y >= self.height or y < 0:
				return False
			if self.getCoordValue([x, y]) > 0:
				return False
		return True

	def moveRight(self):
		if self.ableMove([self.current_coord[0]+1, self.current_coord[1]]):
			self.current_coord[0] += 1
	def moveLeft(self):
		if self.ableMove([self.current_coord[0]-1, self.current_coord[1]]):
			self.current_coord[0] -= 1
	def rotateClockwise(self):
		if self.ableMove(self.current_coord, (self.current_direction-1) % 4):
			self.current_direction = (self.current_direction-1) % 4
	def rotateAnticlockwise(self):
		if self.ableMove(self.current_coord, (self.current_direction+1) % 4):
			self.current_direction = (self.current_direction+1) % 4
	def moveDown(self):
		removed_lines = 0
		if self.ableMove([self.current_coord[0], self.current_coord[1]+1]):
			self.current_coord[1] += 1
		else:
			x_min, x_max, y_min, y_max = self.current_tetris.getRelativeBoundary(self.current_direction)
			if self.current_coord[1] + y_min < 0:
				self.is_gameover = True
				return removed_lines
			self.mergeTetris()
			removed_lines = self.removeFullLines()
			self.createNewTetris()
		return removed_lines
	
	def dropDown(self):
		while self.ableMove([self.current_coord[0], self.current_coord[1]+1]):
			self.current_coord[1] += 1
		x_min, x_max, y_min, y_max = self.current_tetris.getRelativeBoundary(self.current_direction)

		if self.current_coord[1] + y_min < 0:
			self.is_gameover = True
			return removed_lines
		self.mergeTetris()
		removed_lines = self.removeFullLines()
		self.createNewTetris()
		return removed_lines

	def mergeTetris(self):
		for x, y in self.current_tetris.getAbsoluteCoords(self.current_direction, self.current_coord[0], self.current_coord[1]):
			self.board_data[x + y * self.width] = self.current_tetris.shape
		self.current_coord = [-1, -1]
		self.current_direction = 0
		self.current_tetris = tetrisShape()

	def removeFullLines(self):
		new_board_data = [0] * self.width * self.height
		new_y = self.height - 1
		removed_lines = 0
		for y in range(self.height-1, -1, -1):
			cell_count = sum([1 if self.board_data[x + y * self.width] > 0 else 0 for x in range(self.width)])
			if cell_count < self.width:
				for x in range(self.width):
					new_board_data[x + new_y * self.width] = self.board_data[x + y * self.width]
				new_y -= 1
			else:
				removed_lines += 1
		self.board_data = new_board_data
		return removed_lines

	def createNewTetris(self):
		x_min, x_max, y_min, y_max = self.next_tetris.getRelativeBoundary(0)

		if self.ableMove([self.init_x, -y_min]):
			self.current_coord = [self.init_x, -y_min]
			self.current_tetris = self.next_tetris
			self.next_tetris = self.getNextTetris()
		else:
			self.is_gameover = True
		self.shape_statistics[self.current_tetris.shape] += 1

	def getNextTetris(self):
		return tetrisShape(random.randint(1, 7))

	def getBoardData(self):
		return self.board_data

	def getCoordValue(self, coord):
		return self.board_data[coord[0] + coord[1] * self.width]

	def getCurrentTetrisCoords(self):
		return self.current_tetris.getAbsoluteCoords(self.current_direction, self.current_coord[0], self.current_coord[1])

	def reset(self):
		self.board_data = [0] * self.width * self.height
		self.current_direction = 0
		self.current_coord = [-1, -1]
		self.next_tetris = self.getNextTetris()
		self.current_tetris = tetrisShape()
		self.is_gameover = False
		self.init_x = self.width // 2
		self.shape_statistics = [0] * 8

class ExternalBoard(QFrame):
	score_signal = pyqtSignal(str)
	def __init__(self, parent, grid_size, inner_board):
		super().__init__(parent)
		self.grid_size = grid_size
		self.inner_board = inner_board
		self.setFixedSize(grid_size * inner_board.width, grid_size * inner_board.height)
		self.initExternalBoard()

	def initExternalBoard(self):
		self.score = 0

	def paintEvent(self, event):
		painter = QPainter(self)
		for x in range(self.inner_board.width):
			for y in range(self.inner_board.height):
				shape = self.inner_board.getCoordValue([x, y])
				drawCell(painter, x * self.grid_size, y * self.grid_size, shape, self.grid_size)
		for x, y in self.inner_board.getCurrentTetrisCoords():
			shape = self.inner_board.current_tetris.shape
			drawCell(painter, x * self.grid_size, y * self.grid_size, shape, self.grid_size)
		painter.setPen(QColor(0x777777))
		painter.drawLine(0, self.height()-1, self.width(), self.height()-1)
		painter.drawLine(self.width()-1, 0, self.width()-1, self.height())
		painter.setPen(QColor(0xCCCCCC))
		painter.drawLine(self.width(), 0, self.width(), self.height())
		painter.drawLine(0, self.height(), self.width(), self.height())

	def updateData(self):
		self.score_signal.emit(f'Score：{self.score * 10}')
		self.update()

class SidePanel(QFrame):
	def __init__(self, parent, grid_size, inner_board):
		super().__init__(parent)
		self.grid_size = grid_size
		self.inner_board = inner_board
		self.setFixedSize(grid_size * 5, grid_size * inner_board.height)
		self.move(grid_size * inner_board.width, 0)

	def paintEvent(self, event):
		painter = QPainter(self)
		x_min, x_max, y_min, y_max = self.inner_board.next_tetris.getRelativeBoundary(0)
		dy = 3 * self.grid_size
		dx = (self.width() - (x_max - x_min) * self.grid_size) / 2
		shape = self.inner_board.next_tetris.shape
		for x, y in self.inner_board.next_tetris.getAbsoluteCoords(0, 0, -y_min):
			drawCell(painter, x * self.grid_size + dx, y * self.grid_size + dy, shape, self.grid_size)
			
	def updateData(self):
		self.update()


def drawCell(painter, x, y, shape, grid_size):
	colors = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC, 0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]
	if shape == 0:
		return
	color = QColor(colors[shape])
	painter.fillRect(x+1, y+1, grid_size-2, grid_size-2, color)
	painter.setPen(color.lighter())
	painter.drawLine(x, y+grid_size-1, x, y)
	painter.drawLine(x, y, x+grid_size-1, y)
	painter.setPen(color.darker())
	painter.drawLine(x+1, y+grid_size-1, x+grid_size-1, y+grid_size-1)
	painter.drawLine(x+grid_size-1, y+grid_size-1, x+grid_size-1, y+1)


class TetrisAI():
	def __init__(self, inner_board):
		self.inner_board = inner_board

	def getNextAction(self):
		if self.inner_board.current_tetris == tetrisShape().shape_empty:
			return None
		action = None

		if self.inner_board.current_tetris.shape in [tetrisShape().shape_O]:
			current_direction_range = [0]
		elif self.inner_board.current_tetris.shape in [tetrisShape().shape_I, tetrisShape().shape_Z, tetrisShape().shape_S]:
			current_direction_range = [0, 1]
		else:
			current_direction_range = [0, 1, 2, 3]

		if self.inner_board.next_tetris.shape in [tetrisShape().shape_O]:
			next_direction_range = [0]
		elif self.inner_board.next_tetris.shape in [tetrisShape().shape_I, tetrisShape().shape_Z, tetrisShape().shape_S]:
			next_direction_range = [0, 1]
		else:
			next_direction_range = [0, 1, 2, 3]

		for d_now in current_direction_range:
			x_now_min, x_now_max, y_now_min, y_now_max = self.inner_board.current_tetris.getRelativeBoundary(d_now)
			for x_now in range(-x_now_min, self.inner_board.width - x_now_max):
				board = self.getFinalBoardData(d_now, x_now)
				for d_next in next_direction_range:
					x_next_min, x_next_max, y_next_min, y_next_max = self.inner_board.next_tetris.getRelativeBoundary(d_next)
					distances = self.getDropDistances(board, d_next, range(-x_next_min, self.inner_board.width-x_next_max))
					for x_next in range(-x_next_min, self.inner_board.width-x_next_max):
						score = self.calcScore(copy.deepcopy(board), d_next, x_next, distances)
						if not action or action[2] < score:
							action = [d_now, x_now, score]
		return action

	def getFinalBoardData(self, d_now, x_now):
		board = copy.deepcopy(self.inner_board.getBoardData())
		dy = self.inner_board.height - 1
		for x, y in self.inner_board.current_tetris.getAbsoluteCoords(d_now, x_now, 0):
			count = 0
			while (count + y < self.inner_board.height) and (count + y < 0 or board[x + (count + y) * self.inner_board.width] == tetrisShape().shape_empty):
				count += 1
			count -= 1
			if dy > count:
				dy = count
		return self.imitateDropDown(board, self.inner_board.current_tetris, d_now, x_now, dy)

	def imitateDropDown(self, board, tetris, direction, x_imitate, dy):
		for x, y in tetris.getAbsoluteCoords(direction, x_imitate, 0):
			board[x + (y + dy) * self.inner_board.width] = tetris.shape
		return board

	def getDropDistances(self, board, direction, x_range):
		dists = {}
		for x_next in x_range:
			if x_next not in dists:
				dists[x_next] = self.inner_board.height - 1
			for x, y in self.inner_board.next_tetris.getAbsoluteCoords(direction, x_next, 0):
				count = 0
				while (count + y < self.inner_board.height) and (count + y < 0 or board[x + (count + y) * self.inner_board.width] == tetrisShape().shape_empty):
					count += 1
				count -= 1
				if dists[x_next] > count:
					dists[x_next] = count
		return dists

	def calcScore(self, board, d_next, x_next, distances):
		board = self.imitateDropDown(board, self.inner_board.next_tetris, d_next, x_next, distances[x_next])
		width, height = self.inner_board.width, self.inner_board.height
		removed_lines = 0
		hole_statistic_0 = [0] * width
		hole_statistic_1 = [0] * width
		num_blocks = 0
		num_holes = 0
		roof_y = [0] * width
		for y in range(height-1, -1, -1):
			has_hole = False
			has_block = False
			for x in range(width):
				if board[x + y * width] == tetrisShape().shape_empty:
					has_hole = True
					hole_statistic_0[x] += 1
				else:
					has_block = True
					roof_y[x] = height - y
					if hole_statistic_0[x] > 0:
						hole_statistic_1[x] += hole_statistic_0[x]
						hole_statistic_0[x] = 0
					if hole_statistic_1[x] > 0:
						num_blocks += 1
			if not has_block:
				break
			if not has_hole and has_block:
				removed_lines += 1

		num_holes = sum([i ** .7 for i in hole_statistic_1])
		max_height = max(roof_y) - removed_lines
		roof_dy = [roof_y[i]-roof_y[i+1] for i in range(len(roof_y)-1)]

		if len(roof_y) <= 0:
			roof_y_std = 0
		else:
			roof_y_std = math.sqrt(sum([y**2 for y in roof_y]) / len(roof_y) - (sum(roof_y) / len(roof_y)) ** 2)
		if len(roof_dy) <= 0:
			roof_dy_std = 0
		else:
			roof_dy_std = math.sqrt(sum([dy**2 for dy in roof_dy]) / len(roof_dy) - (sum(roof_dy) / len(roof_dy)) ** 2)

		abs_dy = sum([abs(dy) for dy in roof_dy])
		max_dy = max(roof_y) - min(roof_y)
		score = removed_lines * 1.8 - num_holes * 1.0 - num_blocks * 0.5 - max_height ** 1.5 * 0.02 - roof_y_std * 1e-5 - roof_dy_std * 0.01 - abs_dy * 0.2 - max_dy * 0.3
		return score



class TetrisGame(QMainWindow):
        def __init__(self):
                super().__init__()
                self.is_paused = False
                self.is_started = False
                self.initUI()
                
        def initUI(self):
                self.grid_size = 30
                self.fps = 100
                self.timer = QBasicTimer()
                self.setFocusPolicy(Qt.StrongFocus)

                palette = QPalette()

                layout_horizontal = QHBoxLayout()
                self.inner_board = InnerBoard()
                self.external_board = ExternalBoard(self, self.grid_size, self.inner_board)

                layout_horizontal.addWidget(self.external_board)
                self.side_panel = SidePanel(self, self.grid_size, self.inner_board)

                layout_horizontal.addWidget(self.side_panel)
                self.status_bar = self.statusBar()
                self.external_board.score_signal[str].connect(self.status_bar.showMessage)

                self.start()
                self.center()

                self.setWindowIcon(QIcon('game_icon.jpg'))

                pygame.mixer.init()
                pygame.mixer.music.load("game_bgm.wav")
                pygame.mixer.music.play(-1)

                palette.setColor(palette.Background,QColor(20,120,20))
                self.setPalette(palette)

                self.setWindowTitle('AI Tetris Game  - Developed by hanshiqiang365')
                self.show()

                self.setFixedSize(self.external_board.width() + self.side_panel.width(),self.side_panel.height() + self.status_bar.height())

                self.tetris_ai = TetrisAI(self.inner_board)

                self.next_action = None
                self.pre_tetris = tetrisShape().shape_empty
        
        def center(self):
                screen = QDesktopWidget().screenGeometry()
                size = self.geometry()
                self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

        def updateWindow(self):
                self.external_board.updateData()
                self.side_panel.updateData()
                self.update()

        def start(self):
                if self.is_started:
                        return

                self.is_started = True
                self.inner_board.createNewTetris()
                self.timer.start(self.fps, self)

        def pause(self):
                if not self.is_started:
                        return

                self.is_paused = not self.is_paused
                if self.is_paused:
                        self.timer.stop()
                        self.external_board.score_signal.emit('Paused')
                else:
                        self.timer.start(self.fps, self)

                self.updateWindow()

        def timerEvent(self, event):
                if event.timerId() == self.timer.timerId():
                        if not self.next_action:
                                self.next_action = self.tetris_ai.getNextAction()
                        if self.next_action:
                                while self.inner_board.current_direction != self.next_action[0]:
                                        self.inner_board.rotateAnticlockwise()
                                count = 0
                                while self.inner_board.current_coord[0] != self.next_action[1] and count < 5:
                                        if self.inner_board.current_coord[0] > self.next_action[1]:
                                                self.inner_board.moveLeft()
                                        else:
                                                self.inner_board.moveRight()
                                        count += 1

                        removed_lines = self.inner_board.moveDown()
                        self.external_board.score += removed_lines
                        if self.pre_tetris != self.inner_board.current_tetris:
                                self.next_action = None
                                self.pre_tetris = self.inner_board.current_tetris
                        self.updateWindow()
                else:
                        super(TetrisGame, self).timerEvent(event)

        def keyPressEvent(self, event):
                if not self.is_started or self.inner_board.current_tetris == tetrisShape().shape_empty:
                        super(TetrisGame, self).keyPressEvent(event)
                        return

                key = event.key()
                if key == Qt.Key_P:
                        self.pause()
                        return

                if self.is_paused:
                        return
                else:
                        super(TetrisGame, self).keyPressEvent(event)
                self.updateWindow()


if __name__ == '__main__':
	app = QApplication([])
	tetris = TetrisGame()
	sys.exit(app.exec_())
	
