#!/usr/bin/python

import acpi
from acpi import *

myAcpi = Acpi()
myAcpi.update()


print "fan : " + str(myAcpi.fan_state("FAN0"))
print "ac-adapter : " + str(myAcpi.charging_state())
print "nb batteries : " + str(myAcpi.nb_of_batteries())
print "charge: " + str(myAcpi.capacity())
print "percent: " + str(myAcpi.percent())
print "lifetime: " + str(myAcpi.estimated_lifetime())
print "temperature: "+ str(myAcpi.temperature("THRM"))
#print "Frequency: "+ myAcpi.frequency(0)
#print "Available freqencies: "+str(myAcpi.performance_states(0))

#print "Change to "+myAcpi.performance_states()[1]
#print "result: "+ str(myAcpi.set_frequency(myAcpi.performance_states()[1]))

