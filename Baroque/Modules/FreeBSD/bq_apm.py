##############################################################################
##
## $Id: bq_apm.py,v 1.2 2002/12/15 22:53:02 riemer Exp $
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


#implementation for FreeBSD

import bq_consts, commands


class CApm:
	def __init__(self):
		self.apm_cmd = "/usr/sbin/apm"
		self.ac_line_state = bq_consts.OFFLINE
		
		self.life_percent = 0
		self.life_time_string = "00:00"

		#initial reading of apm info
		self.update()
	
	
	def update(self):
		#call apm and extract needed infos
		percent_sum_found = 0
		time_sum_found    = 0
		
		#we reset LC_ALL because we need the english output from apm
		res = commands.getoutput("env LC_ALL=C " + self.apm_cmd)
		lines = res.split("\n")
		for i in lines:
			if not percent_sum_found and (i.find("battery life") > 0):
				percent_sum_found = 1
				self.life_percent = int(i.split(":")[1].split("%")[0].strip())
				
			if not time_sum_found and (i.find("battery time") > 0):
				time_sum_found = 1
				life_res = i.split(": ")[1].split(":")
				self.life_time_string = life_res[0] + ":" + life_res[1]
	
			if i.find("off-line") > 0:
				self.ac_line_state  = bq_consts.OFFLINE
			elif i.find("on-line") > 0:
				self.ac_line_state  = bq_consts.ONLINE
		
	
	def percent(self):
		#returns percentage capacity of all batteries
		return self.life_percent
		
		
	def capacity_or_time_string(self):
		#returns time string of all batteries
		return self.life_time_string
	
	
	def charging_state(self):
		return self.ac_line_state
