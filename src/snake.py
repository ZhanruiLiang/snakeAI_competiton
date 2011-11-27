"""
The BaseSnake class is the base class of other AISnake class, to derive it,
you should implement it's response method

Author: Ray
Last modified: Sunday, November 20, 2011 PM12:19:42 HKT 
"""
from baseobj import *

class BaseSnake(object):
	"""
	members:

	name
	direction: current direction of the snake
	body: a array of the snake's body, index 0 is the head
	field: the field this snake is playing on
	statistic: records of score, die how many times, etc.
	"""
	def __init__(self,name, body, direction, field):
		"""
		body: =[(i0, j0), (i1, j1), ... ]
		"""
		self.name = name
		if body:
			self.body = [Body(self, pos=p) for p in body]
		self.direction = direction
		self.field = field
		self.statistic = None

	def __repr__(self):
		# TODO
		return "<Snake names %s, direction=%s>"%(self.name, self.direction)

class RenderSnake(BaseSnake):
	def __init__(self, name, body, direction, stat, res_path='res/snake1.png'):
		self.name = name
		self.body = body
		self.direction = direction
		self.statistic = stat
		self.res_path = res_path

class AISnake(BaseSnake):
	"""
	append members:

	res_path: the resource path, path of the skin file
	response(): 
		calculate to response
	"""
	def __init__(self, name, field, res_path='res/snake.png'):
		self.res_path = res_path
		super(AISnake, self).__init__(name, None, None, field)

	def response(self):
		pass


