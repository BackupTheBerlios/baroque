############################################################################
##
## $Id: baroque.py,v 1.7 2003/12/09 16:24:18 rds Exp $
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


import rox
from rox import g
from rox.options import Option

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
		rox.croak('Sorry, but we could not find or load apm.py or acpi.py. Please download and install either apm.py or acpi.py from http://www.iapp.de/~riemer/projects')

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
	# Meet the Opteels.
	warn = Option('warn', True)
	warn_level = Option('warn_level', 10)
	applet_width = Option('applet_width', 100)
	applet_height = Option('applet_height', 20)
	text_height = Option('text_height', 10)
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
			self.update_timeout = g.timeout_add(int(self.ticks_till_update.int_value) * 100, self.update_display, battery)

		rox.app_options.add_notify(options_update)
		
		def destroyed(self):
			g.timeout_remove(self.update_timeout)
			rox.app_options.remove_notify(options_update)

		self.connect('destroy', destroyed)
		self.pack_start(self.percent_display, 1, 1, 2)
		self.pack_start(self.battery_display, 1, 1, 2)
		self.update_display(battery)
		self.battery_display.set_justify(g.JUSTIFY_CENTER)
		self.show()

	def update_display(self, battery):
		"""Updates all the parts of our applet, and cleans it up if needed."""

		if batt_type == 0:
			try:
				battery.update()
			except AcpiError:
				# rem battery
				# battery = acpi.Acpi()
				#TODO: handling of exception
				pass
		else:
			battery.update()


		percent=battery.percent()
		self.percent_display.set_fraction(float(percent) / 100)

		#should never happens
		txt = "Unknown"
		
#		if self.msg == 1:
#			if battery.charging_state() == 1:
#				txt = 'AC Online'
#			elif battery.charging_state() == 2:
#				txt = 'Charging'
#			else: txt = 'Battery'
#			self.msg = 0
#		else:
#			if batt_type == 1:
#				temp2 = battery.time()
#				temp = int(temp2 / 60)
#				temp2 = temp2 - (temp * 60)
#				txt = str(int(temp)) + 'hours,' + str(temp2) + 'mins'
#			else:
#				try:
#					temp = float(battery.estimated_lifetime())
#					temp2 = int(60 * (temp - int(temp)))
#					txt = str(int(temp)) + 'hours,' + str(temp2) + 'mins'
#				except ValueError:
#					txt = 'AC Online'
#			if battery.charging_state() == 2: txt = 'Charging'
#			self.msg = 1

		if battery.charging_state() == 1:
			txt = 'AC Online'
		elif battery.charging_state() == 2:
			txt = 'Charging'
		else:
			# Discharing from the battery
			if self.msg == 1:
				self.msg = 0
				txt = 'Battery'
			else:
				self.msg =1
				if batt_type == 1:
					temp2 = battery.time()
					temp = int(temp2 / 60)
					temp2 = temp2 - (temp * 60)
					txt = str(int(temp)) + 'hours,' + str(temp2) + 'mins'
				else:
					try:
						temp = float(battery.estimated_lifetime())
						temp2 = int(60 * (temp - int(temp)))
						txt = str(int(temp)) + 'hours,' + str(temp2) + 'mins'
					except ValueError:
						txt = 'Charging'

		if (self.LABEL_IN_BAR.value) == "True":
			self.percent_display.set_size_request(self.applet_width.int_value, self.applet_height.int_value)
			self.percent_display.set_text(txt)
			self.percent_display.show()
			self.battery_display.hide()
		else:
			self.percent_display.set_size_request(self.applet_width.int_value, self.applet_height.int_value - (self.text_height.int_value + 4))
			self.battery_display.set_size_request(self.applet_width.int_value, self.text_height.int_value + 4)
			self.battery_display.set_markup('<span foreground="black" size="'+ str(self.text_height.int_value) + '000">' + txt + ' </span>')		
			self.percent_display.set_text('')
			self.percent_display.show()
			self.battery_display.show()

		# if battery.charging_state() == offline_state: 
		#	if self.warned == False:
		#		if self.warn.value == 'True':
		#			if percent <= self.warn_level.int_value:
		if self.warn.value == 'True':
			if (battery.charging_state() == offline_state and percent <= self.warn_level.int_value):
				if self.warned == False:
#				if battery.charging_state() == offline_state: 
#					if percent <= self.warn_level.int_value:
					warning_dialog(title='Warning, low battery', txt='Warning. Battery is\ncurrently at ' + str(battery.percent()) + '%')
					self.warned = True
			else:
				self.warned = False

		return 1

	def percent(self):
		return str(battery.percent())
