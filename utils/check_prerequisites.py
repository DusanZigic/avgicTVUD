#!/usr/bin/env python3

from sys import argv, exit, version_info
from os import path, walk, listdir, mkdir, remove
from shutil import rmtree
from subprocess import call
from params import params

###################################################################################################################################
def check_install(comp):
	temp_file = open('response.info', 'w')
	call(comp, shell=True, stdout=temp_file, stderr=temp_file)
	temp_file.close()
	if 'not found' in open('response.info').readline():
		remove('response.info')
		return False
	else:
		remove('response.info')
		return True
#######################################################################################
def check_version(comp):
	temp_file = open('response.info', 'w')
	call(f'{comp} --version', shell=True, stdout=temp_file, stderr=temp_file)
	temp_file.close()
	with open('response.info', 'r') as f:
		version = f.readline().split()[-1]
		version = version.split('.')[0:2]
		version = int(version[0]) + int(version[1])/10.0
		return version
#######################################################################################
def check_module(mdl):
	try:
		__import__(mdl)
	except ImportError:
		return False
	return True
#######################################################################################
def check_libs(lib):
	temp_file = open('response.info', 'w')
	call(f'dpkg -s lib{lib}-dev', shell=True, stdout=temp_file, stderr=temp_file)
	temp_file.close()
	if 'not installed' in open('response.info').readline():
		remove('response.info')
		return False
	else:
		remove('response.info')
		return True
#######################################################################################
def check_prerequisites():

	#checking for python version and modules:
	if check_version('python3') < 3.5:
		print('Error: python version 3.5+ needed. Aborting...')
		return False
	for mdl in ['numpy', 'scipy', 'cython', 'h5py']:
		if not check_module(mdl):
			print(f'Error: python module {mdl} not installed. Aborting...')
			return False

	#checking for c compilers:
	c_comp = False
	for ccomp in ['gcc', 'icc']:
		if check_install(ccomp): c_comp = True
	if not c_comp:
		print('Error: c compiler not installed. Aborting...')
		return False

	#checking for c++ compilers:
	cpp_comp = False
	for cppcomp in ['g++', 'icpc']:
		if check_install(cppcomp): cpp_comp = True
	if not cpp_comp:
		print('Error: c++ compiler not installed. Aborting...')
		return False

	#checking for g++ compiler and it's version:
	if not check_install('g++'):
		print('Error: g++ not installed. Aborting...')
		return False
	if check_version('g++') < 5.0:
		print('Error: g++ version 5.0+ needed. Aborting...')
		return False

	#checking for fortran compilers:
	f_comp = False
	for fcomp in ['gfortran', 'ifort']:
		if check_install(fcomp): f_comp = True
	if not f_comp:
		print('Error: fortran compiler not installed. Aborting...')
		return False

	#checking cmake:
	if not check_install('cmake'):
		print('Error: cmake not installed. Aborting...')
		return False
	if check_version('cmake') < 3.4:
		print('Error: cmake version 3.4+ nedded. Aborting...')
		return False

	#checking boost, hdf5 and gsl libraries:
	lib_check = True
	for lib in ['boost', 'hdf5', 'gsl']:
		if not check_libs(lib):
			lib_check = False
			print(f'Error: {lib} library not installed. Aborting...')
	if not lib_check: return False

	return True
