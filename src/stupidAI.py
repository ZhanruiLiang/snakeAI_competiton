from field import Snake, Field
class Snake_AI(Snake):
	"""
	members:

	direction
	body
	color
	response(): 
		calculate to response
	"""
	def response(self):
		field = self.field
		dirs = field.dirs # get the directions list
		W, H = field.size # get the board size of the field
		head = self.body[0]

		for i,d in enumerate(dirs):
			pos = (head.pos[0] + d[0]) % W, (head.pos[1] + d[1]) % H # you can no get contents at something like (-1, 3)
			c = self.field.getContentAt(pos)
			if c == None or c.type == field.FOOD:
				self.direction = i
			elif c.type == field.BODY and c.owner != self:
				print "hello %s"%(c.owner.name)
		return self.direction

