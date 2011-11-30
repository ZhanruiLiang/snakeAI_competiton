import itertools
import pygame
import random
import bz2
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
	reset()
	is_over()
	acceptCommand(snake_name, direction)
	getContentAt(pos):
		return the content, *NOT* a list
	newInitPos(): return (initpos, direction)
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
		self.reset()

	def reset(self):
		self.round = 0
		self.snakes = []
		self.foods = []
		self.blocks = []
		self._board = {}
		self._commands = {}
		self.started = False
		self._sync_cache = None

		size = self.size
		self._initpos = [([(i, size[Y]/2) for i in xrange(5, 1, -1)], self.RIGHT),
				([(i, size[Y]/2) for i in xrange(size[X] - 5, size[X] - 1)], self.LEFT)
				]
		self._next_initpos = 0
		n, m = size
		for i,j in itertools.product(xrange(n), xrange(m)):
			self._board[i, j] = []

		# add block
		for i in xrange(size[0]):
			for j in xrange(size[1]):
				if i == 0 or i == size[0]-1 or j == 0 or j == size[1] - 1:
					self._addContentAt((i,j), Block())
		for y in xrange(3, 20, 7):
			for x in xrange(7, 18):
				self._addContentAt((x, y), Block())
		# add food
		for i in xrange(50):
			self._add_food()
		# self.tracker = Tracker('runlog.bz2')

	def start(self):
		self.started = True

	def register(self, snake):
		"""
		register and init a snake on the board
		"""
		print 'Register a snake named %s'%snake.name

		# test if the snake already exist
		for s in self.snakes:
			if s.name == snake.name:
				# raise SnakeNameError("There is already a snake named %s, %s"%(s.name, s))
				print "There is already a snake named %s, %s"%(s.name, s)
				return
		self.snakes.append(snake)
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
		self._sync_cache = None
		if len(self.snakes) > 0:
			self.start()

	def getSyncInfo(self):
		if self._sync_cache and self._sync_cache[0] == self.round:
			return self._sync_cache[1]
		foods = [x.pos for x in self.foods]
		blocks = [x.pos for x in self.blocks]
		snakes = []
		for snake in self.snakes:
			snakes.append({'name':snake.name,
				'body':[x.pos for x in snake.body],
				'direction':snake.direction,
				})
				# 'stat':snake.statistic})

		info = {'size':self.size,
			'round':self.round,
			'foods':foods, 'blocks':blocks, 'snakes':snakes}

		# l1 = len(info)
		# info = bz2.compress(info.replace(' ', ''))
		# l2 = len(info)
		# print 'compressed %f%%, result len %d'%(100 - float(l2)/l1 * 100, l2)
		self._sync_cache = (self.round, info)
		return info

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

	def newInitPos(self):
		x = self._next_initpos
		self._next_initpos += 1
		self._next_initpos %= len(self._initpos)
		return self._initpos[x]

	def loop(self):
		"""
		run the game, return the ghost
		"""
		if not self.started:
			return []
		self.round += 1
		# backup the snakes' tail in a dict, if a snake eat a food then it can retrieve it's tail
		backup = {}

		# move the snakes
		for snake in self.snakes:
			direction = self._commands.get(snake.name, None)
			if direction != None:
				snake.direction = direction
			dx, dy = self.dirs[snake.direction]
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
		for snake in self.snakes:
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
		for snake in self.snakes:
			snake.statistic.length = len(snake.body)

		self._add_food()
		if self.snakes == []:
			self.reset()
		return [x.name for x in to_die]

	def getPlayers(self):
		return [x.name for x in self.snakes]

	def _eat(self, snake, food):
		snake.statistic.score += food.score
		self._rmContentAt(food.pos, food)

	def _add_food(self):
		if len(self.foods) < 3:
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
				self.foods.append(content)
			elif content.type == Field.BLOCK:
				# self.tracker.log('add %s'%content, pos)
				self.blocks.append(content)
			v.append(content)
			content.pos = pos
		return content

	def _rmContentAt(self, pos, content):
		try:
			self.foods.remove(content)
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

		self.snakes.remove(snake)
		snake.alive = False

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

class Statistic(object):
	"""
	Statistic data of a snake
	"""
	def __init__(self,x=None):
		if x:
			self.score = x[0]
			self.length = x[1]
			self.die = x[2]
		else:
			self.score = 0
			self.length = 0
			self.die = 0

	def __reset__(self):
		self.score = 0
		self.length = 0
		self.die = 0

	def __repr__(self):
		return "Statistic(%s)"%((self.score, self.length, self.die),)
	
