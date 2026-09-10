# Copyright 2012 Hajime Hikida
# Licensed under the Apache License 2.0

import pygame
from .data import nyancat_frame1
from .data import nyancat_frame2
from .data import nyancat_frame3
from .data import nyancat_frame4
from .data import nyancat_frame5
from .data import nyancat_frame6

class Nyancat:
	#Pixel wide for the original image.
	_PIXEL_WIDE = 35
	
	#Pixel high for the original image.
	_PIXEL_HIGH = 25
	
	#Pixel colors
	_WHITE 	= pygame.Color(255, 255, 255)	#FFFFFF
	_BLACK 	= pygame.Color(0, 0, 0)			#000000
	_GRAY 	= pygame.Color(153, 153, 153)	#999999
	_PINK1 	= pygame.Color(255, 204, 153)	#FFCC99
	_PINK2 	= pygame.Color(255, 153, 255)	#FF99FF
	_PINK3 	= pygame.Color(255, 51, 153)	#FF3399
	_PINK4 	= pygame.Color(255, 153, 153)	#FF9999
	
	def __init__(self, rect=pygame.Rect(0, 0, _PIXEL_WIDE, _PIXEL_HIGH)):
		#Rectangle area of the cat image (subject to change).
		self._rect = rect
		
		#Width of a pixelerated area of the image (i.e., dots' width)
		self._tileWidth = 0.0
		
		#height of a pixelerated area of the image (i.e., dots' height)
		self._tileHeight = 0.0
		
		#Animation frames from external modules.
		self._frames = (
						nyancat_frame1.pixeldata,
						nyancat_frame2.pixeldata,
						nyancat_frame3.pixeldata,
						nyancat_frame4.pixeldata,
						nyancat_frame5.pixeldata,
						nyancat_frame6.pixeldata)
		
		#Index of the current animation frame.
		self._currentFrame = 0
		
		self._configureSize()
	
	#Private method. Calculate the maximum image size in a given rectangle area without breaking the image's aspect ratio.
	def _configureSize(self):
		w = self._rect.width
		h = self._rect.height
		
		if (w <= h):
			imageWidth = w
			imageHeight = w * self.__class__._PIXEL_HIGH / float(self.__class__._PIXEL_WIDE)
		else:
			imageWidth = h * self.__class__._PIXEL_WIDE / float(self.__class__._PIXEL_HIGH)
			imageHeight = h
		
		#Make sure the image size is always smaller than the rectangle.
		if imageWidth > self._rect.width or imageHeight > self._rect.height:
			raise ArithmeticError
		
		self._tileWidth = imageWidth / float(self.__class__._PIXEL_WIDE)
		self._tileHeight = imageHeight / float(self.__class__._PIXEL_HIGH)
		
		#Set a newer size.
		self._rect.size = (int(round(imageWidth)), int(round(imageHeight)))
	
	#Set the next animation frame.
	def update(self):
		self._currentFrame += 1

		if (self._currentFrame > len(self._frames) - 1):
			self._currentFrame = 0
	
	#Draw pixel data on the surface.
	def draw(self, surface):
		self._draw(surface, self._frames[self._currentFrame][0], self.__class__._WHITE)
		self._draw(surface, self._frames[self._currentFrame][1], self.__class__._BLACK)
		self._draw(surface, self._frames[self._currentFrame][2], self.__class__._GRAY)
		self._draw(surface, self._frames[self._currentFrame][3], self.__class__._PINK1)
		self._draw(surface, self._frames[self._currentFrame][4], self.__class__._PINK2)
		self._draw(surface, self._frames[self._currentFrame][5], self.__class__._PINK3)
		self._draw(surface, self._frames[self._currentFrame][6], self.__class__._PINK4)
		
	#Private method. Fill rectangles with a given color on the surface object.
	def _draw(self, surface, positions, color):
		offsetX = self._rect.left;
		offsetY = self._rect.top;
		
		#Fill each rectangle area specified by a position array.
		for pos in positions:
			#Tile 大小放大后通常非整数，独立取整会让相邻格子间出现 1px 网格间隙；
			#改为对格子的左右边界分别取整，相邻格子共享边界，实现无缝拼接。
			x0 = int(round(offsetX + pos[0] * self._tileWidth))
			y0 = int(round(offsetY + pos[1] * self._tileHeight))
			x1 = int(round(offsetX + (pos[0] + 1) * self._tileWidth))
			y1 = int(round(offsetY + (pos[1] + 1) * self._tileHeight))
			w = max(x1 - x0, 1)	#极端小的格子至少占 1 像素，避免消失
			h = max(y1 - y0, 1)
					
			rect = pygame.Rect(x0, y0, w, h)
			pygame.draw.rect(surface, color, rect)	
	#Return the rectangle area of the surface object.
	def rect(self):
		return self._rect
	rect = property(rect, None, None, None)
	
	#Return a pixelerated rectangle area (i.e., dot size) for the image.
	def cellSize(self):
		return (int(round(self._tileWidth)), int(round(self._tileHeight)))
	cellSize = property(cellSize, None, None, None)
