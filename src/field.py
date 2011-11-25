import itertools
import pygame
import random
from tracker import Tracker
from baseobj import *
from snake import BaseSnake

X, Y = 0, 1

class Field(object):
	"""
	members:

	size:
		(w, h),indicates that the field is a w x h grid borad
	register()
	acceptCommand(snake_name, direction)
	getContentAt(pos):
		return the content, *NOT* a list
	---------------------------------------
	note that in the coordinate system,
	upper-left=(0, 0),
	upper-right=(w,0),
	lower-left=(0,h),
	lower-right=(w,h)
	"""
	LEFT, DOWN, RIGHT, UP = 0, 1, 2, 3
	FOOD, BLOCK, BODY, EMPTY = Food.type, Block.type, Body.type, Empty.type
	dirs = ((-1, 0), (0, 1), (1, 0), (0, -1))

	def __init__(self, size):
		self.size = size
		self._snakes = []
		self._foods = []
		self._blocks = []
		self._board = {}
		n, m = size
		for i,j in itertools.product(xrange(n), xrange(m)):
			self._board[i, j] = []

		# self.tracker = Tracker('runlog.bz2')

	def register(self, snake):
		"""
		register and init a snake on the board
		"""
		print 'Register a snake named %s'%snake.name

		# test if the snake already exist
		for s in self._snakes:
			if s.name == snake.name:
				raise SnakeNameError("There is already a snake named %s, %s"%(s.name, s))
		self._snakes.append(snake)
		snake.alive = True
		snake.statistic = Statistic()
		for node in snake.body:
			v = self.getContentAt(node.pos)
			if  v == None:
				self._addContentAt(node.pos, node)
			elif v.type == Field.FOOD:
				self._eat(snake, v)
				self._addContentAt(node.pos, node)
			else:
				snake.body = snake.body[:snake.body.index(node)]
				if node == snake.body[0]:
					# this means the snake can not be initialize on the place
					raise self.RegisterError(self.getContentAt(node.pos))
				else:
					break

	def acceptCommand(self, name, direction):
		self._commands[name] = direction

	def getContentAt(self, pos):
		"""
		return value: the content at pos
		"""
		v = self._board[pos]
		# self.tracker.log('get content=%s'%v, pos)
		if len(v) == 1:
			return v[0]
		elif len(v) == 0:
			return None
		else:
			raise self.OverlapError(v)

	def loop(self):
		"""
		run the game
		"""
		# backup the snakes' tail in a dict, if a snake eat a food then it can retrieve it's tail
		backup = {}
		# commands[sname], the next direction of the snake

		# move the snakes
		for snake in self._snakes:
			dx, dy = self.dirs[self._commands[snake.name]]
			p = snake.body[0].pos
			next_p = (p[X] + dx) % self.size[X], (p[Y] + dy) % self.size[Y]
			if len(snake.body) > 1 and snake.body[1].pos != next_p:
				snake.body.insert(0, Body(snake))
				self._addContentAt(next_p, snake.body[0])
				self._rmContentAt(snake.body[-1].pos, snake.body[-1])
				backup[snake.name] = snake.body.pop()
			else:
				# this command can not be executed
				pass
		# clear the commands
		self._commands = {}

		# judge by the rules
		to_die = []
		for snake in self._snakes:
			b = snake.body[0]
			v = self._board[b.pos]
			for i in v:
				if i != b and i.type in (Field.BODY, Field.BLOCK):
					# the snake hit another snake
					to_die.append(snake)
					break
			else:
				# not die
				for i in v:
					if i.type == Field.FOOD:
						self._eat(snake, i)
						b = backup[snake.name]
						snake.body.append(self._addContentAt(b.pos, b))

		for snake in to_die:
			self._die_snake(snake)

		# update statistics
		for snake in self._snakes:
			snake.statistic.length = len(snake.body)

		self._add_food()

	class Error(Exception):
		def __init__(self, value):
			self.value = value
		def __str__(self):
			return repr(self.value)
	class OverlapError(Error):
		pass
	class SnakeNameError(Error):
		pass
	class RegisterError(Error):
		pass


	def _eat(self, snake, food):
		snake.statistic.score += food.score
		self._rmContentAt(food.pos, food)

	def _add_food(self):
		if len(self._foods) < 3:
			added = False
			while not added:
				pos = random.randint(0, self.size[0]-1), random.randint(0, self.size[1]-1)
				c = self.getContentAt(pos)
				if c == None:
					self._addContentAt(pos, Food())
					# self.tracker.log('add food', pos)
					added = True
					break

	def _addContentAt(self, pos, content):
		v = self._board[pos]
		need = True
		if content.type == Field.FOOD:
			for i in v:
				if i.type == Field.FOOD:
					i.merge(content)
					content = i
					# self.tracker.log('merge food %s, %s'%(i, content), pos)
					need = False
					break
				if i.type == Field.BLOCK:
					need = False
					break
		if need:
			if content.type == Field.FOOD:
				# self.tracker.log('add food', pos)
				self._foods.append(content)
			elif content.type == Field.BLOCK:
				# self.tracker.log('add %s'%content, pos)
				self._blocks.append(content)
			v.append(content)
			content.pos = pos
		return content

	def _rmContentAt(self, pos, content):
		try:
			self._foods.remove(content)
		except ValueError:
			pass
		self._board[pos].remove(content)
		# self.tracker.log('remove %s, rest:%s'%(content, self._board[pos]), pos)

	def _die_snake(self, snake):
		""" the snake die, and it's body change to food"""
		print '%s die'%snake.name
		snake.statistic.die += 1
		# self.tracker.log('die %s'%snake, snake.body[0].pos)

		# remove the bodies
		for b in snake.body:
			self._rmContentAt(b.pos, b)

		# some part of body change to food
		# for b in snake.body[1::4]:
		# 	self._addContentAt(b.pos, Food(0x660022))

		self._snakes.remove(snake)
		snake.alive = False

class Statistic(object):
	"""
	Statistic data of a snake
	"""
	def __init__(self):
		self.score = 0
		self.length = 0
		self.die = 0

	def __reset__(self):
		self.score = 0
		self.length = 0
		self.die = 0

