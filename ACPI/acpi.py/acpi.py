##############################################################################
##
## $Id: acpi.py,v 1.2 2003/06/30 19:05:06 sorgue Exp $
##
## Copyright (C) 2002-2003 Tilo Riemer <riemer@lincvs.org>
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


#enums
OFFLINE     =  0
ONLINE      =  1
CHARGING    =  2   #implies ONLINE



#exceptions

class AcpiError(Exception):
	"""Base class for APM exceptions"""
	pass


class AcpiNoDevice(AcpiError):
	"""Acpi is not configured on this host"""

	def __init__(self):
		pass

	def __str__(self):
		return "Apm is not configured on this host"


class AcpiNotImplemented(AcpiError):
	"""No implementation for this operating system"""

	def __init__(self):
		pass

	def __str__(self):
		return "No implementation for this operating system"


class AcpiNoAcpiLowLevel(AcpiError):
	"""Acpi_lowlevel module not found"""
	
	def __init__(self):
		pass

	def __str__(self):
		return "Acpi_lowlevel module not found"




#interface

class Acpi:
	"""Interface class for ACPI"""
	
	def __init__(self):
		res = sys.platform
		if res.find("freebsd4") > -1:
			self.acpi = None #throw exception (os unknown)
			raise AcpiNotImplemented

		elif res.find("netbsd1") > -1:
			self.acpi = None #throw exception (os unknown)
			raise AcpiNotImplemented
		
		elif res.find("linux2") > -1:
			self.acpi = AcpiLinux()
			
		else:
			self.acpi = None #throw exception (os unknown)
			raise AcpiNotImplemented
		

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
	




class AcpiLinux:
	def __init__(self):
		"""init ACPI class and check for batteries in /proc/acpi/battery"""

		self.proc_battery_dir = "/proc/acpi/battery"
                #self.proc_battery_dir = "/home/riemer/fix/Baroque/acpi/battery"

		batteries_dir_entries = os.listdir(self.proc_battery_dir)
		
		self.batteries = []
		for i in batteries_dir_entries:
			mode = os.stat(self.proc_battery_dir + "/" + i)[stat.ST_MODE]
			if stat.S_ISDIR(mode):
				self.batteries.append(i)
		
		self.ac_line_state = OFFLINE
		self.design_capacity = {}
		self.life_capacity = {}

		#initial reading of acpi info
		self.initialize()
		self.update()


	def initialize(self):
		"""Read /proc/acpi/battery/*/info and extract needed infos"""
		
		for i in self.batteries:
			info_file = open(self.proc_battery_dir + "/" + i + "/info")
			line = info_file.readline()
			
			while len(line) != 0:
				if line.find("design capacity") == 0:
					cap = line.split(":")[1].strip()
					self.design_capacity[i] = int(cap.split("mWh")[0].strip())					
				line = info_file.readline()
			info_file.close()
			
			
	def update(self):
		"""Read /proc/acpi/battery/*/state and extract needed infos"""
		
		for i in self.batteries:
			state_file = open(self.proc_battery_dir + "/" + i + "/state")
			line = state_file.readline()
			
			while len(line) != 0:
				if (line.find("present")==0) and (line.find("no")>0):
					self.life_capacity[i] = 0
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
					
				line = state_file.readline()
			state_file.close()
					
		
	def percent(self):
		"""Returns percentage capacity of all batteries"""
		life_capacity = 0
		design_capacity = 0
		for i in self.batteries:
			life_capacity = life_capacity + self.life_capacity[i]
			design_capacity = design_capacity + self.design_capacity[i]
		
		return (life_capacity * 100) / design_capacity


	def capacity(self):
		"""Returns capacity of all batteries"""
		capacity = 0
		for i in self.batteries:
			capacity = capacity + self.life_capacity[i]
		return capacity


	def nb_of_batteries(self):
		#returns the number of batteries
		#if it returns 0, maybe ACPI is not available or 
		#battery driver is not load
		nb = len(self.batteries)
		for i in self.batteries:
			file = open(self.proc_battery_dir + "/" + i + "/state")
			line = file.readline()
			while len(line) != 0:
				if (line.find("present")==0) and (line.find("no")>0):
					nb = nb - 1
				line = file.readline()
			file.close()
		return nb
		


	def charging_state(self):
		return self.ac_line_state
