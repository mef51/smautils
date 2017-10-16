#!/usr/bin/python3

import shutil, glob, os
import miriad


def split(uvo, uvc, so, lines=[]):
	""" Split in different files LL and RR """
	stks = ['ll', 'rr', 'lr', 'rl']
	for stk in stks:
		for lin in lines:
			path = '{}/{}.{}.{}'.format(uvc, so, lin, stk)
			if os.path.exists(path): shutil.rmtree(path)

			miriad.uvaver({
				'vis' : '{}/{}.{}'.format(uvo, so, lin),
				'out' : '{}/{}.{}.{}'.format(uvc, so, lin, stk),
				'select' : 'pol({})'.format(stk)
			})

def selfcal(so, uvc, lines=[]):
	"""
	Original map used for selfcal in MAPS
	Independent step for RR and LL (u,v) files
	1. Selcalibration of continuum
	2. Applying selfcalibration  for continuum
	3. Copyinggains to Line data (all in the USB)
	4. Applying selfcalibration  for lines
	5. Concanate LL and RR in ine file
	6. Resort data

	lines: ex. ['co3-2', 'sio8-7', 'cnt.usb', 'usb']
	"""
	calibrator = 'cnt.usb'
	for stk in ['ll', 'rr']:
		for sb in [calibrator]:
			miriad.selfcal({
				'vis' : '{}/{}.{}.{}'.format(uvc, so, sb, stk),
				'model' : 'MAPS/{}.cont.usb.i.cc'.format(so),
				'refant' : 6,
				'interval' : 8,
				'options' : 'phase'
			})
			miriad.gpplt({
				'vis' : '{}/{}.{}.{}'.format(uvc, so, sb, stk),
				'device' : '1/xs',
				'yaxis' : 'phase',
				'nxy' : '1,3'
			})
			input("Press enter to continue...")

			path = '{}/{}.{}.{}.slfc'.format(uvc, so, sb, stk)
			if os.path.exists(path): shutil.rmtree(path)

			miriad.uvaver({
				'vis' : '{}/{}.{}.{}'.format(uvc, so, sb, stk),
				'out' : '{}/{}.{}.{}.slfc'.format(uvc, so, sb, stk)
			})
		for lin in [l for l in lines if l != calibrator]: # iterate over lines excluding the calibrator
			path = '{}/{}.{}.{}.slfc'.format(uvc, so, lin, stk)
			if os.path.exists(path): shutil.rmtree(path)

			miriad.gpcopy({
				'vis' : '{}/{}.cnt.usb.{}'.format(uvc, so, stk),
				'out' : '{}/{}.{}.{}'.format(uvc, so, lin, stk),
			})
			miriad.uvaver({
				'vis' : '{}/{}.{}.{}'.format(uvc, so, lin, stk),
				'out' : '{}/{}.{}.{}.slfc'.format(uvc, so, lin, stk),
			})

	for lin in lines:
		vis = '{}/{}.{}'.format(uvc, so, lin)
		for folder in ['tmp.5', 'tmp.6', '{}/{}.{}.corrected.slfc'.format(uvc, so, lin)]:
			if os.path.exists(folder): shutil.rmtree(folder)

		miriad.uvcat({
			'vis' : '{0}.rr.slfc,{0}.ll.slfc,{0}.rl,{0}.lr'.format(vis),
			'out' : 'tmp.5',
		})
		miriad.uvsort({
			'vis' : 'tmp.5',
			'out' : 'tmp.6',
		})
		miriad.uvaver({
			'vis' : 'tmp.6',
			'out' : '{}/{}.{}.corrected.slfc'.format(uvc, so, lin),
			'interval' : 5
		})

