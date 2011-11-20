import pygame

class FieldClient:
	"""
	members:
	----access by user
	FOOD  --|
	HEAD  --|-- constants
	BODY  --|
	BLOCK --|
	size

	----access by system
	_snakes
	_foods
	_blocks
	_board

	------------------------------------------
	methods:
	----call by user
	getContentAt(pos): return the content at pos
	sendCommand(direction): send out the direction you want to go

	----call by client program
	sync()
	connect(server): connect to the server
	
	"""
	pass
