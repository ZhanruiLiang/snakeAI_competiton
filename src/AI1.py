from field_client import FieldClient
from snake import AISnake
import pygame

F = FieldClient
X, Y = 0, 1

class SnakeAI(AISnake):
	def __init__(self, field):
		super(SnakeAI, self).__init__('Ray', field, 'res/snake1.png')
		self._path = []
		self._expires = []

	def _can_go_food(self, pos):
		c = self.field.getContentAt(pos)
		if c == F.EMPTY or c == F.FOOD:
			return True
		# TODO
		elif pos in self.body:
			if self._expires[self.body.index(pos)] <= self._search_t:
				return True
		return False

	def _dangerous(self, pos):
		return False
		W, H = self.field.size
		for d in F.dirs:
			np = (pos[X] + d[X]) % W, (pos[Y] + d[Y]) % H
			c = self.field.getContentAt(np)
			if c == F.HEAD:
				return True
		return False

	def response(self):
		if not self._path:
			self._caclulate()
		if not self._path:
			return None
		np = self._path[0]
		c = self.field.getContentAt(np)
		if ((c == F.BLOCK) or (c == F.BODY and np != self.body[-1])):
			self._caclulate()
			if not self._path:
				return None

		np = self._path.pop(0)
		p = self.body[0]
		dp = (np[0] - p[0], np[1] - p[1])
		try:
			self.direction = F.dirs.index(dp)
			self._t += 1
		except ValueError as e:
			self._path = []
			return self.response()
		# self.direction = F.dirs.index(dp)
		# self._t += 1

		return self.direction

	def _caclulate(self):
		l = len(self.body)
		self._expires = [l - x for x in xrange(0, l)]
		self._t = 0
		self._path = self._bfs(self.field, self._can_go_food, self.body[0], destType=F.FOOD)
		if self._path != None and not self._dangerous(self._path[0]):
			pass
		else:
			p = self.body[0]
			W, H = self.field.size
			for dx, dy in F.dirs:
				np = (p[0] + dx) % W, (p[1] + dy) % H
				c = self.field.getContentAt(np)
				if (c == F.EMPTY or c == F.FOOD) and not self._dangerous(np):
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
			for d in F.dirs:
				npos = (h[0][0]+d[0]) % W, (h[0][1]+d[1]) % H
				if npos not in vis and can_go(npos):
					que.append((npos, head, h[2] + 1))
					vis.add(npos)
					tail += 1
					c = field.getContentAt(npos)
					if (dest!=None and npos == dest) or (destType!=None and c == destType):
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

