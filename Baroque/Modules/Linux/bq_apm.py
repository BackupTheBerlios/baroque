##############################################################################
##
## $Id: bq_apm.py,v 1.2 2002/12/09 22:43:55 riemer Exp $
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


#implementation for Linux


import bq_consts, commands


class CApm:
	def __init__(self):
		self.apm_cmd = "apm"
		self.ac_line_state = bq_consts.OFFLINE
		
		self.life_percent = 0
		self.life_time_string = "00:00"

		#initial reading of apm info
		self.update()
	
	
	def update(self):
		#call apm and extract needed infos
		
		#we reset LC_ALL because we need the english output from apm
		res = commands.getoutput("env LC_ALL=C " + self.apm_cmd)
		#res = "AC off-line, battery status high: 100% (3:20)\n"
		
		lines = res.split("\n")
	
		#we assume all info in the first (the one and only) line
		if lines[0].find("off-line") > 0:
			self.ac_line_state = bq_consts.OFFLINE
		else:
			self.ac_line_state = bq_consts.ONLINE
			
	
		#if lines[0].find("charging") > 0:
			#print "charging"
	
		items = lines[0].split()
	
		for i in items:
			if i.find("%") > 0:
				self.life_percent = i.split("%")[0].strip()
		
			if (i.find("(") > -1) and (i.find(":") > 0) and (i.find(")") > 0):
				self.life_time_string = i.split("(")[1].split(")")[0].strip()
		
	
	def percent(self):
		#returns percentage capacity of all batteries
		return self.life_percent
		
		
	def capacity_or_time_string(self):
		#returns time string of all batteries
		return self.life_time_string
	
	
	def charging_state(self):
		return self.ac_line_state
	