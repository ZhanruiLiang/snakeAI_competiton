class FieldObj:
	type = 'unknown'
	def __init__(self, pos=None):
		self.pos = pos

	def __repr__(self):
		return "<%s at %s>"%(self.type, self.pos)

class Empty:
	type = 'empty'

class Food(FieldObj):
	type = 'food'
	score = 5
	
	def merge(self, other):
		self.score += other.score

class Block(FieldObj):
	type = 'block'

class Body(FieldObj):
	type = 'body'
	def __init__(self, owner, pos=None):
		"""
		owner: the snake who own this block of body
		"""
		self.owner = owner
		self.pos = pos
	def __repr__(self):
		return "<%s at %s, owner=%s>"%(self.type, self.pos, self.owner.name)
