##############################################################################
##
## $Id: acpi.py,v 1.12 2003/08/18 09:08:57 riemer Exp $
##
## Copyright (C) 2002-2003 Tilo Riemer <riemer@lincvs.org>
##                     and Luc Sorgue  <luc.sorgue@laposte.net>
## All rights reserved. 
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
## THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
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

import os,stat,sys


# genenal constants ###########################################################

#enums
OFFLINE      =  0
ONLINE       =  1
CHARGING     =  2   #implies ONLINE
FAN_OFF      =  0
FAN_ON       =  1
FREQ_CHANGED =  1
ERROR        =  0



# exceptions ##################################################################

#exception enums
ERR_GENERIC               = -1
ERR_NO_DEVICE             = -2
ERR_NOT_IMPLEMENTED       = -3
ERR_NO_LOW_LEVEL          = -4
ERR_CONFIGURATION_CHANGED = -5   #reload module? or function reconfigure?
ERR_NOT_ALLOWED           = -6   #access for some resource not allowed --> better idea?

class AcpiError(Exception):
	"""ACPI exceptions"""

	def __init__(self, errno):
		self.errno = errno

	def __str__(self):
		if self.errno == ERR_GENERIC:
			return "Any ACPI error occured."
		elif self.errno == ERR_NO_DEVICE:
			return "ACPI is not configured on this host."
		elif self.errno == ERR_NOT_IMPLEMENTED:
			return "No implementation for this operating system."
		elif self.errno == ERR_NO_LOW_LEVEL:
			return "Acpi_lowlevel module not found."
		elif self.errno == ERR_CONFIGURATION_CHANGED:
			return "ACPI configuartion has been changed."
		else:
			return "Unknown error occured."



# interface ###################################################################

class Acpi:
	"""Interface class for ACPI"""
	
	def __init__(self):
		res = sys.platform
		if res.find("freebsd4") > -1:
			self.acpi = None #throw exception
			raise AcpiError, ERR_NOT_IMPLEMENTED

		elif res.find("netbsd1") > -1:
			self.acpi = None #throw exception
			raise AcpiError, ERR_NOT_IMPLEMENTED
		
		elif res.find("linux2") > -1:
			self.acpi = AcpiLinux()
			
		elif res.find("linux") > -1:
			#some systems return linux instead of linux2. We should
			#show a warning or check by ourselves for Linux2
			self.acpi = AcpiLinux()
			
		else:
			self.acpi = None #throw exception (os unknown)
			raise AcpiError, ERR_NOT_IMPLEMENTED
		

	def update(self):
		"""Updates the ACPI state"""
		self.acpi.update()

	def percent(self):
		"""Returns percentage capacity of all batteries"""
		return self.acpi.percent()

	def capacity(self):
		"""Returns capacity of all batteries (in mWh)"""
		return self.acpi.capacity()

	def nb_of_batteries(self):
		"""Returns the number of batteries"""
		return self.acpi.nb_of_batteries()

	def charging_state(self):
		"""Returns ac state (off-/online/charging)"""
		return self.acpi.charging_state()
	
	def estimated_lifetime(self):
		"""Returns Estimated Lifetime"""
		return self.acpi.estimated_lifetime()


#ab hier pro Lüfter/Processor etc.?
	def temperature(self):
		"""Returns Processor Temperature"""
		return self.acpi.temperature()

	def fan_state(self):
		"""Returns fan states"""
		return self.acpi.fan_state()

	def frequency(self):
		""" Return  the frequency of the processor"""
		return self.acpi.frequency()

	def performance_states(self):
		""" Return a list of available frequencies for the proc """
		return self.acpi.performance_states()

	def set_frequency(self,f):
		""" Set the processor frequency - Warning ! Needs root privileges to work """
		return self.acpi.set_frequency(f)



# implementation for Linux ####################################################

class AcpiLinux:
	def __init__(self):
		"""init ACPI class and check for any ACPI features in /proc/acpi/"""

		self.init_batteries()
		#self.init_fans()
		#self.init_processors()

		self.update()


	def update(self):
		"""Read current states of supported acpi components"""

		self.update_batteries()
		#self.update_fans()
		#self.update_processors()


        #battery related functions
	def init_batteries(self):
		"""Checks for and initializes the batteries"""

		self.proc_battery_dir = "/proc/acpi/battery"
		#self.proc_battery_dir = "/home/riemer/fix/Baroque/acpi/battery"

                #empty lists implies no battery, no capacity etc.
		self.design_capacity = {}
		self.life_capacity = {}
		self.present_rate = {}

		#empty list of battery sub directories; implies no batteries available
		self.battery_dir_entries = []

		try:
			battery_dir_entries = os.listdir(self.proc_battery_dir)
		except OSError:
			self.ac_line_state = ONLINE  # no batteries: we assume that a cable is plugged in ;-)
			return   #nothing more to do
			

		try:
			for i in battery_dir_entries:
				mode = os.stat(self.proc_battery_dir + "/" + i)[stat.ST_MODE]
				if stat.S_ISDIR(mode):
					self.battery_dir_entries.append(i)
		except OSError:
			raise AcpiError, ERR_GENERIC
		
		
		self.ac_line_state = OFFLINE

		try:
			for i in self.battery_dir_entries:
				info_file = open(self.proc_battery_dir + "/" + i + "/info")
				line = info_file.readline()
			
				while len(line) != 0:
					if line.find("last full capacity:") == 0:
						cap = line.split(":")[1].strip()
						self.design_capacity[i] = int(cap.split("mWh")[0].strip())					
						line = info_file.readline()
					info_file.close()
		except IOError:
			# generic error or reconfigure? (if just in this moment the battery driver is unloaded)
			raise AcpiError, ERR_GENERIC



	def update_batteries(self):
		"""Read current state of batteries"""

		try:
			for i in self.battery_dir_entries:
				state_file = open(self.proc_battery_dir + "/" + i + "/state")
				line = state_file.readline()

				while len(line) != 0:
					if line.find("remaining capacity") == 0:
						cap = line.split(":")[1].strip()
						self.life_capacity[i] = int(cap.split("mWh")[0].strip())
						
					#a little bit tricky... if loading of ac driver fails, we cant use info
					#from /proc/ac_*/...
					#if information in /proc/acpi/battery/*/state is wrong we had to
					#track the capacity history.
					#I asume that all battery state files get the same state.
					if line.find("charging state") == 0:
						state = line.split(":")[1].strip()
						if state == "discharging":
							self.ac_line_state = OFFLINE
						elif state == "charging":
							self.ac_line_state = CHARGING
						else:
							self.ac_line_state = ONLINE

					# Read the present energy consumption to 
					# estimate life time 

					if line.find("present rate:") == 0:
						pr_rate = float(line.split(":")[1].strip().split("mW")[0].strip())
						self.present_rate[i] = pr_rate

					line = state_file.readline()
					state_file.close()
		except IOError:
			raise AcpiError, ERR_CONFIGURATION_CHANGED


	def init_temperatures(self):
		"""Initializes temperature stuff"""

		self.temperatures = {}

		try:
			# Read /proc/acpi/thermal_zone/*
			for i in  os.listdir("/proc/acpi/thermal_zone"):
				self.temperatures[i] = "0"
		except OSError:
			self.temperatures = {}   #reset list --> should we throw an exception
			return


	def update_temperatures(self):
		"""Read current temperatures"""
		
			
		# Update processor temperature
