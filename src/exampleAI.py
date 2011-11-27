from field_client import FieldClient
from snake import AISnake
F = FieldClient
class SnakeAI(AISnake):
	def __init__(self, field):
		super(SnakeAI, self).__init__('Example', field)
	def response(self):
		field = self.field
		dirs = field.dirs # get the directions list
		W, H = field.size # get the board size of the field
		head = self.body[0]

		for i,d in enumerate(dirs):
			pos = (head[0] + d[0]) % W, (head[1] + d[1]) % H # you can no get contents at something like (-1, 3)
			c = field.getContentAt(pos)
			if c == F.EMPTY or c == F.FOOD:
				self.direction = i
		return self.direction

