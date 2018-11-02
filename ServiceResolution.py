# -*- coding: utf-8 -*-
#
# ServiceResolution  - Converter
#
# Coded by dhwz (c) 2018
# E-Mail: dhwz@gmx.net
#
# This plugin is open source but it is NOT free software.
#
# This plugin may only be distributed to and executed on hardware which
# is licensed by Dream Property GmbH.
# In other words:
# It's NOT allowed to distribute any parts of this plugin or its source code in ANY way
# to hardware which is NOT licensed by Dream Property GmbH.
# It's NOT allowed to execute this plugin and its source code or even parts of it in ANY way
# on hardware which is NOT licensed by Dream Property GmbH.
#
# If you want to use or modify the code or parts of it,
# you have to keep MY license and inform me about the modifications by mail.
#

from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService
from Components.Element import cached
from os import path

class ServiceResolution(Converter, object):
	VIDEO_PARAMS = 0

	def __init__(self, type):
		Converter.__init__(self, type)
		self.type, self.interesting_events = {
				"VideoInfo": (self.VIDEO_PARAMS, (iPlayableService.evVideoSizeChanged, iPlayableService.evVideoProgressiveChanged, iPlayableService.evVideoFramerateChanged, iPlayableService.evUpdatedInfo,)),
			}[type]
		self.need_wa = iPlayableService.evVideoSizeChanged in self.interesting_events

	def reuse(self):
		self.need_wa = iPlayableService.evVideoSizeChanged in self.interesting_events

	@cached
	def getBoolean(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return False

		if self.type == self.VIDEO_PARAMS:
			frame_rate = info.getInfo(iServiceInformation.sFrameRate)
			if frame_rate > 0:
				return True
			else:
				return False

		return False

	boolean = property(getBoolean)

	@cached
	def getText(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return ""

		if self.type == self.VIDEO_PARAMS:
			xres = None
			if path.exists("/proc/stb/vmpeg/0/xres"):
				f = open("/proc/stb/vmpeg/0/xres", "r")
				try:
					xres = int(f.read(),16)
				except:
					pass
				f.close()
			if not xres:
				xres = info.getInfo(iServiceInformation.sVideoWidth)

			yres = None
			if path.exists("/proc/stb/vmpeg/0/yres"):
				f = open("/proc/stb/vmpeg/0/yres", "r")
				try:
					yres = int(f.read(),16)
				except:
					pass
				f.close()
			if not yres:
				yres = info.getInfo(iServiceInformation.sVideoHeight)

			progressive = info.getInfo(iServiceInformation.sProgressive)
			frame_rate = info.getInfo(iServiceInformation.sFrameRate)
			if not progressive:
				frame_rate *= 2
			frame_rate = (frame_rate+500)/1000
			if frame_rate > 0:
				xres = str(xres)
				yres = str(yres)
				x = "x"
				frame_rate = str(frame_rate)
				p = 'p' if progressive else 'i'
			else:
				xres = ""
				yres = ""
				x = ""
				frame_rate = ""
				p = ""
			return "%s%s%s%s%s" % (xres, x, yres, p, frame_rate)
		return ""

	text = property(getText)

	@cached
	def getValue(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return -1

		if self.type == self.VIDEO_PARAMS:
			return -1 if info.getInfo(iServiceInformation.sVideoHeight) < 0 or info.getInfo(iServiceInformation.sFrameRate) < 0 or info.getInfo(iServiceInformation.sProgressive) < 0 else -2
		return -1

	value = property(getValue)

	def changed(self, what):
		if what[0] != self.CHANGED_SPECIFIC or what[1] in self.interesting_events:
			Converter.changed(self, what)
		elif self.need_wa:
			if self.getValue() != -1:
				Converter.changed(self, (self.CHANGED_SPECIFIC, iPlayableService.evVideoSizeChanged))
				self.need_wa = False