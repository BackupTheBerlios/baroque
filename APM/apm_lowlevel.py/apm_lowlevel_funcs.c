/****************************************************************************

 $Id: apm_lowlevel_funcs.c,v 1.1 2003/04/07 21:01:25 riemer Exp $

 Copyright (C) 2002-2003 Tilo Riemer <riemer@lincvs.org>
 All rights reserved. 

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions
 are met:

 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
 3. The name of the author may not be used to endorse or promote products
    derived from this software without specific prior written permission. 

 THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
 IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
 INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

****************************************************************************/



#ifdef __FreeBSD__
not implemented yet, but coming soon
#endif

/***************************************************************************/

#ifdef __NetBSD__

#define PATH_APM_DEV "/dev/apm"

#include <fcntl.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <machine/apmvar.h>


int apm_state(int* p, int* t, int* ac) //return value == error code
{
  //t  --> remaining time
  //p  --> remaining percentage
  //ac --> ac state (on|offline|charging)

  struct apm_power_info battery;
  int fd;


  *t  = 0;
  *p  = 0;
  *ac = 0;
  
  fd = open(PATH_APM_DEV, O_RDONLY);
  if (fd == -1) return -1;

  memset(&battery, 0, sizeof(battery));
  if (ioctl(fd, APM_IOC_GETPOWER,
	    &battery) == -1) {
    return -1;
  }

  *p = battery.battery_life;
  *t = battery.minutes_left;

  /* ac: 0 --> offline; 1 --> online; 2 --> charging */
  if (battery.ac_state == APM_AC_ON) *ac = 1;
  else *ac = 0;

  if (battery.battery_state == APM_BATT_CHARGING) *ac = 2;


  return 0;
}

#endif

/***************************************************************************/

#ifdef __linux__
  //if we will use a low level modul anytime we have to include apm_bios.h
  //#include <linux/apm_bios.h>
#endif

/***************************************************************************/
