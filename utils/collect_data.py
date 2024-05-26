#!/usr/bin/env python3

from os import path, mkdir, remove, rename, listdir
from glob import glob
from re import findall
from time import sleep
from shutil import rmtree
from subprocess import call
import numpy as np
from params import params

def collect_trento():
# function that collects trento results

	work_dir = path.abspath("work")
	job_dirs = glob(path.join(work_dir, "trentojob*"))
	job_dirs = sorted(job_dirs, key=lambda x: int(findall("\d+", path.split(x)[-1])[0]))

	while True:
		sleep(2)
		if all([path.exists(path.join(job_dir, "jobdone.info")) for job_dir in job_dirs]): break
	sleep(2)
	
	trento_events = np.empty((0, 6), float)
	for job_dir in job_dirs: trento_events = np.concatenate((trento_events, np.loadtxt(path.join(job_dir, "trento_events.dat"))), axis=0)
	sorted_index  = np.lexsort((trento_events[:,5], -trento_events[:,4], -trento_events[:,3], -trento_events[:,2]))
	trento_events = trento_events[sorted_index]
	trento_events = np.hstack((np.array(range(0, trento_events.shape[0]))[...,None], trento_events))
	np.savetxt(path.join(work_dir, "trento_events.dat"), trento_events, fmt="%6d %4d %6d %3d %3d %.5f %.5f",\
				header="id_sort job_id event_id npart ncoll TATB b")

	dest_dir = path.join(work_dir, "trentoic")
	if not path.exists(dest_dir): mkdir(dest_dir)

	for tevent in trento_events:
		rename(path.join(work_dir, f"trentojob{tevent[1]:0.0f}", "eventstemp",    f"{tevent[2]:0.0f}.dat"),\
				path.join(dest_dir,    f"{tevent[0]:0.0f}.dat"))
		rename(path.join(work_dir, f"trentojob{tevent[1]:0.0f}", "eventstemp", f"bcp{tevent[2]:0.0f}.dat"),\
				path.join(dest_dir, f"bcp{tevent[0]:0.0f}.dat"))

	for job_id in range(len(job_dirs)): rmtree(path.join(work_dir, job_dirs[job_id]))

def collect_trentoavg():
# function that collects trentoavg results

	work_dir = path.abspath("work")
	job_dirs = glob(path.join(work_dir, "trentoavgjob*"))
	job_dirs = sorted(job_dirs, key=lambda x: int(findall("\d+", path.split(x)[-1])[0]))

	while True:
		sleep(2)
		if all([path.exists(path.join(job_dir, "jobdone.info")) for job_dir in job_dirs]): break
	sleep(2)

	sd_dir  = path.join(work_dir, "avgsd")
	if not path.exists(sd_dir): mkdir(sd_dir)
	bcd_dir = path.join(work_dir, "bcdens")
	if not path.exists(bcd_dir): mkdir(bcd_dir)

	for job_id in range(len(job_dirs)):
		rename(path.join(job_dirs[job_id],     "sdavg.dat"), path.join(sd_dir,      f"sdavg{job_id:d}.dat"))
		rename(path.join(job_dirs[job_id], "bcdensity.dat"), path.join(bcd_dir, f"bcdensity{job_id:d}.dat"))

	for job_dir in job_dirs: rmtree(job_dir)
	rmtree(path.join(work_dir, "trentoic"))

def collect_hydro():
# function that collects hydro results

	work_dir = path.abspath("work")
	job_dirs = glob(path.join(work_dir, "hydrojob*"))
	job_dirs = sorted(job_dirs, key=lambda x: int(findall("\d+", path.split(x)[-1])[0]))

	while True:
		sleep(2)
		if all([path.exists(path.join(job_dir, "jobdone.info")) for job_dir in job_dirs]): break
	sleep(2)

	dest_dir = path.join(work_dir, "tempevols")
	if not path.exists(dest_dir): mkdir(dest_dir)

	for job_id in range(len(job_dirs)):
		job_dir = job_dirs[job_id]
		rename(path.join(job_dir, "Temp_evo.dat"), path.join(dest_dir, f"tempevol{job_id:d}.dat"))
		filestoremove = list(set(glob(path.join(job_dir, "*"))) - set(glob(path.join(job_dir, "particles_in_*"))))
		for aFile in filestoremove: remove(aFile)

def collect_urqmd(hydrojobid):
# function that collects urqmd results

	work_dir = path.abspath("work")
	job_dirs = glob(path.join(work_dir, "urqmdjob*"))
	job_dirs = sorted(job_dirs, key=lambda x: int(findall("\d+", path.split(x)[-1])[0]))

	while True:
		sleep(2)
		if all([path.exists(path.join(job_dir, "jobdone.info")) for job_dir in job_dirs]): break
	sleep(2)

	dest_dir = path.join(work_dir, "urqmd")
	if not path.exists(dest_dir): mkdir(dest_dir)

	commandString  = "cat "
	commandString += " ".join([path.join(job_dir, "particles_out.dat") for job_dir in job_dirs])
	commandString += " > "
	commandString += path.join(dest_dir, f"particles_out_{hydrojobid:d}.dat")
	call(commandString, shell=True, cwd=work_dir)

	for job_dir in job_dirs: rmtree(job_dir)

def collect_analysis():
# function that collects analysis results

	work_dir = path.abspath("work")
	job_dirs = glob(path.join(work_dir, "analysisjob*"))
	job_dirs = sorted(job_dirs, key=lambda x: int(findall("\d+", path.split(x)[-1])[0]))

	while True:
		sleep(2)
		if all([path.exists(path.join(job_dir, "jobdone.info")) for job_dir in job_dirs]): break
	sleep(2)

	dest_dir = path.join(work_dir, "analysis")
	if not path.exists(dest_dir): mkdir(dest_dir)

	for job_id in range(len(job_dirs)):
		
		job_dir = job_dirs[job_id]
		centrality = params['main']['centrality'][job_id].replace('-', '').replace('%', '')

		for aFile in params['analysis']['save_files']:
			rename(path.join(job_dir, aFile), path.join(dest_dir, aFile.replace(".dat", f"{centrality}.dat")))

		rmtree(job_dir)

def collect_dreena(job_id):
# function that collects energy loss results

	work_dir = path.abspath("work")
	job_dir  = path.join(work_dir, f"dreenajob{job_id:d}")
	dest_dir = path.join(work_dir, "analysis")
	if not path.exists(dest_dir): mkdir(dest_dir)

	centrality = params['main']['centrality'][job_id].replace('-', '').replace('%', '')

	while True:
		sleep(2)
		if path.exists(path.join(job_dir, "jobdone.info")): break
	sleep(2)
	
	rename(path.join(job_dir,  "b.dat"), path.join(dest_dir,  f"b{centrality}.dat"))
	rename(path.join(job_dir,  "d.dat"), path.join(dest_dir,  f"d{centrality}.dat"))
	# rename(path.join(job_dir, "ch.dat"), path.join(dest_dir, f"ch{centrality}.dat"))

	rmtree(job_dir)

def collect_all():
# function that collects all model predictions

	src_dir  = path.abspath("work/analysis")
	run_id   = len([f for f in listdir(path.abspath("")) if path.isdir(f) and "analysis" in f])
	dest_dir = path.abspath(f"analysis{run_id:d}")
	if not path.exists(dest_dir): mkdir(dest_dir)

	for aFile in listdir(src_dir): rename(path.join(src_dir, aFile), path.join(dest_dir, aFile))

	rename(path.abspath("work/params.json"), path.join(dest_dir, "params.json"))

	if params['main']['remove_work'] == 1: rmtree(path.abspath("work"))