def mapvis(uvo, uvc, so, mapdir, lines=[], lineSelection=[]):
	"""
	Make a map from visibilities
	1. Continuum Stokes I,V Uncorrected & Corrected data
	2. Map All lines. Corrected
	3. Map All lines. Uncorrected
	4. Continuum LL and RR independently, for non-selfcal and selfcal cases
	"""
	calibrator = 'cnt.usb'
	if len(lines) != len(lineSelection):
		lineSelection = [None for l in lines]

	# 1.
	src = '{}/{}.cnt'.format(mapdir, so)
	tall = 0.03

	for path in glob.glob('{}.*'.format(src)):
		if os.path.exists(path): shutil.rmtree(path)

	vis = '{}/{}.cnt.usb.corrected.slfc'.format(uvc, so)
	for src in ['{}/{}.cnt'.format(mapdir, so), '{}/{}.cnt.uncorrected'.format(mapdir, so)]:
		miriad.invert({
			'vis': vis,
			'stokes': 'i,v',
			'beam': '{}.bm'.format(src),
			'map': '{0}.i.mp,{0}.v.mp'.format(src),
			'imsize': 128,
			'cell': 0.3,
			'options': 'systemp,double,mfs',
			'sup': 0
		})

		for stk in ['i', 'v']:
			miriad.clean({
				'map': '{}.{}.mp'.format(src, stk),
				'beam': '{}.bm'.format(src),
				'out': '{}.{}.cc'.format(src, stk),
				'niters': 3000,
				'cutoff': tall
			})
			miriad.restor({
				'map': '{}.{}.mp'.format(src, stk),
				'beam': '{}.bm'.format(src),
				'model': '{}.{}.cc'.format(src, stk),
				'out': '{}.{}.cm'.format(src, stk),
			})
		vis = '{}/{}.cnt.usb'.format(uvo, so)

	# 2. Map corrected line data
	# 3. Map uncorrected line data with same paramenters as in 2
	tall = 0.50

	# remove continuum, its already been mapped
	lines.remove(calibrator)
	lines.remove('usb')

	for i, lin in enumerate(lines):
		vis = '{}/{}.{}.corrected.slfc'.format(uvc, so, lin)
		for src in ['{}/{}.{}'.format(mapdir, so, lin), '{}/{}.{}.uncorrected'.format(mapdir, so, lin)]:
			line = miriad.averageVelocityLine(vis, 2)
			for path in glob.glob('{}.*'.format(src)):
				if os.path.exists(path): shutil.rmtree(path)

			invertOptions = {
				'vis': vis,
				'stokes': 'i,v',
				'beam': '{}.bm'.format(src),
				'map': '{0}.i.mp,{0}.v.mp'.format(src),
				'imsize': 128,
				'cell': 0.3,
				'options': 'systemp,double,mfs',
				'sup': 0,
			}
			if lineSelection[i] is not None:
				invertOptions['line'] = lineSelection[i]
			miriad.invert(invertOptions)

			for stk in ['i', 'v']:
				miriad.clean({
					'map': '{}.{}.mp'.format(src, stk),
					'beam': '{}.bm'.format(src),
					'out': '{}.{}.cc'.format(src, stk),
					'niters': 3000,
					'cutoff': tall
				})
				miriad.restor({
					'map': '{}.{}.mp'.format(src, stk),
					'beam': '{}.bm'.format(src),
					'model': '{}.{}.cc'.format(src, stk),
					'out': '{}.{}.cm'.format(src, stk),
				})
			vis = '{}/{}.{}'.format(uvo, so, lin)

	# 4. nopol is for selfcal case (this option is not used!)
	tall = 0.03

	for stk in ['ll', 'rr']:
		src = '{}/{}.cnt.{}'.format(mapdir, so, stk)
		for path in glob.glob('{}.*'.format(src)):
			if os.path.exists(path): shutil.rmtree(path)
		for pol in ['nopol', 'nocal']:
			path = '{}.bm'.format(src)
			if os.path.exists(path): shutil.rmtree(path)

			miriad.invert({
				'vis': '{}/{}.cnt.usb.{}'.format(uvc, so, stk),
				'beam': '{}.bm'.format(src),
				'map': '{}.{}.mp'.format(src, pol),
				'imsize': 128,
				'cell': 0.3,
				'options': 'systemp,double,mfs,{}'.format(pol),
				'sup': 0
			})
			miriad.clean({
				'map': '{}.{}.mp'.format(src, pol),
				'beam': '{}.bm'.format(src),
				'out': '{}.{}.cc'.format(src, pol),
				'niters': 3000,
				'cutoff': tall
			})
			miriad.restor({
				'map': '{}.{}.mp'.format(src, pol),
				'beam': '{}.bm'.format(src),
				'model': '{}.{}.cc'.format(src, pol),
				'out': '{}.{}.cm'.format(src, pol),
			})

