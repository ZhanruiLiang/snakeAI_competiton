class Controller:
	def __init__(self, snake, keys=None):
		"""
		snake: the snake to be control
		keys = [left, down, right, up]
		"""
		self.snake = snake
		if keys == None:
			self.keys = ['a', 's', 'd', 'w']
		else:
			self.keys = keys
		self.directs = {}
		d = (Left, Down, Right, Up)
		for i in xrange(4):
			self.directs[self.keys[i]] = d[i]
		
	def control(self, event):
		key = event.unicode
		try:
			direct = self.directs[key] 
		except KeyError:
			return
		if (direct, self.snake.direction) not in ((Right, Left), (Left, Right), (Up, Down), (Down, Up)):
			self.snake.direction = direct
