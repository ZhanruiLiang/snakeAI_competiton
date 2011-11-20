import pygame
from random import randint
import itertools
from field import *
from render import Render
import AI1
# import cProfile
import config

X, Y = 0, 1
Left, Down, Right, Up = Field.LEFT, Field.DOWN, Field.RIGHT, Field.UP
		

def init():
	pygame.display.init()
	pygame.font.init()

def quitclean():
	pygame.display.quit()
	pygame.font.quit()

def main():
	init()

	sSize = config.screen_size #the screen size
	fSize = config.field_size1 # the field size

	screen = pygame.display.set_mode(sSize, 0, 32)
	pygame.display.set_caption('The VimSnakes')
	field = Field(fSize)
	# add block
	for i in xrange(fSize[0]):
		for j in xrange(fSize[1]):
			if i == 0 or i == fSize[0]-1 or j == 0 or j == fSize[1] - 1:
				field._addContentAt((i,j), Block())
	for y in xrange(3, 20, 7):
		for x in xrange(7, 18):
			field._addContentAt((x, y), Block())
	# add food
	for i in xrange(50):
		field._add_food()


	# add snake
	init0 = [(i, fSize[1]/2) for i in xrange(1, 5)]
	init1 = [(i, fSize[1]/2) for i in xrange(fSize[0]-2, fSize[0]-6, -1)]
	init2 = [(fSize[0]/2, i) for i in xrange(1, 5)]

	snake0 = AI1.Snake_AI('Ray', field, init0, Right, 'res/snake1.png')
	snake1 = AI1.Snake_AI('Pest', field, init1 , Left, 'res/snake2.png')
	snake1 = AI1.Snake_AI('ddmbr', field, init2 , Left, 'res/snake.png')

	# controller0 = Controller(snake0)
	render = Render(field, screen)
	
	quit = False
	frame_rate = config.frame_rate
	timer = pygame.time.Clock()
	frame = 0
	try:
		while not quit:
			events = pygame.event.get()
			for event in events:
				if event.type == pygame.QUIT:
					quit = True
				# elif event.type == pygame.KEYDOWN:
				# 	controller0.control(event)
			field.loop()

			render.render()
			pygame.display.flip()
			timer.tick(frame_rate)
			# print 'FPS:',timer.get_fps()
	finally:
		field.tracker.close()
	
	quitclean()
	print 'Bye'
		
if __name__ == '__main__':
	# cProfile.run('main()')
	main()