def mapallvis(uvo, uvc, so, mapdir, lines=[]):
	"""
	Similar to mapvis but doesn't do multiple frequency synthesis.
	The frequency axis is preserved so you can get spectra from the image.
	"""
	calibrator = 'cnt.usb'
	tall = 0.50

	# remove continuum, its already been mapped
	lines.remove(calibrator)
	lines.remove('usb')

	for i, lin in enumerate(lines):
		vis = '{}/{}.{}.corrected.slfc'.format(uvc, so, lin)
		for src in ['{}/{}.{}'.format(mapdir, so, lin), '{}/{}.{}.uncorrected'.format(mapdir, so, lin)]:
			line = miriad.averageVelocityLine(vis, 2)
			for path in glob.glob('{}.full.*'.format(src)):
				if os.path.exists(path): shutil.rmtree(path)

			invertOptions = {
				'vis': vis,
				'stokes': 'i,v',
				'beam': '{}.full.bm'.format(src),
				'map': '{0}.i.full.mp,{0}.v.full.mp'.format(src),
				'imsize': 128,
				'cell': 0.3,
				'options': 'systemp,double',
				'sup': 0,
			}
			miriad.invert(invertOptions)

			for stk in ['i', 'v']:
				miriad.clean({
					'map': '{}.{}.full.mp'.format(src, stk),
					'beam': '{}.full.bm'.format(src),
					'out': '{}.{}.full.cc'.format(src, stk),
					'niters': 3000,
					'cutoff': tall
				})
				miriad.restor({
					'map': '{}.{}.full.mp'.format(src, stk),
					'beam': '{}.full.bm'.format(src),
					'model': '{}.{}.full.cc'.format(src, stk),
					'out': '{}.{}.full.cm'.format(src, stk),
				})
			vis = '{}/{}.{}'.format(uvo, so, lin)