#so natuerlich quatsch: da muss ja dann der dateiname drinnenstehen!!!
		for i in  self.temperatures:
			#here we should use try/except
			file = open("/proc/acpi/thermal_zone/"+i+"/temperature")
			line = file.readline()
			while len(line) != 0:
				if line.find("temperature") == 0:
					self.temperatures[i] = line.split(":")[1].strip()
				line = file.readline()

			
	def init_fans(self):
		"""Initialize fans"""
		
		self.fans = {}

		try:
			# Read /proc/acpi/fan/*
			for i in os.listdir("/proc/acpi/fan"):
				self.fans[i] = "off"
		except OSError:
			#no fan support
			self.fans = {}   #reset list --> should we throw an exception
			return
		

	def update_fans(self):
		"""Read current state of fans"""
		
		for i in os.listdir("/proc/acpi/fan"):
			file = open("/proc/acpi/fan/"+i+"/state")
			line = file.readline()
                        while len(line) != 0:
                                if line.find("status") == 0:
					if line.split(":")[1].strip() == 'on':
						self.fans[i] = FAN_ON
					else:
						self.fans[i] = FAN_OFF
					line = file.readline()


	def init_processors(self):
		"""Initialize processors"""

		#at the moment only the first processor is supported?

		self.perf_states = {}   #empty list implies no processor support
		
		try:
			# Read processor info
			self.processor = os.listdir("/proc/acpi/processor")[0]
		except OSError:
			#no prcessor support
			return

		try:
			f = open("/proc/acpi/processor/"+self.processor+"/performance")
		except IOError:
			self.perf_states = {}   #reset list --> should we throw an exception
			return
			
		l = f.readline()
		while(len(l)!=0):
			if l.find("MHz") > -1:
				state = l.split(":")[0].strip().split("P")[-1]
				freq = l.split(":")[1].split(",")[0].strip()
				self.perf_states[freq] = state
			l = f.readline()


	def update_processors(self):
		"""Read current state of processors"""

		pr = os.listdir("/proc/acpi/processor")[0]
		f = open("/proc/acpi/processor/"+pr+"/performance","r")
		l = f.readline()
		while(len(l)!=0):
			if l.find("*") > -1:
				self.freq = l.split(":")[1].strip().split(",")[0]
			l = f.readline()
		f.close()


	def percent(self):
		"""Returns percentage capacity of all batteries"""

		if self.nb_of_batteries() == 0:
			return 0

		life_capacity = 0
		design_capacity = 0
		for i,c in self.life_capacity.items():
			life_capacity = life_capacity + c
			design_capacity = design_capacity + self.design_capacity[i]
		
		return (life_capacity * 100) / design_capacity


	def capacity(self):
		"""Returns capacity of all batteries"""
		capacity = 0
		for i,c in self.life_capacity.items():
			capacity = capacity + c
		return capacity


	def nb_of_batteries(self):
		#returns the number of batteries
		#if it returns 0, maybe ACPI is not available or 
		#battery driver is not load
		return len(self.life_capacity)

		
	def charging_state(self):
		return self.ac_line_state


	def estimated_lifetime(self):
		time = 0
		for batt,life_capacity in self.life_capacity.items():
			if self.present_rate[batt] == 0:
				return "charging"
			time = time + life_capacity/self.present_rate[batt]
		return str(time)


	def temperature(self):
		return self.temp


	def fan_state(self):
		return self.fans


	def performance_states(self):
		return self.perf_states.keys()


	def frequency(self):
		return self.freq


	def set_frequency(self,f):
	#I think we should throw exceptions if someone goes wrong here
	
		if self.perf_states.has_key(f):
			state = self.perf_states[f]
			try:
				pr = os.listdir("/proc/acpi/processor")[0]
			except OSError:
				raise AcpiError, ERR_NOT_ALLOWED

			try:				
				f = open("/proc/acpi/processor/"+pr+"/performance","w")
			except IOError:
				raise AcpiError, ERR_NOT_ALLOWED
				
			f.write(state)
			f.close()
