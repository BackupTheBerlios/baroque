#!/usr/bin/env python

import sys

sys.path.append("./")
sys.path.append("../")

import bq_acpi

print "loaded"

acpi = bq_acpi.CAcpi()

print acpi.nb_of_batteries()
print "State", acpi.charging_state()

acpi.update()

print "Prozent", acpi.percent()
print "Kapazität", acpi.capacity()
print  "State", acpi.charging_state()
