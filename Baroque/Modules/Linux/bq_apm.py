##############################################################################
##
## $Id: bq_apm.py,v 1.1 2002/12/02 16:47:59 riemer Exp $
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

import bq_consts


class CApm:
	def __init__(self, apm_command):
		self.apm_cmd = apm_command
		self.ac_line_state = bq_consts.OFFLINE
		self.cur_warn_level = bq_consts.WARN_LEVEL
		self.alert_state = 0	#warn me if alert_state == 1
		
		self.life_percent = "0%"
		self.life_time = "00:00"

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
			self.cur_warn_level = bq_consts.WARN_LEVEL
			self.ac_line_state = bq_consts.ONLINE
			
	
		#if lines[0].find("charging") > 0:
			#print "charging"
	
		items = lines[0].split()
	
		for i in items:
			if i.find("%") > 0:
				self.life_percent = i
		
			if (i.find("(") > -1) and (i.find(":") > 0) and (i.find(")") > 0):
				self.life_time = i.split("(")[1].split(")")[0]
			
		#we do nothing return, the caller ask the class for life_* and states
		
	
	def check_capacity(cap):
		#check if capacity is less than WARN_LEVEL
		#note that cap has to be a string ("x%")
		cap_val = int(cap.split("%")[0])
	
		if self.alert_state == 0:
			if (cap_val < self.cur_warn_level) and (self.ac_line_state == OFFLINE):
				self.alert_state = 1
				self.cur_warn_level = self.cur_warn_level * 2 / 3	 #decrease warn level
		elif alert_state == 2:
			alert_state = 0
				
	