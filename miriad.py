#!/usr/bin/python3

import subprocess, shlex, os
import matplotlib.pyplot as plt
import plawt

def do(command, options={}, stdout=None):
	""" run `command *options` in bash """
	for option in options:
		command += ' '
		command += '{}={}'.format(option, shlex.quote(str(options[option])))
	# print(command)
	result = subprocess.run(command, shell=True, stdout=stdout)
	result.check_returncode()
	return result

def averageLine(numChannels, factor=16):
	"""
	Utility to get the line option needed for Miriad in order
	to average the channels together.
	For example if I want to average every four channels given that there are
	6144 channels I need to do this in miriad:
	`uvspec vis=... line='chan,1536,1,4'

	Given `numChannels` and `factor` (the number of channels to combine)
	this will return 'chan,numChannels/factor,1,factor'.

	You can get the number of channels in an observation using `uvlist`.
	"""
	return 'chan,{},1,{}'.format(numChannels/factor, factor)

def getNumChannels(vis, options={}):
	""" Parse the number of channels out of `uvlist`s output """
	options['vis'] = vis
	result = uvlist(options, stdout=subprocess.PIPE)
	result = str(result.stdout).split('\\n')[3]
	return int(result[result.find(':')+1:result.find(',')])

def getVelocityRange(vis, options={}):
	"""
	Parse the velocity range from uvlist.
	Useful when resampling and re-binning data in `line` selections

	Returns a tuple of the form (starting velocity, end velocity)
	"""
	options['vis'] = vis
	options['options'] = 'spec'

	specdata = uvlist(options, stdout=subprocess.PIPE).stdout
	specdata = str(specdata)

	# starting velocity
	startvel = specdata[specdata.find('starting velocity'):]
	startvel = startvel[startvel.find(':')+1:startvel.find('\\n')].split()[0]

	# ending velocity
	endvel = specdata[specdata.rfind('ending velocity'):]
	endvel = endvel[endvel.find(':')+1:endvel.find('\\n')].split()[-1]

	return (float(startvel), float(endvel))

def showChannels(vis, options={}, freq=False):
	"""
	Dump visibility data and plot it with a matplotlib window.
	The matplotlib window has better mouse controls and helps
	with selecting channel numbers.

	Data is from Miriad's uvspec with stokes=i, axes=chan,amp, interval=9999
	and options=avall,nobase

	set `freq` to true to have the x-axis be frequency instead of channels
	"""
	options['vis']      = vis
	options['stokes']   = 'i'
	options['options']  = 'avall,nobase'
	options['axis']     = 'freq,amp' if freq else 'chan,amp'
	options['interval'] = 9999

	filename = '__{}_uvspec.dat'.format(vis.split('/')[0])
	options['log'] = filename

	chans = []
	amps = []

	uvspec(options) # miriad will leave us a file with the data
	with open(filename, 'r') as file:
		data = file.readlines()

	for line in data:
		pair = line.split()
		chans.append(float(pair[0]))
		amps.append(float(pair[1]))

	os.remove(filename)

	fig = plawt.plot({
		0: {'x': chans, 'y': amps, 'draw': 'steps-mid', 'line': 'k'},
		'xlabel': 'Frequency' if freq else 'Channel',
		'ylabel': 'Amplitude',
		'title': vis,
		'keepOpen': True
	})

	print('Click to print channel number:')
	def onclick(e):
		print(round(e.xdata))

	cid = fig.canvas.mpl_connect('button_press_event', onclick)
	plt.show()
	fig.canvas.mpl_disconnect(cid)

def uvspec(options={}):
	return do('uvspec', options)

def smauvspec(options={}):
	return do('smauvspec', options)

def smauvplt(options={}):
	return do('smauvplt', options)

def imspec(options={}):
	return do('imspec', options)

def cgcurs(options={}):
	return do('cgcurs', options)

def uvaver(options={}):
	return do('uvaver', options)

def uvflag(options={}):
	return do('uvflag', options)

def uvputhd(options={}):
	return do('uvputhd', options)

def uvredo(options={}):
	return do('uvredo', options)

def uvlist(options={}, stdout=None):
	return do('uvlist', options, stdout=stdout)

def uvlin(options={}):
	return do('uvlin', options)

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
