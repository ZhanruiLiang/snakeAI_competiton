from field import Snake, Field
import pygame

dirs = Field.dirs
X, Y = 0, 1

class Snake_AI(Snake):
	def __init__(self,name, field, body, direction, color=0x0000ff, res_path='res/snake.png'):
		Snake.__init__(self, name, field, body, direction, color, res_path)
		self._path = []
		self._timer = pygame.time.Clock()
		self.W, self.H = field.size
	def _can_go_food(self, pos):
		c = self.field.getContentAt(pos)
		if c == None or c.type == Field.FOOD:
			return True
		# elif (c in self.body) and c.expire <= self._search_t:
		# 	return True
		return False

	def _dangerous(self, pos):
		for d in dirs:
			np = (pos[0] + d[0]) % self.W, (pos[1] + d[1]) % self.H
			c = self.field.getContentAt(np)
			if c and c.type == Field.BODY and c == c.owner.body[0]:
				print 'dangerous'
				return True
		return False

	def response(self):
		if not self._path:
			self._caclulate()
		if not self._path:
			return self.direction
		np = self._path[0]
		c = self.field.getContentAt(np)
		if (c and ((c.type == Field.BLOCK) 
				or (c.type == Field.BODY and c != self.body[-1]))):
				self._caclulate()
				if not self._path:
					return self.direction

		np = self._path.pop(0)
		p = self.body[0].pos
		dp = (np[0] - p[0], np[1] - p[1])
		self.direction = Field.dirs.index(dp)
		self._t += 1

		return self.direction

	def _caclulate(self):
		expire = 0
		for b in self.body[-1:0:-1]+[self.body[0]]:
			expire += 1
			b.expire = expire
		self._t = 0
		self._path = self._bfs(self.field, self._can_go_food, self.body[0].pos, destType=Field.FOOD)
		if self._path != None and not self._dangerous(self._path[0]):
			pass
		else:
			p = self.body[0].pos
			W, H = self.field.size
			for dx, dy in dirs:
				np = (p[0] + dx) % W, (p[1] + dy) % H
				c = self.field.getContentAt(np)
				if (c == None or c.type == Field.FOOD) and not self._dangerous(np):
					self._path = [np]
					break


	def _bfs(self, field, can_go, start, dest=None, destType=None):
		"""
		start: (x0, y0)
		can_go is function, will be called like: can_go(pos), return Ture or False

		return value: a path list, like [(x1, y1), ....]
		"""
		# node format in que: (pos, father_in_que, distance)
		W, H = field.size
		que = [(start, None, 0)]
		head = tail = 0
		found = False
		vis = set()
		vis.add(start)
		while head <= tail and not found:
			h = que[head]
			self._search_t = h[2] + 1
			for d in dirs:
				npos = (h[0][0]+d[0]) % W, (h[0][1]+d[1]) % H
				if npos not in vis and can_go(npos):
					que.append((npos, head, h[2] + 1))
					vis.add(npos)
					tail += 1
					c = field.getContentAt(npos)
					if (dest!=None and c == dest) or (destType!=None and c and c.type == destType):
						found = True
						break
			head += 1

		if found:
			p = que[tail]
			path = []
			while p[1] != None:
				path.append(p[0])
				p = que[p[1]]
			path.reverse()
			return path
		else:
			return None

