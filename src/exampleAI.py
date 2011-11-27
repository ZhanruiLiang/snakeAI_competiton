from field_client import FieldClient as F
from snake import AISnake
class SnakeAI(AISnake):
	# replace 'Example' with your AI's name, 
	# it will be the player's name shown on the server
	def __init__(self, field):
		super(SnakeAI, self).__init__('Example', field)
	# the method will be call by the client program one time each round
	# it shound return the direction the snake want to go in this round
	def response(self):
		print 'res'
		field = self.field
		dirs = field.dirs # get the directions list
		W, H = field.size # get the board size of the field
		head = self.body[0]

		for i,d in enumerate(dirs):
			pos = (head[0] + d[0]) % W, (head[1] + d[1]) % H # you can no get contents at something like (-1, 3)
			c = field.getContentAt(pos)
			print pos,c
			if c == F.EMPTY or c == F.FOOD:
				self.direction = i
		return self.direction

