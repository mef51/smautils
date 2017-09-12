#!/usr/bin/python3

import subprocess

def do(command, options={}):
	""" run `command *options` in bash """
	for option in options:
		command += ' '
		command += '{}={}'.format(option, options[option])
	# print(command)
	result = subprocess.run(command, shell=True)
	result.check_returncode()
	return result.returncode

def uvspec(options={}):
	return do('uvspec', options)

def imspec(options={}):
	return do('imspec', options)

def cgcurs(options={}):
	return do('cgcurs', options)

def uvaver(options={}):
	return do('uvaver', options)

def uvcat(options={}):
	return do('uvcat', options)

def uvsort(options={}):
	return do('uvsort', options)

def selfcal(options={}):
	return do('selfcal', options)

def gpplt(options={}):
	return do('gpplt', options)

def gpcopy(options={}):
	return do('gpcopy', options)

def invert(options={}):
	return do('invert', options)

def cgdisp(options={}):
	return do('cgdisp', options)

def clean(options={}):
	return do('clean', options)

def restor(options={}):
	return do('restor', options)

def cgdisp(options={}):
	return do('cgdisp', options)

def imstat(options={}):
	return do('imstat', options)

def maxfit(options={}):
	return do('maxfit', options)

def maths(options={}):
	return do('maths', options)

if __name__ == '__main__':
	uvspec({
		'vis'      : 'UVDATA/orkl_080106.usb,UVOffsetCorrect/orkl_080106.usb.corrected.slfc',
		'device'   : '1/xs',
		'interval' : 9999,
		'options'  : 'avall,nobase',
		'nxy'      : '1,2',
		'stokes'   : 'v',
		'axis'     : 'chan,amp',
		'line'     : 'chan,48,1,64.0',
		'device'   : '2/xs'
	})
