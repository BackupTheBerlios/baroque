import os,stat,sys

# For raising ERR_NOT_IMPLEMENTED
from default_class import *

VERSION      = "0.3.1"

class Power(object):
	"""Interface class for ACPI"""
	
	def __init__(self):
		self.power = None

		res = sys.platform
		if res.find("linux2") > -1 or res.find("linux") > -1:
			# some systems return linux instead of linux2. We should
			# show a warning or check by ourselves for Linux2
			try:
				# Attempt to load /proc-based ACPI implimentation
				import linux_acpi
				self.power = linux_acpi.AcpiLinuxProc()
			except:
				# XXX: Try /sys ACPI.
					# All searches for ACPI-based power management failed. Try APM
					try:
						import linux_apm
						self.power = linux_apm.ApmLinux()
					except:
						self.power = None
						raise PowerError, ERR_NOT_IMPLEMENTED
		elif res.find("freebsd4") > -1:
			raise PowerError, ERR_NOT_IMPLEMENTED
		elif res.find("netbsd1") > -1:
			raise PowerError, ERR_NOT_IMPLEMENTED

		else:
			raise PowerError, ERR_NOT_IMPLEMENTED
		

	def identity(self):
		"""Returns the identity of this module"""
		try:
			return self.power.indentity()
		except:
			return "acpi.py"
		
	def version(self):
		# Returns the version of this module
		# XXX: Return version of acpi.py and acpi as tuple.
		try:
			return(VERSION, self.power.version)
		except:
			# self.power does not have a version method, or we do not have a self.power.
			if self.power:
				return(VERSION, 'unknown')
			return(VERSION, 'unknown (no power management system found)')
		
	def update(self):
		# Updates the ACPI state
		self.power.update()

	def percent(self):
		# Returns percentage capacity of all batteries
		return self.power.percent()

	def capacity(self):
		# Returns capacity of all batteries
		return self.power.capacity()

	def nb_of_batteries(self):
		# Returns the number of batteries
		return self.power.nb_of_batteries()
	
	def nb_of_fans(self):
		# Returns number of fans found as a integer
		return self.power.nb_of_fans()

	def charging_state(self):
		# Returns ac state (off-/online/charging)
		return self.power.charging_state()
	
	def estimated_lifetime(self):
		"""Returns Estimated Lifetime as real number"""
		return self.power.estimated_lifetime()

	def temperature(self, idx):
		"""Returns Processor Temperature"""
		return self.power.temperature(idx)

	def fan_state(self, idx):
		"""Returns fan states"""
		return self.power.fan_state(idx)

#unfinished: don't use it or better send us improvements ;-) ###########################################################
	def frequency(self, idx):
		""" Return  the frequency of the processor"""
		return self.power.frequency(idx)

	def performance_states(self, idx):
		""" Return a list of available frequencies for the proc """
		return self.power.performance_states(idx)

	def set_frequency(self, freq):
		""" Set the processor frequency - Warning ! Needs root privileges to work """
		return self.power.set_frequency(freq)