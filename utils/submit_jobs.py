#!/usr/bin/env python3

from os import path
from glob import glob
from subprocess import call, Popen, DEVNULL

class submitJobs:
	def __init__(self, params):
		self.params = params

	def submit_trento_jobs(self):
		for job_dir in glob(path.abspath("work/trentojob*")):
			if self.params['main']['batch_system'] == 'slurm':
				call("sbatch jobscript.slurm", shell=True, cwd=job_dir, stdout=DEVNULL)
			elif self.params['main']['batch_system'] == 'local':
				Popen("bash jobscript.slurm", shell=True, cwd=job_dir, stdout=DEVNULL)

	def submit_trentoavg_jobs(self):
		for job_dir in glob(path.abspath("work/trentoavgjob*")):
			if self.params['main']['batch_system'] == 'slurm':
				call("sbatch jobscript.slurm", shell=True, cwd=job_dir, stdout=DEVNULL)
			elif self.params['main']['batch_system'] == 'local':
				Popen("bash jobscript.slurm", shell=True, cwd=job_dir, stdout=DEVNULL)

	def submit_hydro_jobs(self):
		for job_dir in glob(path.abspath("work/hydrojob*")):
			if self.params['main']['batch_system'] == 'slurm':
				call("sbatch jobscript.slurm", shell=True, cwd=job_dir, stdout=DEVNULL)
			elif self.params['main']['batch_system'] == 'local':
				Popen("bash jobscript.slurm", shell=True, cwd=job_dir, stdout=DEVNULL)

	def submit_urqmd_jobs(self):
		for job_dir in glob(path.abspath("work/urqmdjob*")):
			if self.params['main']['batch_system'] == 'slurm':
				call("sbatch jobscript.slurm", shell=True, cwd=job_dir, stdout=DEVNULL)
			elif self.params['main']['batch_system'] == 'local':
				Popen("bash jobscript.slurm", shell=True, cwd=job_dir, stdout=DEVNULL)

	def submit_analysis_jobs(self):
		for job_dir in glob(path.abspath("work/analysisjob*")):
			if self.params['main']['batch_system'] == 'slurm':
				call("sbatch jobscript.slurm", shell=True, cwd=job_dir, stdout=DEVNULL)
			elif self.params['main']['batch_system'] == 'local':
				Popen("bash jobscript.slurm", shell=True, cwd=job_dir, stdout=DEVNULL)

	def submit_dreena_jobs(self, job_id):
		job_dir = path.abspath(f"work/dreenajob{job_id:d}")
		if self.params['main']['batch_system'] == 'slurm':
			call("sbatch jobscript.slurm", shell=True, cwd=job_dir, stdout=DEVNULL)
		elif self.params['main']['batch_system'] == 'local':
			Popen("bash jobscript.slurm", shell=True, cwd=job_dir, stdout=DEVNULL)