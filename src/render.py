import pygame
from field import *
import config

X, Y = 0, 1

def load(filename):
	return pygame.image.load(filename).convert_alpha()

class Render:
	SEP_DASH = 3
	MAX_FRAME = 10000
	def __init__(self, field, surface):
		self.field = field
		self.grid_size = config.grid_size
		self.color_bg = (0xff, 0xff, 0xaa)
		self.surface = surface
		self.load_pics()
		self._frame = 0

	def _rotate_span(self, surface, cnt=4):
		ans = [surface]
		for i in xrange(cnt):
			ans.append(pygame.transform.rotate(ans[-1], 90))
		return ans

	def load_snake_pic(self, snake, path):
		transform = pygame.transform
		gw, gh = self.grid_size

		pic0 = transform.smoothscale(load(path), (gw*4, gh))

		turn = self._rotate_span(pic0.subsurface((0, 0, gw, gh)))
		body = self._rotate_span(pic0.subsurface((gw, 0, gw, gh)), 2)
		head = self._rotate_span(pic0.subsurface((gw * 2, 0, gw, gh)))
		tail = self._rotate_span(pic0.subsurface((gw * 3, 0, gw, gh)))
		pic = {
				((0, 1), (1, 0)): turn[0],
				((0, -1), (1, 0)): turn[1],
				((-1, 0), (0, -1)): turn[2],
				((-1, 0), (0, 1)): turn[3],
				((-1, 0), (1, 0)): body[1],
				((0, -1), (0, 1)): body[0],
				'head': head,
				'tail': tail,
				}
		self._pic_snakes[snake.name] = pic

	def load_pics(self):
		"""
		load and cache the picures for future rendering
		"""
		transform = pygame.transform

		gw, gh = self.grid_size

		# load background
		self._pic_dashback = load('res/dashback.png')
		self._pic_dashboard = load('res/dashboard.png')
		
		# load the snakes body
		# construct:
		#		self._pic_snake_turn = [ down-right, right-up, left-up, left-down]
		#		self._pic_snake_body = [ up-down, left-right]
		#		self._pic_snake_head = [ up, left, down, right]
		#		self._pic_snake_tail = [ down, right, up, left]
		snake = load('res/snake.png')
		snake = transform.smoothscale(snake, (gw*4, gh))

		self._pic_snakes = {}

		# load food
		self._pic_food = transform.smoothscale(load('res/food.png'), (gw, gh))
		self._pic_block = transform.smoothscale(load('res/block.png'), (gw, gh))

		# load dashboard
		self._pic_dashback = load('res/dashback.png')
		self._pic_dashboard = load('res/dashboard.png')

		# allocate surfaces
		self._surface_dash = pygame.Surface(config.dash_size).convert_alpha()
		self._surface_dash.blit(self._pic_dashback, (0, 0))
		self._surface_dash.blit(load('res/logo.png'), (5, 5))
		self._surface_dashboard = self._pic_dashboard.copy()
		self._surface_dashboards = {}

		self._surface_field = pygame.Surface(config.field_size).convert_alpha()

		# load font
		self._font = pygame.font.SysFont('monospace', 24)
		self._font_color = (0xff, 0xff, 0xff, 0xff)
		# pre render the background of a dashboard
		# it starts at (x0, y0), then (x0, y0 + dy + 2) ... etc
		font = self._font
		dashboard = self._surface_dashboard
		x0, y0 = 10, 20
		lines = ['score:', 'length:', 'die:']
		for line in lines:
			dashboard.blit(font.render(line, True, self._font_color), (x0, y0))
			y0 += font.size('')[1]+2

	def render_dash(self):
		x0, y0 = 5, 70
		x, y = x0, y0
		sep = 10
		dy = self._pic_dashboard.get_size()[1] + sep
		for snake in self.field._snakes:
			# render the snake's board
			if snake.name not in self._surface_dashboards:
				# create
				board = self._surface_dashboard.copy()
				board.blit(self._font.render(snake.name, True, self._font_color), (20, 1))
				self._surface_dashboards[snake.name] = board
			else:
				board = self._surface_dashboards[snake.name]

			st = snake.statistic
			lines = ['score', 'length', 'die']
			bx, by = 180, 20
			rect = 100, 5, 80, 110
			board.blit(self._surface_dashboard.subsurface(rect), rect)
			for key in lines:
				text = str(st.__getattribute__(key))
				size = self._font.size(text)
				rect = (bx - size[X], by) + size
				board.blit(self._font.render(text, True, self._font_color), rect)
				by += size[Y] + 2

			self._surface_dash.blit(board, (x, y))
			y += dy

	def render_food(self):
		for food in self.field._foods:
			self._surface_field.blit(self._pic_food, (self.grid_size[X] * food.pos[X], self.grid_size[Y] * food.pos[Y]))

	def render_block(self):
		for block in self.field._blocks:
			self._surface_field.blit(self._pic_block, (self.grid_size[X] * block.pos[X], self.grid_size[Y] * block.pos[Y]))

	def grid_to_real(self, pos):
		return pos[X] * self.grid_size[X], pos[Y] * self.grid_size[Y]

	def render_snake(self):
		for snake in self.field._snakes:
			if snake.name not in self._pic_snakes:
				self.load_snake_pic(snake, snake.res_path)
			# pic_snake is the collection of a snake's pictures
			# pic_snake = { 'head': ..., 'tail': ..., ((0, -1), (1, 0)): ..., ((0, 1), (1, 0)): ...}
			pic_snake = self._pic_snakes[snake.name]
			# render head
			head = snake.body[0].pos
			pic = pic_snake['head'][(snake.direction + 1) % 4]
			self._surface_field.blit(pic, self.grid_to_real(head))

			if len(snake.body) == 1: continue
			# render tail
			tail = snake.body[-1].pos
			prev = snake.body[-2].pos
			tail_direction = (Field.dirs.index((tail[X] - prev[X], tail[Y] - prev[Y])) + 3) % 4
			pic = pic_snake['tail'][tail_direction]
			self._surface_field.blit(pic, self.grid_to_real(tail))

			# render body
			for sec0, sec1, sec2 in zip(snake.body[:-2], snake.body[1:-1], snake.body[2:]):
				p0, p1, p2 = sec0.pos, sec1.pos, sec2.pos
				key = (p0[X] - p1[X], p0[Y] - p1[Y]), (p2[X] - p1[X], p2[Y] - p1[Y])
				keyp = key[1], key[0]
				pic = pic_snake.get(key, 0) or pic_snake.get(keyp, 0)
				self._surface_field.blit(pic, self.grid_to_real(p1))

	def render(self):
		# procedure
		# 1. render background
		# 2. render foods
		# x. render blocks
		# 3. render snakes
		# 4. render dashboards

		# rendder background
		self._surface_field.fill(self.color_bg)
		# render others
		self.render_food()
		self.render_block()
		self.render_snake()
		if self._frame % self.SEP_DASH == 0:
			self.render_dash()

		self.surface.blit(self._surface_dash, config.dash_pos)
		self.surface.blit(self._surface_field, config.field_pos)
		self._frame += 1
		self._frame %= self.MAX_FRAME
