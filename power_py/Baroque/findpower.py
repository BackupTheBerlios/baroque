#!/usr/bin/env python

'''
	findpower.py
		Finds power.py, and imports it so it is available
	to the calling Python app.
	
	Copyright 2004 rds <rds@rdsarts.com>
	
	This is beer-ware. Do what you want with it, there's no
	promises/warrenties.
'''
import sys, os

def find():
	# XXX: Version checking..

	# Try with just in and of itself.
	try:
		import power
		return
	except ImportError:
		# not in path
		pass


	# XXX: ZeroInstall

	# Incase we need it.
	sys_path = sys.path
	lib_paths = []

	try:
		libdirpath = os.environ['LIBDIRPATH']
		libdirpath = libdirpath.split(':')
		lib_paths += libdirpath
	except KeyError:
		# No LIBDIRPATH
		pass

	# Add ROX paths
	home_dir = os.environ['HOME']
	lib_paths += [home_dir + '/lib/', '/usr/local/lib', '/usr/lib']

	for path in lib_paths:
		full_path = path + '/power_py/python/power/'
		full_path = os.path.abspath(full_path)
		if os.path.exists(full_path):
			sys.path.append(full_path)
			try:
				import power
				return
			except ImportError:
				# Not there, reset path and continue
				sys.path = sys_path
				pass
		# Didn't find and import power.py, notify and exit
		print "findpower.py: Could not find power.py in path"
		raise ImportError