###################################################################################################################################
def check_execs():
	model_dir    = path.abspath('models')
	compile_file = open(path.join(model_dir, 'compile.info'), 'w')
	
	#checking for trento:
	src_dir = path.join(model_dir, 'trento')
	trento_check = False
	for root, dirs, files in walk(src_dir):
		if 'trento' in files: trento_check = True
	if not trento_check:
		if not path.exists(path.join(src_dir, 'build')): mkdir(path.join(src_dir, 'build'))
		call('cmake ..', shell=True, cwd=path.join(src_dir, 'build'), stdout=compile_file, stderr=compile_file)
		call('make', shell=True, cwd=path.join(src_dir, 'build'), stdout=compile_file, stderr=compile_file)
		trento_check = False
		for root, dirs, files in walk(src_dir):
			if 'trento' in files: trento_check = True
		if not trento_check:
			print('Error: unable to compile TRENTO. Aborting...')
			compile_file.close()
			return False

	#checking for trentoavgc:
	src_dir = path.join(model_dir, 'trentoavgc')
	trentoavgc_check = False
	for root, dirs, files in walk(src_dir):
		if 'trentoavgc' in files: trentoavgc_check = True
	if not trentoavgc_check:
		call('g++ trentoavgc.cpp -O3 -o trentoavgc', shell=True, cwd=src_dir, stdout=compile_file, stderr=compile_file)
		trentoavgc_check = False
		for root, dirs, files in walk(src_dir):
			if 'trentoavgc' in files: trentoavgc_check = True
		if not trentoavgc_check:
			print('Error: unable to compile trento averaging code. Aborting...')
			compile_file.close()
			return False

	#checking for share directory:
	share_dir_path = path.join(path.expanduser("~"), '.local', 'share')
	if not path.exists(share_dir_path): mkdir(share_dir_path)

	#checking for freestream module:
	src_dir = path.join(model_dir, 'freestream')
	if not check_module('freestream'):
		call('python3 setup.py install --user', shell=True, cwd=src_dir, stdout=compile_file, stderr=compile_file)
		if not check_module('freestream'):
			print('Error: unable to install freestream module. Aborting...')
			compile_file.close()
			return False

	#checking for frzout module:
	src_dir = path.join(model_dir, 'frzout')
	if not check_module('frzout'):
		call('python3 setup.py install --user', shell=True, cwd=src_dir, stdout=compile_file, stderr=compile_file)
		if not check_module('frzout'):
			print('Error: unable to install frzout module. Aborting...')
			compile_file.close()
			return False

	#checking for osu-hydro:
	src_dir = path.join(model_dir, 'osu-hydro')
	osuhydro_check = False
	for root, dirs, files in walk(src_dir):
		if 'osu-hydro' in files: osuhydro_check = True
	if not osuhydro_check:
		if not path.exists(path.join(src_dir, 'build')): mkdir(path.join(src_dir, 'build'))
		call('cmake .. -DCMAKE_INSTALL_PREFIX=hydro', shell=True, cwd=path.join(src_dir, 'build'), stdout=compile_file, stderr=compile_file)
		call('make install', shell=True, cwd=path.join(src_dir, 'build'), stdout=compile_file, stderr=compile_file)
		osuhydro_check = False
		for root, dirs, files in walk(src_dir):
			if 'osu-hydro' in files: osuhydro_check = True
		if not osuhydro_check:
			print('Error: unable to compile osu-hydro. Aborting...')
			compile_file.close()
			return False
	if not path.exists(path.join(src_dir, 'eos', 'eos.dat')):
		call('python3 eos.py > eos.dat', shell=True, cwd=path.join(src_dir, 'eos'))
		if not path.exists(path.join(src_dir, 'eos', 'eos.dat')):
			print('Error: unable to generate eos. Aborting...')
			compile_file.close()
			return False

	#checking for urqmd:
	src_dir = path.join(model_dir, 'urqmd-afterburner')
	afterburner_check = False
	osc2u_check       = False
	urqmd_check       = False
	for root, dirs, files in walk(src_dir):
		if 'afterburner' in files: afterburner_check = True
		if 'osc2u'       in files: osc2u_check       = True
		if 'urqmd'       in files: urqmd_check       = True
	if not afterburner_check or not osc2u_check or not urqmd_check:
		if not path.exists(path.join(src_dir, 'build')): mkdir(path.join(src_dir, 'build'))
		call('cmake .. -DCMAKE_INSTALL_PREFIX=hadrontransport', shell=True, cwd=path.join(src_dir, 'build'), stdout=compile_file, stderr=compile_file)
		call('make install', shell=True, cwd=path.join(src_dir, 'build'), stdout=compile_file, stderr=compile_file)
		afterburner_check = False
		osc2u_check       = False
		urqmd_check       = False
		for root, dirs, files in walk(src_dir):
			if 'afterburner' in files: afterburner_check = True
			if 'osc2u'       in files: osc2u_check       = True
			if 'urqmd'       in files: urqmd_check       = True
		if not afterburner_check or not osc2u_check or not urqmd_check:
			print('Error: unable to compile urqmd afterburner. Aborting...')
			compile_file.close()
			return False

	#checking for analysis scripts:
	src_dir = path.join(model_dir, 'analysis')
	analysis_check = True
	if not path.exists(src_dir): 								 analysis_check = False
	if not path.exists(path.join(src_dir, 'analyse.py')): 		 analysis_check = False
	if not path.exists(path.join(src_dir, 'reference_flow.py')): analysis_check = False
	if not analysis_check:
		print('Error: unable to find analysis scripts. Aborting...')
		compile_file.close()
		return False

	#checking for DREENAA executables:
	src_dir = path.join(model_dir, 'avgictvuddreena')
	dreena_check = False
	for root, dirs, files in walk(src_dir):
		if 'DREENAA' in files: dreena_check = True
	if not dreena_check:
		call('g++ source/*.cpp -fopenmp -O3 -o DREENAA', shell=True, cwd=src_dir, stdout=compile_file, stderr=compile_file)
		dreena_check = False
		for root, dirs, files in walk(src_dir):
			if 'DREENAA' in files: dreena_check = True
		if not dreena_check:
			print('Error: unable to compile DREENA-A source code. Aborting...')
			compile_file.close()
			return False
	
	compile_file.close()
	remove(path.join(model_dir, 'compile.info'))
	
	# checking for initial pT distributions:
	src_dir = path.join(model_dir, "dreena", "ptDists", f"ptDist{params['trento']['ecm']:d}GeV")
	if "ch" in params['dreena']['particles']:
		for pName in ["Down", "DownBar", "Gluon", "Strange", "Up", "UpBar"]:
			if not f"ptDist_{params['trento']['ecm']:d}GeV_{pName}.dat" in listdir(src_dir):
				print(f"Error: unable to find initial pT distribution for {pName.lower().replace('bar', '-bar')} quark. Aborting...")
				return False
	if "d" in params['dreena']['particles']:
		if not f"ptDist_{params['trento']['ecm']:d}GeV_Charm.dat" in listdir(src_dir):
			print(f"Error: unable to find initial pT distribution for charm quark. Aborting...")
			return False
	if "b" in params['dreena']['particles']:
		if not f"ptDist_{params['trento']['ecm']:d}GeV_Bottom.dat" in listdir(src_dir):
			print(f"Error: unable to find initial pT distribution for bottom quark. Aborting...")
			return False
	
	return True
###################################################################################################################################

###################################################################################################################################
def recompile():
	if params['main']['recompile'] == 0: return True

	models_dir = path.abspath("models")
	rmtree(path.join(models_dir, "trento",                "build"))
	remove(path.join(models_dir, "trentoavgc",		 "trentoavgc"))
	rmtree(path.join(models_dir, "osu-hydro",             "build"))
	rmtree(path.join(models_dir, "urqmd-afterburner",     "build"))
	remove(path.join(models_dir, "dreena",                "DREENAA"))

	if not check_execs(): return False

	return True

###################################################################################################################################