def disp(uvo, uvc, so, mapdir, lines=[], stokesVrms=[]):
	"""
	1. Plot uncorrected channel map
	2. Plot corrected channel map
	"""

	for i, lin in enumerate(lines):
	# for lin in ['cnt', 'co3-2', 'sio8-7']:
		devicetype = 'ps/cps'
		filename = lin
		src = '{}/{}.{}'.format(mapdir, so, lin)
		nxy = '1,1'

		path = '{}.v-i.perc'.format(src)
		if os.path.exists(path): shutil.rmtree(path)
		path = '{}.v-i.perc.uncorrected'.format(src)
		if os.path.exists(path): shutil.rmtree(path)

		rms = stokesVrms[i]
		if lin == 'cnt':
			for suffix in ['', 'uncorrected.']:
				opts = {
					'exp': '100*<{0}.{1}v.cm>/<{0}.{1}i.cm>'.format(src, suffix),
					'mask': '<{}.{}i.cm>.gt.0.4'.format(src, suffix),
				}
				suffix = '.uncorrected' if suffix != '' else ''
				opts['out'] =  '{}.v-i.perc{}'.format(src, suffix)
				miriad.maths(opts)
		else:
			for suffix in ['', 'uncorrected.']:
				val = 6 if suffix == '' else 8
				opts = {
						'exp': '100*<{0}.{1}v.cm>/<{0}.{1}i.cm>'.format(src, suffix),
						'mask': '<{}.{}i.cm>.gt.{}'.format(src, suffix, val),
					}
				suffix = '.uncorrected' if suffix != '' else ''
				opts['out'] =  '{}.v-i.perc{}'.format(src, suffix)
				miriad.maths(opts)

		for datatype in ['uncorr', 'corr']:
			cgdispOpts = {
				'type': 'cont,cont',
				'labtyp': 'arcsec,arcsec',
				'options': 'full,beambl,3val',
				'csize': '0,1,0,0',
				'cols1': 2, 'cols2': 8,
				'levs1': '15,35,55,75,95',
				'nxy': nxy,
			}

			if datatype is 'uncorr':
				# flux plot
				cgdispOpts['slev'] = 'p,1,a,{}'.format(rms)
				cgdispOpts['device'] = '{}.uncorr.{}'.format(filename, devicetype)
				cgdispOpts['in'] = '{0}.uncorrected.i.cm,{0}.uncorrected.v.cm'.format(src)
				cgdispOpts['levs2'] = '-8,-7,-6,-5,-4,-3,-2,2,3,4,5,6,7,8'
				miriad.cgdisp(cgdispOpts)
				miriad.imstat({'in': '{}.i.cm'.format(src), 'region':'box(3,3,50,125)'})
				miriad.imstat({'in': '{}.v.cm'.format(src), 'region':'box(3,3,50,125)'})
				input("Press enter to continue...")

				# v/i plot
				cgdispOpts['slev'] = 'p,1,a,1'
				cgdispOpts['device'] = '{}.uncorr.perc.{}'.format(filename, devicetype)
				cgdispOpts['in'] = '{0}.uncorrected.i.cm,{0}.v-i.perc.uncorrected'.format(src)
				cgdispOpts['levs2'] = '-6,-5,-4,-3,-2,-1,1,2,3,4,5,6'
				miriad.cgdisp(cgdispOpts)
				input("Press enter to continue...")
			else:
				# flux plot
				cgdispOpts['slev'] = 'p,1,a,{}'.format(rms)
				cgdispOpts['device'] = '{}.corr.{}'.format(filename, devicetype)
				cgdispOpts['in'] = '{0}.i.cm,{0}.v.cm'.format(src)
				cgdispOpts['levs2'] = '-8,-7,-6,-5,-4,-3,-2,2,3,4,5,6,7,8'
				miriad.cgdisp(cgdispOpts)
				miriad.imstat({'in': '{}.i.cm'.format(src), 'region':'box(3,3,50,125)'})
				miriad.imstat({'in': '{}.v.cm'.format(src), 'region':'box(3,3,50,125)'})
				input("Press enter to continue...   ")

				# v/i plot
				cgdispOpts['slev'] = 'p,1,a,1'
				cgdispOpts['device'] = '{}.corr.perc.{}'.format(filename, devicetype)
				cgdispOpts['in'] = '{0}.i.cm,{0}.v-i.perc'.format(src)
				cgdispOpts['levs2'] = '-6,-5,-4,-3,-2,-1,1,2,3,4,5,6'
				miriad.cgdisp(cgdispOpts)
				input("Press enter to continue...   ")

def peak(so, mapdir):
	src = '{}/{}.cnt'.format(mapdir, so)
	for li in ['ll.nocal', 'rr.nocal', 'll.nopol', 'rr.nopol']:
		miriad.maxfit({'in': '{}.{}.cm'.format(src, li), 'log': 'maxfit_{}.{}'.format(so, li)})
	miriad.maxfit({'in': '{}.i.cm'.format(src), 'log': 'maxfit_{}.stokesI'.format(so)})

if __name__ == '__main__':
	so = 'NGC7538S-s4'
	uvo = 'UVDATA'
	uvc = 'UVOffsetCorrect'
	mapdir = 'MAPSCorrect'

	lines = ['co3-2', 'ch2co17-16', 'cnt.usb', 'usb']
	input("Press return to split")
	split(uvo, uvc, so, lines)
	input("Press return to selfcal")
	selfcal(so, uvc, lines)
	input("Press return to map visibilities")
	mapvis(uvo, uvc, so, mapdir, lines[:],
		lineSelection=[None, None, None, None]
	)
	input("Press return to map visibilities with frequency axis")
	mapvis(uvo, uvc, so, mapdir, lines[:])
	input("Press return to save plots")
	disp(uvo, uvc, so, mapdir,
		lines=['co3-2', 'ch2co17-16', 'cnt'],
		stokesVrms=[0.044, 0.0089, 0.0055]
	)
