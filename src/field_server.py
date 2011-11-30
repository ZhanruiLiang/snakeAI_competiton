from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from random import randint
from snake import BaseSnake
import config

class FieldRequestHandler(SimpleXMLRPCRequestHandler):
	pass
	# def handle(self):
	# 	super(RequestHandler, self).handle()

class FieldServer(SimpleXMLRPCServer):
	def __init__(self, addr, field):
		SimpleXMLRPCServer.__init__(self, addr, requestHandler=FieldRequestHandler, logRequests=False, allow_none=True)

		self.register_function(self._clifunc_add, 'add')
		self.register_function(self._clifunc_leave, 'leave')
		self.register_function(self._clifunc_join, 'join')
		self.register_function(self._clifunc_quit, 'quit')
		self.register_function(self._clifunc_response, 'response')
		self.register_function(self._clifunc_sync, 'sync')


		self.field = field
		# _ids is used to store the ids that generated. 
		# when need to generate new id, randomly get one, if not in _ids, 
		# then the id can be use
		self._ids = set()
		# the added clients of the server, {id:name, id:name, ...}
		self.clients = {}

	def serve(self, timeout):
		""" timeout is count in ms """
		if timeout != 0:
			self.timeout = max(1, timeout/1000.0)
		else:
			self.timeout = None

		self.handle_request()

	def generateID(self):
		" generateID a client id. "
		while 1:
			r = randint(100000, 999999)
			if r not in self._ids:
				self._ids.add(r)
				return r

	# below are the client call functions, start with _clifunc_
	# generally, return (1, msg) pair if succeed, (0, fail_msg) if fail.
	def _clifunc_add(self):
		if len(self.clients) < config.max_clients:
			id = self.generateID()
			print 'client #%s added into this server' % (id)
			self.clients[id] = None
			return 1, id
		else:
			return 0, 'Too many clients on this server, sorry.'

	def _clifunc_leave(self, id):
		try:
			del self.clients[id]
			self._ids.remove(id)
			print 'client #%s leave this server' % (id)
			return (1, '')
		except:
			return (0, 'No such id')

	def _clifunc_join(self, id, name):
		""" Client with the id request to join the game using player name """
		try:
			self.clients[id] = name
			field = self.field
			initpos, direction =  field.newInitPos()
			snake = BaseSnake(name, initpos, direction, field)
			field.register(snake)
			print 'player %s joined the game' % (name)
			return 1, ''
		except field.RegisterError as e:
			return 0, str(e)

	def _clifunc_quit(self, id):
		name = self.clients[id]
		self.clients[id] = None
		print 'player %s quited the game' % (name)
		return 1, ''

	def _clifunc_response(self, id, round, direction):
		field = self.field
		if round != field.round:
			# something wrong
			return 0, {'round':field.round, 'reason':'round not match'}
		else:
			field.acceptCommand(self.clients[id], direction)
			return 1, ''

	def _clifunc_sync(self, id):
		msg = {}
		name = self.clients[id]
		if name != None and name not in self.field.getPlayers():
			msg['youlost'] = 1
		msg['info'] = self.field.getSyncInfo()
		return 1, msg
