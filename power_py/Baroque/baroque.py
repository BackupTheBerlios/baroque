############################################################################
##
## $Id: baroque.py,v 1.1 2004/07/11 02:38:20 rdsarts Exp $
##
## Copyright (C) 2002-2003 Rds <rds@rdsarts.com> and 
##              Tilo Riemer <riemer@lincvs.org>
## All rights reserved.
##
## Baroque is a merge of BatMonitor and the old Baroque
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions
## are met:
##
## 1. Redistributions of source code must retain the above copyright
##    notice, this list of conditions and the following disclaimer.
## 2. Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
## 3. The name of the author may not be used to endorse or promote products
##    derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE AUTHOR `AS IS'' AND ANY EXPRESS OR
## IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
## OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
## IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
## INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
## NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
## THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##
###############################################################################


import rox, os, pango
from rox import g
from rox.options import Option

import findpower
findpower.find()
import power
from power import *
offline_state = OFFLINE

battery = Power()
	#rox.croak('Sorry, but we could not find or load apm.py or acpi.py. '\
	#	  'Please download and install power.py from http://rdsarts.com/code/powerpy/')

_ = rox.i18n.translation(os.path.join(rox.app_dir, 'Messages'))

'''
batt_type = -1	# 0 = ACPI, 1 = APM

# Initalize the battery object
try:
	import acpi
	battery = acpi.Acpi()
	batt_type = 0
	offline_state = acpi.OFFLINE
except ImportError:
	try:
		import apm
		battery = apm.Apm()
		batt_type = 1
		offline_state = apm.OFFLINE
	except ImportError:
		# No PM module loaded. We be screwed.
		# warning_dialog(title='Low Battery Warning', txt="Sorry, could not load apm.py or acpi.py.\nPlease download and install one from http://www.iapp.de/~riemer/projects", warn = 0)
		rox.croak('Sorry, but we could not load power.py. '+
			  'Please download and install either apm.py or acpi.py from http://www.iapp.de/~riemer/projects')

'''

def warning_dialog(txt='', warning = 1, title='Dialog'):
	"""This displays a dialog box, with only a OK button, that contains txt as it's text, and title as it's title.
	If called before destroying the last one, spawns a new window and puts the same dialog in both windows...
	Yah, that's a TODO.."""
	dialog = g.Dialog('Low Battery Warning', None, 0)

	def dialog_kill(self, event):
		dialog.destroy()

	button=g.Button("OK")
	button.connect("clicked", dialog_kill, "button 1")
	dialog.action_area.pack_start(button, True, False, 0)

	image=g.Image()
	if warning == 1: image.set_from_stock(g.STOCK_DIALOG_WARNING, g.ICON_SIZE_DIALOG)
	else: 		image.set_from_stock(g.STOCK_DIALOG_INFO, g.ICON_SIZE_DIALOG)
	label=g.Label(str='Warning. Battery is\ncurrently at ' + str(battery.percent()) + '%')

	hbox = g.HBox(False, 5)
	hbox.pack_start(image, False, False, 5)
	hbox.pack_start(label, False, False, 5)
	dialog.vbox.pack_start(hbox, True, False, 5)
	dialog.show_all()

class boxes(g.VBox):
	"""This is a class containing the V/HBoxes for our applet."""
	## XXX: Move this back into being class variables, not instance.
	# Meet the Opteels.
	warn = Option('warn', True)
	warn_level = Option('warn_level', 10)
	applet_width = Option('applet_width', 100)
	# applet_height = Option('applet_height', 20)
	text_font = Option('text_font', 'Sans 12')
	# text_height = Option('text_height', 10)
	ticks_till_update = Option('ticks_till_update', "1000")
	LABEL_IN_BAR = Option('LABEL_IN_BAR', True)

	#init class variables
	warned = False
	msg = 0
	battery_display = g.Label()
	percent_display = g.ProgressBar()
	tooltip = g.Tooltips()
	update_timeout = 0


	def __init__(self):
		g.VBox.__init__(self)
		
		self.update_timeout = g.timeout_add(int(self.ticks_till_update.int_value) * 100, self.update_display, battery)
		
		def options_update():
			g.timeout_remove(self.update_timeout)
			self.update_display(battery)
			# print str(int(self.ticks_till_update.int_value) * 100)
			print self.text_font			
			self.set_size_request(self.applet_width.int_value, -1)
			self.update_timeout = g.timeout_add(int(self.ticks_till_update.int_value) * 100, self.update_display, battery)

		rox.app_options.add_notify(options_update)
		
		def destroyed(self):
			g.timeout_remove(self.update_timeout)
			rox.app_options.remove_notify(options_update)

		self.connect('destroy', destroyed)
		# pack_start(widget, expand, fill, padding)
		self.pack_start(self.percent_display, g.TRUE, g.TRUE, 0)
		self.pack_start(self.battery_display, g.FALSE, g.FALSE, 0)
		self.percent_display.set_size_request(-1,10)
		self.set_size_request(self.applet_width.int_value, -1)
		self.update_display(battery)
		self.battery_display.set_justify(g.JUSTIFY_CENTER)
		self.show()

	def update_display(self, battery):
		"""Updates all the parts of our applet, and cleans it up if needed."""
		try:
			battery.update()
		except:
			print "SHOULD HANDLE THIS! ERROR IN UPDATE!!!!!!"
			return g.TRUE

		percent=battery.percent()
		self.percent_display.set_fraction(float(percent) / 100)

		#should never happens
		txt = "Unknown"

		if battery.charging_state() == 1:
			txt = _("AC Online")
		elif battery.charging_state() == 2:
			txt = _("Charging")
		else:
			# Discharing from the battery
			# TODO: This reports 'Battery' if we start it without a battery. This is a no-no?
			if self.msg == 1:
				self.msg = 0
				txt = _("Battery")
			else:
				self.msg =1
				hour, min = battery.time()
				txt = _("%d hours, %d minutes")%(hour, min)

		self.percent_display.set_text(txt)
		
		label_font = pango.FontDescription(self.text_font.value)
		self.battery_display.modify_font(label_font)
		self.battery_display.set_markup(txt)

		label_display = self.LABEL_IN_BAR.value

		if label_display == 'text-only':
			self.percent_display.hide()
			self.battery_display.show()
		elif label_display == 'progress-only':
			self.percent_display.show()
			self.battery_display.hide()
		elif label_display == 'progress-notext':
			self.percent_display.show()
			self.battery_display.hide()
			self.percent_display.set_text('')
		else:
			self.percent_display.set_text('')
			self.percent_display.show()
			self.battery_display.show()

		if self.warn.value == 'True':
			if (battery.charging_state() == offline_state and percent <= self.warn_level.int_value):
				if self.warned == False:
					warning_dialog(title=_('Warning, low battery'), 
						txt=_('Warning. Battery is\ncurrently at %d%%'%battery.percent()) )
					self.warned = True
			else:
				self.warned = False

		return g.TRUE

	def percent(self):
		return str(battery.percent())
