#!/usr/bin/python3

import subprocess

def do(command, options={}):
	""" run `command *options` in bash """
	command = 'uvspec'
	for option in options:
		command += ' '
		command += '{}={}'.format(option, options[option])
	result = subprocess.run(command, shell=True)
	return result.returncode


def uvspec(options={}):
	return do('uvspec', options)


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
