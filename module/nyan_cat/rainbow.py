# Copyright 2012 Hajime Hikida
# Licensed under the Apache License 2.0

import pygame

class Rainbow:
	#Scalers used for calculating the size of the rainbow rectangles according to the cat image size.
	_SCALER_X = 7
	_SCALER_Y = 2
	
	#Number of the animation frame of the cat.
	_NUM_FRAME_CAT = 6
	
	#Rainbow colors
	_RED 	= pygame.Color(255, 0, 0) 		#FF0000
	_ORANGE = pygame.Color(255, 153, 0) 	#FF9900
	_YELLOW = pygame.Color(255, 255, 0)	#FFFF00
	_GREEN	= pygame.Color(51, 255, 0)		#33FF00
	_BLUE	= pygame.Color(0, 153, 255)		#0099FF
	_PURPLE	= pygame.Color(102, 51, 255)	#6633FF

	def __init__(self, catRect, cellSize):
		#Rectangle area of the cat image, not the rainbow!!
		self._catRect = catRect
					
		#Rectangle width of each rainbow component (i.e., red rectangle, orange rectangle, etc.)
		self._tileWidth = self.__class__._SCALER_X * cellSize[0]
					
		#Rectangle height of each rainbow component
		self._tileHeight = self.__class__._SCALER_Y * cellSize[1]
					
		#Store the toggled animation state.
		self._animationToggled = False
		
		#Current frame index of the cat animation.
		self._catFrame = 0

	#Update properties according to the status of the cat image.
	def update(self):
		self._catFrame += 1
		
		#Update the animation frame of the rainbow object only when the cat object is in the initiali state, i.e., in the first frame.
		#This is becaue the cat has 6 frames while the rainbow only 2.
		if (self._catFrame > self.__class__._NUM_FRAME_CAT - 1):
			self._animationToggled = not self._animationToggled
			self._catFrame = 0
	
	#Draw rainbows according to the status of the cat image.
	def draw(self, surface):
		#Setup initial state.
		x = self._catRect.left
		y = self._catRect.top + 2 * self._tileHeight
		direction = 1
		
		if self._animationToggled:
			y = self._catRect.top + 3 * self._tileHeight
			direction =-1
		
		count = 0
		
		#Draw rainbow rectangles until far enough from the surface bounds. 
		while x > -0.5 * surface.get_rect().width:
			self._draw(surface, (x, y))
			x -= self._tileWidth
			y += 0.5 * self._tileHeight * direction
			count += 1
			
			if count >= 3:
				count = 0
				direction *= -1
	
	#Private method. Draw a set of rainbow components (i.e., red, orange, ..., purple).
	def _draw(self, surface, origins):
		x = origins[0]
		y = origins[1]
		
		#Tile 大小放大后通常非整数，独立取整会让相邻色块间出现 1px 网格间隙；
		#对边界分别取整并共享（左右边界、上下边界），实现无缝拼接。
		x0 = int(round(x))
		x1 = int(round(x + self._tileWidth))
		w = max(x1 - x0, 1)
		
		colors = (self.__class__._RED, self.__class__._ORANGE, self.__class__._YELLOW,
		          self.__class__._GREEN, self.__class__._BLUE, self.__class__._PURPLE)
		for i, color in enumerate(colors):
			y0 = int(round(y + i * self._tileHeight))
			y1 = int(round(y + (i + 1) * self._tileHeight))
			h = max(y1 - y0, 1)
			pygame.draw.rect(surface, color, pygame.Rect(x0, y0, w, h))
