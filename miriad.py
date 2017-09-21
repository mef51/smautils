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

def averageVelocityLine(vis, factor):
	"""
	Utility for making line selections when averaging velocity channels.
	See `averageLine`.

	vis : path to the visibility to use
	factor: number of channels to merge. ex factor = 5 will merge 5 channels into one.
	"""
	velrange = getVelocityRange(vis)
	nvels = round(abs(velrange[0] - velrange[1])/factor)
	startvel = round(velrange[1])
	return 'vel,{0},{1},{2},{2}'.format(nvels, startvel, factor)

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

def dumpSpec(vis, options={}):
	"""
	Returns raw plot data from Miriad's uvspec.
	This is done with the 'log' option.
	Temporarily creates a file that contains the data from miriad
	then deletes it when it's been read.
	"""
	options['vis'] = vis

	logfile = '__{}_uvspec.dat'.format(vis.split('/')[0])
	options['log'] = logfile

	x = []
	y = []

	uvspec(options) # miriad will leave us a file with the data
	with open(logfile, 'r') as file:
		data = file.readlines()

	for line in data:
		pair = line.split()
		x.append(float(pair[0]))
		y.append(float(pair[1]))

	os.remove(logfile)

	return x,y

def compareSpectra(vis1, vis2, combine=10, options={}, plotOptions={}):
	"""
	Compare spectra utility. Stokes V by default

	combine: the number of velocity channels to average together
	"""
	options['stokes']   = 'v'
	options['options']  = 'avall,nobase'
	options['axis']     = 'freq,amp'
	options['interval'] = 9999
	options['line']     = averageVelocityLine(vis1, factor=combine)

	freq1, amps1 = dumpSpec(vis1, options)
	freq2, amps2 = dumpSpec(vis2, options)

	# hack for a bad channel
	amps1[amps1.index(max(amps1))] = 0
	amps2[amps2.index(max(amps2))] = 0

	defaults = {
		0: {'x': freq1, 'y': amps1, 'draw': 'steps-mid', 'line': 'k-'},
		'title': 'Stokes V: Uncorrected vs Corrected',
		'xlabel': 'Frequency (GHz)', 'ylabel': 'Visibility Amplitude',
		'sharex': True, 'sharey': True,
		'hspace': 0.1,
	}

	plawt.plot({**defaults, **plotOptions}, {
		0: {'x': freq2, 'y': amps2, 'draw': 'steps-mid', 'line': 'k-'}
	})

def showChannels(vis, options={}, freq=False):
	"""
	Plot visibility data with a matplotlib window.
	The matplotlib window has better mouse controls and helps
	with selecting channel numbers.

	Data is from Miriad's uvspec with stokes=i, axes=chan,amp, interval=9999
	and options=avall,nobase

	set `freq` to true to have the x-axis be frequency instead of channels
	"""
	options['stokes']   = 'i'
	options['options']  = 'avall,nobase'
	options['axis']     = 'freq,amp' if freq else 'chan,amp'
	options['interval'] = 9999

	chans, amps = dumpSpec(vis, options)

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
