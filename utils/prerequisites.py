#!/usr/bin/env python3

from sys import version_info, exit
from os import path, walk, listdir, mkdir, remove
from shutil import rmtree
from subprocess import call

class prerequisites:
	def __init__(self, params):
		self.params = params
	
	def __check_install(self, comp):
		temp_file = open("response.info", 'w')
		call(f"{comp} --version", shell=True, stdout=temp_file, stderr=temp_file)
		temp_file.close()
		installFlag = not "not found" in open("response.info", 'r').readline()
		remove("response.info")
		return installFlag

	def __check_version(self, comp):
		temp_file = open("response.info", 'w')
		call(comp + " --version", shell=True, stdout=temp_file, stderr=temp_file)
		temp_file.close()
		with open("response.info", 'r') as f:
			version = f.readline().split()[-1]
			version = version.split('.')[0:2]
			version = int(version[0]) + int(version[1])/10.0
			return version
	
	def __check_libs(self, lib):
		temp_file = open("response.info", 'w')
		call("dpkg -s lib%s-dev" % lib, shell=True, stdout=temp_file, stderr=temp_file)
		temp_file.close()
		if "not installed" in open("response.info").readline():
			remove("response.info")
			return False
		else:
			remove("response.info")
			return True
	
	def check_prerequisites(self):
		# python versiob and modules:
		if version_info[0] == 3 and version_info[1] >= 5:
			pass
		else :
			print("Error: python version 3.5+ needed. Aborting...")
			exit()
		for mdl in ["numpy", "scipy", "cython", "h5py", "argparse", "re", "itertools", "json"]:
			try:
				__import__(mdl)
			except ImportError:
				print(f"Error: python module {mdl} not installed. Aborting...")
				exit()

		# checking for c compilers
		cCompFlag = False
		for ccomp in ["gcc", "icc"]:
			if self.__check_install(ccomp): cCompFlag = True
		if not cCompFlag:
			print("Error: c compiler not installed. Aborting...")
			exit()

		# checking for c++ compilers
		cppCompFlag = False
		for cppcomp in ["g++", "icpc"]:
			if self.__check_install(cppcomp): cppCompFlag = True
		if not cppCompFlag:
			print("Error: c++ compiler not installed. Aborting...")
			exit()

		# checking for g++ compiler and its version:
		if not self.__check_install("g++"):
			print("Error: g++ not installed. Aborting...")
			exit()
		if self.__check_version("g++") < 5.0:
			print("Error: g++ version 5.0+ needed. Aborting...")
			exit()

		#checking for fortran compilers:
		fCompFlag = False
		for fcomp in ["gfortran", "ifort"]:
			if self.__check_install(fcomp): fCompFlag = True
		if not fCompFlag:
			print("Error: fortran compiler not installed. Aborting...")
			exit()

		# checking cmake:
		if not self.__check_install("cmake"):
			print("Error: cmake not installed. Aborting...")
			exit()
		if self.__check_version("cmake") < 3.4:
			print("Error: cmake version 3.4+ nedded. Aborting...")
			exit()

		# checking boost, hdf5 and gsl libraries:
		libFlag = True
		for lib in ["boost", "hdf5", "gsl"]:
			if not self.__check_libs(lib):
				libFlag = False
				print(f"Error: {lib} library not installed. Aborting...")
		if not libFlag:
			exit()
		
	def check_execs(self):
		model_dir    = path.abspath("models")
		compile_file = open(path.join(model_dir, "compile.info"), 'w')

		# checking for trento:
		src_dir = path.join(model_dir, "trento")
		trentoFlag = False
		for root, dirs, files in walk(src_dir):
			if "trento" in files: trentoFlag = True
		if not trentoFlag:
			if not path.exists(path.join(src_dir, "build")): mkdir(path.join(src_dir, "build"))
			call("cmake ..", shell=True, cwd=path.join(src_dir, "build"), stdout=compile_file, stderr=compile_file)
			call("make", shell=True, cwd=path.join(src_dir, "build"), stdout=compile_file, stderr=compile_file)
			trentoFlag = False
			for root, dirs, files in walk(src_dir):
				if "trento" in files: trentoFlag = True
			if not trentoFlag:
				print("Error: unable to compile TRENTO. Aborting...")
				compile_file.close()
				exit()
		
		#checking for trentoavgc:
		src_dir = path.join(model_dir, "trentoavgc")
		trentoavgcFlag = False
		for root, dirs, files in walk(src_dir):
			if "trentoavgc" in files: trentoavgcFlag = True
		if not trentoavgcFlag:
			call("g++ trentoavgc.cpp -O3 -o trentoavgc", shell=True, cwd=src_dir, stdout=compile_file, stderr=compile_file)
			trentoavgcFlag = False
			for root, dirs, files in walk(src_dir):
				if "trentoavgc" in files: trentoavgcFlag = True
			if not trentoavgcFlag:
				print("Error: unable to compile trento averaging code. Aborting...")
				compile_file.close()
				return False

		# checking for share directory:
		share_dir_path = path.join(path.expanduser("~"), ".local", "share")
		if not path.exists(share_dir_path): mkdir(share_dir_path)

		# checking for freestream module:
		try:
			__import__("freestream")
		except ImportError:
			src_dir = path.join(model_dir, "freestream")
			call("python3 setup.py install --user", shell=True, cwd=src_dir, stdout=compile_file, stderr=compile_file)
		try:
			__import__("freestream")
		except ImportError:
			print("Error: unable to install freestream module. Aborting...")
			compile_file.close()
			exit()

		# checking for frzout module:
		try:
			__import__("frzout")
		except ImportError:
			src_dir = path.join(model_dir, "frzout")
			call("python3 setup.py install --user", shell=True, cwd=src_dir, stdout=compile_file, stderr=compile_file)
		try:
			__import__("frzout")
		except ImportError:
			print("Error: unable to install frzout module. Aborting...")
			compile_file.close()
			exit()
		
		# checking for osu-hydro:
		src_dir = path.join(model_dir, "osu-hydro")
		osuhydroFlag = False
		for root, dirs, files in walk(src_dir):
			if "osu-hydro" in files: osuhydroFlag = True
		if not osuhydroFlag:
			if not path.exists(path.join(src_dir, "build")): mkdir(path.join(src_dir, "build"))
			call("cmake .. -DCMAKE_INSTALL_PREFIX=hydro", shell=True, cwd=path.join(src_dir, "build"), stdout=compile_file, stderr=compile_file)
			call("make install", shell=True, cwd=path.join(src_dir, "build"), stdout=compile_file, stderr=compile_file)
			osuhydroFlag = False
			for root, dirs, files in walk(src_dir):
				if "osu-hydro" in files: osuhydroFlag = True
			if not osuhydroFlag:
				print("Error: unable to compile osu-hydro. Aborting...")
				compile_file.close()
				exit()
		if not path.exists(path.join(src_dir, "eos", "eos.dat")):
			call("python3 eos.py > eos.dat", shell=True, cwd=path.join(src_dir, "eos"))
			if not path.exists(path.join(src_dir, "eos", "eos.dat")):
				print("Error: unable to generate eos. Aborting...")
				compile_file.close()
				exit()

		# checking for urqmd:
		src_dir = path.join(model_dir, "urqmd-afterburner")
		afterburnerFlag = False
		osc2uFlag       = False
		urqmdFlag       = False
		for root, dirs, files in walk(src_dir):
			if "afterburner" in files: afterburnerFlag = True
			if "osc2u"       in files: osc2uFlag       = True
			if "urqmd"       in files: urqmdFlag       = True
		if not afterburnerFlag or not osc2uFlag or not urqmdFlag:
			if not path.exists(path.join(src_dir, "build")): mkdir(path.join(src_dir, "build"))
			call("cmake .. -DCMAKE_INSTALL_PREFIX=hadrontransport", shell=True, cwd=path.join(src_dir, "build"), stdout=compile_file, stderr=compile_file)
			call("make install", shell=True, cwd=path.join(src_dir, "build"), stdout=compile_file, stderr=compile_file)
			afterburnerFlag = False
			osc2uFlag       = False
			urqmdFlag       = False
			for root, dirs, files in walk(src_dir):
				if "afterburner" in files: afterburnerFlag = True
				if "osc2u"       in files: osc2uFlag       = True
				if "urqmd"       in files: urqmdFlag       = True
			if not afterburnerFlag or not osc2uFlag or not urqmdFlag:
				print("Error: unable to compile urqmd afterburner. Aborting...")
				compile_file.close()
				exit()

		# checking for DREENAA executables:
		src_dir = path.join(model_dir, "avgictvuddreena")
		dreenaFlag = False
		for root, dirs, files in walk(src_dir):
			if "DREENAA" in files: dreenaFlag = True
		if not dreenaFlag:
			call("g++ source/*.cpp -fopenmp -O3 -o DREENAA", shell=True, cwd=src_dir, stdout=compile_file, stderr=compile_file)
			dreenaFlag = False
			for root, dirs, files in walk(src_dir):
				if "DREENAA" in files: dreenaFlag = True
			if not dreenaFlag:
				print("Error: unable to compile DREENA-A source code. Aborting...")
				compile_file.close()
				exit()
		
		# checking for DSSFFs executable:
		src_dir = path.join(model_dir, "DSSFFs")
		if path.exists(src_dir):
			dssffsFlag = False
			for root, dirs, files in walk(src_dir):
				if "DSSFFs" in files: dssffsFlag = True
			if not dssffsFlag:
				call("g++ source/*.cpp -fopenmp -O3 -o DSSFFs", shell=True, cwd=src_dir, stdout=compile_file, stderr=compile_file)
				dssffsFlag = False
				for root, dirs, files in walk(src_dir):
					if "DSSFFs" in files: dssffsFlag = True
				if not dssffsFlag:
					print("Error: could not compile DSSFFs source code. Aborting...")
					compile_file.close()
					exit()
	
		# checking for initial pT distributions:
		src_dir = path.join(model_dir, "ebetvuddreena", "ptDists", f"ptDist{self.params['trento']['ecm']:d}GeV")
		if "ch" in self.params['dreena']['particles']:
			for pName in ["Down", "DownBar", "Gluon", "Strange", "Up", "UpBar"]:
				if not f"ptDist_{self.params['trento']['ecm']:d}GeV_{pName}.dat" in listdir(src_dir):
					print(f"Error: unable to find initial pT distribution for {pName.lower().replace('bar', '-bar')} quark. Aborting...")
					exit()
			if not path.exists(path.join(model_dir, "DSSFFs")):
				print("Error: unable to find DSSFFs source directory. Aborting...")
				exit()
		if "d" in self.params['dreena']['particles']:
			if not f"ptDist_{self.params['trento']['ecm']:d}GeV_Charm.dat" in listdir(src_dir):
				print(f"Error: unable to find initial pT distribution for charm quark. Aborting...")
				exit()
		if "b" in self.params['dreena']['particles']:
			if not f"ptDist_{self.params['trento']['ecm']:d}GeV_Bottom.dat" in listdir(src_dir):
				print(f"Error: unable to find initial pT distribution for bottom quark. Aborting...")
				exit()

		
		compile_file.close()
		remove(path.join(model_dir, "compile.info"))

	def recompile(self):
		if self.params['main']['recompile'] == 1:
			models_dir = path.abspath("models")
			if path.exists(path.join(models_dir, "trento", "build")):
				rmtree(path.join(models_dir, "trento", "build"))
			if path.exists(path.join(models_dir, "trentoavgc", "trentoavgc")):
				remove(path.join(models_dir, "trentoavgc", "trentoavgc"))
			if path.exists(path.join(models_dir, "osu-hydro", "build")):
				rmtree(path.join(models_dir, "osu-hydro", "build"))
			if path.exists(path.join(models_dir, "urqmd-afterburner", "build")):
				rmtree(path.join(models_dir, "urqmd-afterburner", "build"))
			if path.exists(path.join(models_dir, "avgictvuddreena", "DREENAA")):
				remove(path.join(models_dir, "avgictvuddreena", "DREENAA"))
			if path.exists(path.join(models_dir, "DSSFFs", "DSSFFs")):
				remove(path.join(models_dir, "DSSFFs", "DSSFFs"))
			self.check_execs()