#!/usr/bin/env python3

from os import path
from glob import glob
from subprocess import call, Popen, DEVNULL
from params import params

def submit_trento_jobs():
	for job_dir in glob(path.abspath('work/trentojob*')):
		if params['main']['batch_system'] == 'slurm':
			call('sbatch jobscript.slurm', shell=True, cwd=job_dir, stdout=DEVNULL)
		else:
			Popen('bash jobscript.slurm', shell=True, cwd=job_dir, stdout=DEVNULL)

def submit_trentoavg_jobs():
	for job_dir in glob(path.abspath('work/trentoavgjob*')):
		if params['main']['batch_system'] == 'slurm':
			call('sbatch jobscript.slurm', shell=True, cwd=job_dir, stdout=DEVNULL)
		else:
			Popen('bash jobscript.slurm', shell=True, cwd=job_dir, stdout=DEVNULL)

def submit_hydro_jobs():
	for job_dir in glob(path.abspath('work/hydrojob*')):
		if params['main']['batch_system'] == 'slurm':
			call('sbatch jobscript.slurm', shell=True, cwd=job_dir, stdout=DEVNULL)
		else:
			Popen('bash jobscript.slurm', shell=True, cwd=job_dir, stdout=DEVNULL)

def submit_urqmd_jobs():
	for job_dir in glob(path.abspath('work/urqmdjob*')):
		if params['main']['batch_system'] == 'slurm':
			call('sbatch jobscript.slurm', shell=True, cwd=job_dir, stdout=DEVNULL)
		else:
			Popen('bash jobscript.slurm', shell=True, cwd=job_dir, stdout=DEVNULL)

def submit_analysis_jobs():
	for job_dir in glob(path.abspath('work/analysisjob*')):
		if params['main']['batch_system'] == 'slurm':
			call('sbatch jobscript.slurm', shell=True, cwd=job_dir, stdout=DEVNULL)
		else:
			Popen('bash jobscript.slurm', shell=True, cwd=job_dir, stdout=DEVNULL)

def submit_dreena_jobs(job_id):
	job_dir = path.abspath('work/dreenajob{0:d}'.format(job_id))
	if params['main']['batch_system'] == 'slurm':
		call('sbatch jobscript.slurm', shell=True, cwd=job_dir, stdout=DEVNULL)
	else:
		Popen('bash jobscript.slurm', shell=True, cwd=job_dir, stdout=DEVNULL)