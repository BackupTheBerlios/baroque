##############################################################################
##
## $Id: bq_acpi.py,v 1.5 2002/12/09 22:43:55 riemer Exp $
##
## Copyright (C) 2002 Tilo Riemer <riemer@lincvs.org>
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

import bq_consts, os, stat

proc_battery_dir = "/proc/acpi/battery"
#proc_battery_dir = "/home/riemer/fix/Baroque/acpi/battery"

class CAcpi:
	def __init__(self):
		#init ACPI class and check for batteries in /proc/acpi/battery
		batteries_dir_entries = os.listdir(proc_battery_dir)
		
		self.batteries = []
		for i in batteries_dir_entries:
			mode = os.stat(proc_battery_dir + "/" + i)[stat.ST_MODE]
			if stat.S_ISDIR(mode):
				self.batteries.append(i)
		
		self.ac_line_state = bq_consts.OFFLINE
		self.design_capacity = {}
		self.life_capacity = {}

		#initial reading of acpi info
		self.initialize()
		self.update()


	def initialize(self):
		#read /proc/acpi/battery/*/info and extract needed infos
		for i in self.batteries:
			info_file = open(proc_battery_dir + "/" + i + "/info")
			line = info_file.readline()
			
			while len(line) != 0:
				if line.find("design capacity") == 0:
					cap = line.split(":")[1].strip()
					self.design_capacity[i] = int(cap.split("mAh")[0].strip())
					break
					
				line = info_file.readline()
			info_file.close()
			
			
	def update(self):
		#read /proc/acpi/battery/*/state and extract needed infos
		for i in self.batteries:
			state_file = open(proc_battery_dir + "/" + i + "/state")
			line = state_file.readline()
			
			while len(line) != 0:
				if line.find("remaining capacity") == 0:
					cap = line.split(":")[1].strip()
					self.life_capacity[i] = int(cap.split("mAh")[0].strip())
					
				#a little bit tricky... if loading of ac driver fails, we cant use info
				#from /proc/ac_*/...
				#if information in /proc/acpi/battery/*/state is wrong we had to
				#track the capacity history.
				#I asume that all battery state file get the same state.
				if line.find("charging state") == 0:
					state = line.split(":")[1].strip()
					if state == "discharging":
						self.ac_line_state = bq_consts.OFFLINE
					elif state == "charging":
						self.ac_line_state = bq_consts.CHARGING
					else:
						self.ac_line_state = bq_consts.ONLINE
					
				line = state_file.readline()
			state_file.close()
			
		
	def percent(self):
		#returns percentage capacity of all batteries
		life_capacity = 0
		design_capacity = 0
		for i in self.batteries:
			life_capacity = life_capacity + self.life_capacity[i]
			design_capacity = design_capacity + self.design_capacity[i]
		
		return (life_capacity * 100) / design_capacity


	def capacity(self):
		#returns capacity of all batteries
		capacity = 0
		for i in self.batteries:
			capacity = capacity + self.life_capacity[i]
			
		return capacity


	def capacity_or_time_string(self):
		#returns capacity string of all batteries
		return str(self.capacity()) + " mAh"


	def nb_of_batteries(self):
		#returns the number of batteries
		#if it returns 0, maybe ACPI is not available or 
		#battery driver is not load
		return len(self.batteries)
		

	def charging_state(self):
		return self.ac_line_state
