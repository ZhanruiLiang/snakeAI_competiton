"""
The Snake class is the base class of other snakeAI class, to derive it,
you should implement it's response method

Author: Ray
Last modified: Sunday, November 20, 2011 PM12:19:42 HKT 
"""
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
		self.body = [Body(self, pos=p) for p in body]
		self.direction = direction
		self.field = field
		self.statistic = None

	def __repr__(self):
		return "<Snake names %s, direction=%s>"%(self.name, self.direction)

class Snake(BaseSnake):
	"""
	append members:

	res_path: the resource path, path of the skin file
	response(): 
		calculate to response
	"""
	def __init__(self, name, body, direction, field, res_path='res/snake.png'):
		self.res_path = res_path
		super.__init__(self, name, body, direction, field)

	def response(self):
		pass


