# Copyright 2012 Hajime Hikida
# Licensed under the Apache License 2.0

import pygame
import random
from .data import star_frames

class Star:
	_PIXEL_WIDE = 9
	_PIXEL_HIGH = 9
	_WHITE = pygame.Color(255, 255, 255)
	
	def __init__(self, cellSize):
		#Rectangle area of the star image.
		self._rect = pygame.Rect(0, 0, self.__class__._PIXEL_WIDE * cellSize[0], self.__class__._PIXEL_HIGH * cellSize[1])
			
		#Rectangle width of each star component (i.e., white dots)
		self._tileWidth = 0.0
			
		#Rectangle height of each star component (i.e., white dots)
		self._tileHight = 0.0
			
		#Animation frames.
		self._frames = star_frames.frames
			
		#Current animation frame number rondomly chosen from the list.
		self._currentFrame = random.randint(0,len(self._frames) - 1)
			
		self._configureSize()
	
	#Private method. 
	def _configureSize(self):
		self._tileWidth = self._rect.width / float(self.__class__._PIXEL_WIDE)
		self._tileHight = self._rect.height / float(self.__class__._PIXEL_HIGH)
	
	#Update the animation frame.
	def update(self):
		self._currentFrame += 1

		if (self._currentFrame > len(self._frames) - 1):
			self._currentFrame = 0
	
	#Draw the star on the surface object.
	def draw(self, surface):
		offsetX = self._rect.left
		offsetY = self._rect.top
		w = round(self._tileWidth)
		h = round(self._tileHight)
		
		#No stroke by default, i.e., fill the rectangle.
		stroke = 0
		
		#If the rectangle is too small to be filled, stroke it.
		if w <= 1 or h <= 1:
			stroke = 1
		
		for pos in self._frames[self._currentFrame]:
			x = round(offsetX + self._tileWidth * pos[0])
			y = round(offsetY + self._tileHight * pos[1])
			pygame.draw.rect(surface, self.__class__._WHITE, pygame.Rect(int(x), int(y), int(w), int(h)), stroke)
			
	#Return the rectangle area.
	def rect(self):
		return self._rect
	rect = property(rect, None, None, None)
	
	#Return true if the current animation frame is in the last.
	def animationFinished(self):
		return self._currentFrame >= len(self._frames) - 1
	animationFinished = property(animationFinished)
	
	#Return the current animation frame number.
	def getCurrentFrame(self):
		return self._currentFrame
	
	#Set the current animation frame number.
	def setCurrentFrame(self, value):
			self._currentFrame = value
	currentFrame = property(getCurrentFrame, setCurrentFrame, None, None)
