from sys import stderr

# ENUMS ####################################
# should be imported by every subclass.
OFFLINE      =  0
ONLINE       =  1
CHARGING     =  2   #implies ONLINE
FAN_OFF      =  0
FAN_ON       =  1

ERR_GENERIC               = -1
ERR_NO_DEVICE             = -2
ERR_NOT_IMPLEMENTED       = -3
ERR_NO_LOW_LEVEL          = -4
ERR_CONFIGURATION_CHANGED = -5   #reload module? or function reconfigure?
ERR_NOT_ALLOWED           = -6   #access for some resource not allowed --> better idea?

class PowerError(Exception):
	"""Generic exceptions. Should be imported"""

	def __init__(self, errno = ERR_GENERIC):
		# If no errno is provided, default to ERR_GENERIC
		self.errno = errno

	def __str__(self):
		if self.errno == ERR_GENERIC:
			return "Any ACPI error occured."
		elif self.errno == ERR_NO_DEVICE:
			return "ACPI is not configured on this host."
		elif self.errno == ERR_NOT_IMPLEMENTED:
			return "No implementation for this operating system."
		elif self.errno == ERR_NO_LOW_LEVEL:
			return "Acpi_lowlevel module not found."
		elif self.errno == ERR_CONFIGURATION_CHANGED:
			return "ACPI configuartion has been changed."
		else:
			return "Unknown error occured."

class DefaultClass(object):
	"""
		This is a default class for power management. 
		All others should sub-class it to inherit needed defaults.
	"""

	def __init__(self):
		"""Just sets up the class-globals. Subclass should call update!"""
		self.abilities = ['battery', 'fan', 'processor', 'temperature']
		self.init_all()

	def init_all(self):
		#Initializes all routines for power management.
		self.init_batteries()
		self.init_fans()
		self.init_processors()
		self.init_temperatures()

		self.update()

	def update(self):
		# Updates all entries in 'self.abilities.' Raises appropriate exceptions if anything interesting has changed.
		for ability in self.abilities:
			if ability == 'battery':
				self.update_batteries()
			elif ability == 'fan':
				self.update_fans()
			elif ability == 'processor':
				self.update_processors()
			elif ability == 'temperture':
				self.update_temperture()

	def get_has_ability(self, ability):
		"""Returns if we have ability 'ability' in class-global 'self.abilities' list."""
		return self.get_index_of_ability(ability)

	def delete_ability(self, ability):
		"""Deletes ability ability from 'self.abilities.' Returns True if we had it in the class-global list."""
		temp = self.get_index_of_ability(ability)
		if temp:
			# XXX: Here for debugging.
			# print >>stderr, 'WARNING: removing ability %s.'%self.abilities[temp]
			del self.abilities[temp]
			return True
		# XXX: Here for debugging.
		print >>stderr, 'power.py: (DEBUG WARNING)Attempted to remove ability %s, but it was not in our global abilities.'%ability
		return False

	def get_index_of_ability(self, ability):
		"""Returns the index of ability 'ability' in class-global list 'self.abilities.' """
		for x in range(len(self.abilities)):
			if self.abilities[x] == ability:
				return x

# Default methods: #################################################################

# These remove abilities from global list, which you should check against when 

	def init_batteries(self):
		self.delete_ability('battery')

	def init_fans(self):
		self.delete_ability('fan')

	def init_processors(self):
		self.delete_ability('processor')

	def init_temperatures(self):
		self.delete_ability('temperature')
