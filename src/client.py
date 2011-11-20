import pygame
import config
from field_client import FieldClient
from render import Render
import AI1
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

	field = FieldClient()
	field.connect('localhost')

	sSize = config.screen_size #the screen size
	fSize = config.field_size1 # the field size
	frame_rate = config.frame_rate

	screen = pygame.display.set_mode(sSize, 0, 32)
	pygame.display.set_caption('SnakeAIC')

	init0 = [(i, fSize[1]/2) for i in xrange(1, 5)]
	# TODO, modify the interface of AI1.SnakeAI
	snake = AI1.SnakeAI('Ray', field, init0, Right)

	render = Render(field, screen)
	quti = False
	while not quit:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit = True
		field.sync()
		field.sendCommand(snake.response())

		render.render()
		pygame.display.flip()
		timer.tick(frame_rate)
	
	quitclean()
	print "Bye"

