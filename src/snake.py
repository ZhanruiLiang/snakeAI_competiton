"""
The Snake class is the base class of other snakeAI class, to derive it,
you should implement it's response method

Author: Ray
Last modified: Sunday, November 20, 2011 PM12:19:42 HKT 
"""
class Snake:
	"""
	members:

	direction
	body
	name
	response(): 
		calculate to response
	"""
	def __init__(self,name, body, direction, res_path='res/snake.png'):
		"""
		body: =[(i0, j0), (i1, j1), ... ]
		"""
		self.name = name
		self.body = [Body(self, pos=p) for p in body]
		self.direction = direction
		self.res_path = res_path

	def response(self):
		pass

	def __repr__(self):
		return "<Snake names %s, direction=%s>"%(self.name, self.direction)

