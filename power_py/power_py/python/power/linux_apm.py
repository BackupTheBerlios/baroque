import sys, os, stat
from default_class import *

# For exceptions:
from default_class import PowerError as AcpiError

class ApmLinux(DefaultClass):
	# APM class for Linux 2.2 and above,
	def __init__(self, apm_path = '/proc/apm'):
		# init APM class. Call with a alternate path if /proc/apm is not the location of the APM info.
		self.apm_path = apm_path

		# Will run inits on everything and call update()
		DefaultClass.__init__(self)

	def update(self):
		# XXX: This will eventually be replaced by DefaultClass.
		self.update_batteries()

	def update_batteries(self):
		# Tries to read info from 'apm_path.'
		try:
			apm_proc = open(self.apm_path)
		except IOError:
			# APM path doesn't exist. Raise exception and exit
			raise PowerError, ERR_NO_DEVICE
			return False

		line = apm_proc.readline()
		token = line.split()
		if token[3] == "0x00":
			self.ac_line_state = OFFLINE
		elif token[4] == "0x03":
			self.ac_line_state = CHARGING
		else:
			self.ac_line_state = ONLINE

		self.life_percent = int(token[6].split("%")[0])

		self.life_time = int(token[7])

		apm_proc.close()

	def init_batteries(self):
		# Set globals for battery-information
		self.life_percent = 0
		self.life_time = 0
		self.ac_line_state = OFFLINE

# TODO: Change following to get_* in specs and here.
	def percent(self):
		return self.life_percent

	def time(self):
		time = self.life_time
		hour = int(time / 60)
		min = time - (hour * 60)
		return hour, min

	def charging_state(self):
		return self.ac_line_state
