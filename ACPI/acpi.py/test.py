#!/usr/bin/python

import acpi
from acpi import *

myAcpi = Acpi()
myAcpi.update()


print "fan : " + str(myAcpi.fan_state())
print "ac-adapter : " + str(myAcpi.charging_state())
print "nb batteries : " + str(myAcpi.nb_of_batteries())
print "charge: " + str(myAcpi.capacity())
print "percent: " + str(myAcpi.percent())
print "lifetime: " + myAcpi.estimated_lifetime()
print "temperature: "+ str(myAcpi.temperature())
print "Frequency: "+ myAcpi.frequency()
print "Available freqencies: "+str(myAcpi.performance_states())

print "Change to "+myAcpi.performance_states()[1]
print "result: "+ str(myAcpi.set_frequency(myAcpi.performance_states()[1]))

