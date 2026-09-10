# Copyright 2012 Hajime Hikida
# Licensed under the Apache License 2.0

import random
import pygame
from .star import Star

class StarManager:
	#Default value of the horizontal velocity of a star.
	_DEFAULT_VELOCITY_X = -10
	
	def __init__(self, surfaceRect, cellSize, numStars, velocityX=_DEFAULT_VELOCITY_X):
		#Rectangle area of the surface object upon which stars shows up.
		self._surfaceRect = surfaceRect
				
		#Size of pixelated rectangle for the image.
		self._cellSize = cellSize
				
		#Vhorizontal velocity of stars (positive right).
		self._velocityX = velocityX
				
		#Star objects to manage.
		self._stars = self._createStars(surfaceRect, cellSize, numStars)	
	#Return a star object randomly chosen within a rectangle area.
	def _createStar(self, rect, cellSize):
		x = random.randint(rect.left, rect.width)
		y = random.randint(rect.top, rect.height)
		star = Star(cellSize)
		star.rect.topleft = (x, y)
		return star

	#Return a list of newly created stars.cellSize
	def _createStars(self, rect, cellSize, numStars):
		stars = []
					
		for i in range(numStars):
			star = self._createStar(rect, cellSize)
			stars.append(star)
					
		return stars
	
	#Update animation frame of stars.
	def update(self):
		for i in reversed(range(len(self._stars))):
			star = self._stars[i]
			star.rect.left += self._velocityX
			star.update()
			
			#If the star comes to the end of the animation remove it and add a new one.
			if star.animationFinished:
				self._stars.remove(star)
				newStar = self._createStar(self._surfaceRect, self._cellSize)
				newStar.currentFrame = 0
				self._stars.append(newStar)
	
	#Draw stars on the surface object.
	def draw(self, surface):
		for star in self._stars:
			star.draw(surface)
