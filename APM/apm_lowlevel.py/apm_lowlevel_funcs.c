/****************************************************************************

 $Id: apm_lowlevel_funcs.c,v 1.2 2003/04/10 22:17:29 riemer Exp $

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

/* Just to be a bit more clear... */
enum {
  BATTERY_AC_OFF,      /* The computer is running off the battery. */
  BATTERY_AC_ON,       /* Fully charged battery and computer running
                          off AC power. */
  BATTERY_CHARGING,    /* The computer is running off AC power but the
                          battery isn't fully charged yet. */
  BATTERY_NO_BATTERY   /* This is a desktop system or there is not a
                          battery in the computer battery bay. */
} battery_states;

#define BATTERY_VALUE_UNKNOWN    -1 /* When the value is not known or it
                                       simply does not matter. */

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

#if (defined __APPLE__) || (defined __DARWIN__)

#include <stdio.h>
#include <errno.h>
#include <Carbon/Carbon.h>
#include <IOKit/pwr_mgt/IOPMLib.h>
#include <IOKit/pwr_mgt/IOPM.h>
#include <IOKit/ps/IOPowerSources.h>
#include <IOKit/ps/IOPSKeys.h>
#include <mach/mach.h>

int apm_state(int* p, int* t, int* ac) 
{
  mach_port_t master_port;
  CFArrayRef battery_data;
  CFTypeRef power_source;
  CFDictionaryRef power_source_data;
  int max_capacity;
  int current_capacity;
  int battery_flags;
  IOReturn result;
  kern_return_t err;

  err = IOMasterPort(MACH_PORT_NULL, &master_port);
  if (err != kIOReturnSuccess) return err;
  battery_data = CFArrayCreateMutable(NULL, 0, &kCFTypeArrayCallBacks);
  if (battery_data == NULL) return ENOMEM;
  *t = BATTERY_VALUE_UNKNOWN;
  *p = BATTERY_VALUE_UNKNOWN;
  *ac = BATTERY_NO_BATTERY;
  result = IOPMCopyBatteryInfo(master_port, &battery_data);
  if (result != kIOReturnSuccess) {
    /* No battery present */
    CFRelease(battery_data);
    return 0;
  }
  CFNumberGetValue(CFDictionaryGetValue(CFArrayGetValueAtIndex(
    (CFArrayRef)battery_data, 0), CFSTR("Flags")), kCFNumberSInt32Type,
    &battery_flags);
  CFNumberGetValue(CFDictionaryGetValue(CFArrayGetValueAtIndex(
    (CFArrayRef)battery_data, 0), CFSTR("Current")), kCFNumberSInt32Type,
    &current_capacity);
  CFNumberGetValue(CFDictionaryGetValue(CFArrayGetValueAtIndex(
    (CFArrayRef)battery_data, 0), CFSTR("Capacity")), kCFNumberSInt32Type,
    &max_capacity);
  if (!(battery_flags & kIOPMBatteryInstalled)) {
    /* No battery present */
    CFRelease(battery_data);
    return 0;
  }
  CFRelease(battery_data);
  /* 
   * At this point we're pretty sure this is a battery powered device,
   * but there might be more than a single power source. My iBook only
   * has only one of those and I haven't got anything else to test this
   * code on.
   *
   * Another issue is that Mac OS X (v10.2.4 at least) returns -1 for
   * the various timing/percentage values until it has calculated how
   * much battery left to use / charge.
   */
  power_source = IOPSCopyPowerSourcesInfo();
  power_source_data = IOPSGetPowerSourceDescription(power_source,
    CFArrayGetValueAtIndex(IOPSCopyPowerSourcesList(power_source), 0));
  if (battery_flags & kIOPMBatteryCharging) {
    *ac = BATTERY_CHARGING;
    /*
     * I don't know how the *BSD APM implementation works, but I assume the
     * time value returned when the battery is charging means the time left
     * for the battery to fully charged.
     */
    *p = (int)(100.0f * ((float)current_capacity / (float)max_capacity));
    CFNumberGetValue(CFDictionaryGetValue(power_source_data,
      CFSTR(kIOPSTimeToFullChargeKey)), kCFNumberSInt32Type, t);
  } else if (battery_flags & kIOPMACInstalled) {
    *p = 100;
    *ac = BATTERY_AC_ON;
  } else {
    *ac = BATTERY_AC_OFF;
    *p = (int)(100.0f * ((float)current_capacity / (float)max_capacity));
    CFNumberGetValue(CFDictionaryGetValue(power_source_data,
      CFSTR(kIOPSTimeToEmptyKey)), kCFNumberSInt32Type, t);
  }
  CFRelease(power_source);
  return 0;
}

#endif

/***************************************************************************/
