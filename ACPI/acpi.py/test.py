#!/usr/bin/python

import power 
from power import *

myAcpi = Power()
myAcpi.update()



try:
	print "number of fans : " + str(myAcpi.nb_of_fans())
	for I in range(myAcpi.nb_of_fans()):
		print 'fan ' + str(I) + ': ' + str(myAcpi.fan_state(0))
except:
	print "fan : None detected."

print "ac-adapter : " + str(myAcpi.charging_state())

if myAcpi.nb_of_batteries() > 0:
	print "Number of batteries : " + str(myAcpi.nb_of_batteries())
	print "charge: " + str(myAcpi.capacity())
	print "percent: " + str(myAcpi.percent())
	print "lifetime: " + str(myAcpi.estimated_lifetime())
else:
	print "No batteries detected."

print myAcpi.power.abilities

print "TODO: Add number of thermal zones module."
# print "# thermal zones: " + str(myAcpi.nb_of_temperatures())
# print "temperature: "+ str(myAcpi.temperature(0))

# print "Frequency: "+ myAcpi.frequency(0)
# print "Available freqencies: "+str(myAcpi.performance_states(0))

# print "Change to "+myAcpi.performance_states()[1]
# print "result: "+ str(myAcpi.set_frequency(myAcpi.performance_states()[1]))
