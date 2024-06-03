#!/usr/bin/env python3

from os import path, mkdir, rename
from shutil import copy, rmtree
from glob import glob
import json

class generateJobs():
	def __init__(self, params):
		self.params = params	

	def __gen_trento_conf(self, src_dir, jobid):
		cross_section = {
			200:  4.23,
			2760: 6.40,
			5020: 7.00,
			7000: 7.32,
		}

		event_n_per_job = [self.params['main']['trento_event_n']//self.params['main']['num_of_trento_jobs']]*self.params['main']['num_of_trento_jobs']
		for i in range(self.params['main']['trento_event_n']-sum(event_n_per_job)):
			event_n_per_job[i % self.params['main']['num_of_trento_jobs']] += 1
		event_n_per_job = event_n_per_job[jobid]

		with open(path.join(src_dir, 'trento.conf'), 'w') as f:
			f.write(f"projectile = {self.params['trento']['projectile']}\n")
			f.write(f"projectile = {self.params['trento']['target']}\n")
			
			f.write(f"number-events = {event_n_per_job:d}\n")
			
			f.write(f"grid-max = {self.params['trento']['grid_max']:.6f}\n")
			f.write(f"grid-step = {self.params['trento']['grid_step']:.6f}\n")
			
			f.write(f"cross-section = {cross_section[self.params['trento']['ecm']]:.2f}\n")
			
			f.write(f"reduced-thickness = {self.params['trento']['p']:.6f}\n")
			f.write(f"normalization = {self.params['trento']['norm']:.6f}\n")
			f.write(f"fluctuation = {self.params['trento']['k']:.6f}\n")
			f.write(f"nucleon-width = {self.params['trento']['w']:.6f}\n")
			f.write(f"nucleon-min-dist = {self.params['trento']['d']:.6f}\n")
			
			f.write("ncoll = true\n")
			f.write("no-header = true\n")
			f.write(f"output = {path.join(src_dir, 'eventstemp')}\n")
			if self.params['trento']['random_seed'] and self.params['trento']['random_seed'] > 0:
				f.write(f"random-seed = {self.params['trento']['random_seed']:d}\n")

	def __gen_slurm_job_trento(self, src_dir, jobid):
		trento_src_dir  = path.abspath("models")
		trento_src_dir  = path.join(trento_src_dir, "trento", "build", "src")

		event_n_per_job = [self.params['main']['trento_event_n']//self.params['main']['num_of_trento_jobs']]*self.params['main']['num_of_trento_jobs']
		for i in range(self.params['main']['trento_event_n']-sum(event_n_per_job)):
			event_n_per_job[i % self.params['main']['num_of_trento_jobs']] += 1
		event_n_per_job = event_n_per_job[jobid]

		with open(path.join(src_dir, "jobscript.slurm"), 'w') as f:
			f.write("#!/bin/bash\n")
			f.write("#\n")
			f.write(f"#SBATCH --job-name=trento{jobid:d}\n")
			f.write("#SBATCH --output=outputfile.txt\n")
			f.write("#\n")
			f.write("#SBATCH --ntasks=1\n")
			f.write("#SBATCH --cpus-per-task=1\n")
			f.write(f"#SBATCH --time={int(event_n_per_job*0.01):d}:00:00\n\n")
			f.write(f"(cd {trento_src_dir}\n")
			f.write(f"	./trento -c {path.join(src_dir, 'trento.conf')} > {path.join(src_dir, 'trento_events.dat')}\n")
			f.write(")\n\n")
			f.write("python3 gen_bcp.py\n\n")
			f.write("echo 'job done' > jobdone.info")

	def gen_trento_jobs(self):
		work_dir = path.abspath("work")
		if path.exists(work_dir): rmtree(work_dir)
		mkdir(work_dir)

		#exporting parameters to json file:
		json_params = json.dumps(self.params, indent=4)
		with open(path.join(work_dir, "params.json"), 'w') as f: f.write(json_params)

		for job_id in range(self.params['main']['num_of_trento_jobs']):		
			job_dir = path.join(work_dir, f"trentojob{job_id:d}")
			if not path.exists(job_dir): mkdir(job_dir)
			copy(path.abspath("utils/gen_bcp.py"), job_dir)
			self.__gen_trento_conf(job_dir, job_id)
			self.__gen_slurm_job_trento(job_dir, job_id)

	def __gen_slurm_job_trentoavg(self, jobdir, jobid, srcdir, eidlow, eidhigh):
		with open(path.join(jobdir, "jobscript.slurm"), 'w') as f:
			f.write("#!/bin/bash\n")
			f.write("#\n")
			f.write(f"#SBATCH --job-name=trentoavg{jobid:d}\n")
			f.write("#SBATCH --output=outputfile.txt\n")
			f.write("#\n")
			f.write("#SBATCH --ntasks=1\n")
			f.write("#SBATCH --cpus-per-task=1\n")
			f.write("#SBATCH --time=5:00:00\n\n")
			f.write(f"./trentoavgc {srcdir} {eidlow:d} {eidhigh:d} ")
			f.write(f"{self.params['trento']['x_hist'][0]:.6f} {self.params['trento']['x_hist'][1]:.6f} {self.params['trento']['x_hist'][2]:.6f} ")
			f.write(f"{self.params['trento']['y_hist'][0]:.6f} {self.params['trento']['y_hist'][1]:.6f} {self.params['trento']['y_hist'][2]:.6f}\n\n")
			f.write("echo 'job done' > jobdone.info")

	def gen_trentoavg_jobs(self):
		work_dir = path.abspath("work")

		for job_id in range(len(self.params['main']['centrality'])):		
			job_dir = path.join(work_dir, f"trentoavgjob{job_id:d}")
			if not path.exists(job_dir): mkdir(job_dir)

			#exporting parameters to json file:
			json_params = json.dumps(self.params, indent=4)
			with open(path.join(job_dir, "params.json"), 'w') as f: f.write(json_params)

			#copying calculation script:
			copy(path.abspath("models/trentoavgc/trentoavgc"),  job_dir)

			#calculating eventIDs for given centrality:
			centrality    = self.params['main']['centrality'][job_id]
			tot_event_n   = self.params['main']['trento_event_n']
			cent_low      = int(centrality.replace('%', '').split('-')[0])
			event_id_low  = int(cent_low*tot_event_n/100)
			cent_high     = int(centrality.replace('%', '').split('-')[1])
			event_id_high = int(cent_high*tot_event_n/100 - 1)
			src_dir  	  = path.abspath("work/trentoic")

			#exporting slurm job script:
			self.__gen_slurm_job_trentoavg(job_dir, job_id, src_dir, event_id_low, event_id_high)

	def __gen_hydro_conf(self, src_dir):
		with open(path.join(src_dir, "osu-hydro.conf"), 'w') as f:
			f.write(f"{self.params['hydro']['T0']:.6f}\n")
			f.write(f"{self.params['hydro']['IEin']:d}\n")
			f.write(f"{self.params['hydro']['InitialURead']:d}\n")
			f.write(f"{self.params['hydro']['Initialpitensor']:d}\n\n")

			f.write(f"{self.params['hydro']['DT']:.6f}\n")
			f.write(f"{self.params['hydro']['DXY']:.6f}\n")
			f.write(f"{self.params['hydro']['NLS']:d}\n\n")

			f.write(f"{self.params['hydro']['Edec']:.6f}\n")
			f.write(f"{self.params['hydro']['NDT']:d}\n")
			f.write(f"{self.params['hydro']['NDXY']:d}\n\n")

			f.write(f"{self.params['hydro']['ViscousEqsType']:d}\n\n")

			f.write(f"{self.params['hydro']['VisT0']:.6f}\n")
			f.write(f"{self.params['hydro']['VisHRG']:.6f}\n")
			f.write(f"{self.params['hydro']['VisMin']:.6f}\n")
			f.write(f"{self.params['hydro']['VisSlope']:.6f}\n")
			f.write(f"{self.params['hydro']['VisCrv']:.6f}\n")
			f.write(f"{self.params['hydro']['VisBeta']:.6f}\n\n")

			f.write(f"{self.params['hydro']['VisBulkT0']:.6f}\n")
			f.write(f"{self.params['hydro']['VisBulkMax']:.6f}\n")
			f.write(f"{self.params['hydro']['VisBulkWidth']:.6f}\n")
			f.write(f"{self.params['hydro']['IRelaxBulk']:d}\n")
			f.write(f"{self.params['hydro']['BulkTau']:.6f}\n")

	def __gen_slurm_job_hydro(self, src_dir, jobid):
		with open(path.join(src_dir, "jobscript.slurm"), 'w') as f:
			f.write("#!/bin/bash\n")
			f.write("#\n")
			f.write(f"#SBATCH --job-name=hydro{jobid:d}\n")
			f.write("#SBATCH --output=outputfile.txt\n")
			f.write("#\n")
			f.write("#SBATCH --ntasks=1\n")
			f.write("#SBATCH --cpus-per-task=1\n")
			f.write("#SBATCH --time=5:00:00\n\n")
			if self.params['freestream']['turn_on'] == 1:
				f.write("python3 streamIC.py\n\n")
			f.write("./osu-hydro\n\n")
			f.write("python3 sampleSurface.py\n\n")
			f.write("echo 'job done' > jobdone.info")

	def gen_hydro_jobs(self):
		work_dir = path.abspath("work")

		for job_id in range(len(self.params['main']['centrality'])):
			
			job_dir = path.join(work_dir, f"hydrojob{job_id:d}")
			if not path.exists(job_dir): mkdir(job_dir)

			#exporting parameters to json file:
			json_params = json.dumps(self.params, indent=4)
			with open(path.join(job_dir, "params.json"), 'w') as f: f.write(json_params)

			#copying initial conditions:
			rename(path.join(work_dir, "avgsd", f"sdavg{job_id:d}.dat"), path.join(job_dir, "sd.dat"))

			#copying freestream script:
			if self.params['freestream']['turn_on'] == 1:
				aFile = path.abspath("models")
				aFile = path.join(aFile, "freestream", "streamIC.py")
				if not path.exists(aFile):
					print("Error: could not find freestream script. Aborting...")
					return False
				copy(aFile, job_dir)

			#copying osu-hydro exec
			aFile = path.abspath("models")
			aFile = path.join(aFile, "osu-hydro", "build" ,"hydro", "bin", "osu-hydro")
			if not path.exists(aFile):
				print("Error: could not find osu-hydro executable. Aborting...")
				return False
			else:
				copy(aFile, job_dir)

			#exporting osu-hydro configuration file:
			self.__gen_hydro_conf(job_dir)

			#copying eos
			aFile = path.abspath("models")
			aFile = path.join(aFile, "osu-hydro", "eos", "eos.dat")
			if not path.exists(aFile):
				print("Error: could not find eos table. Aborting...")
				return False
			copy(aFile, job_dir)

			#copying sample_surface:
			aFile = path.abspath("models")
			aFile = path.join(aFile, "frzout", "sampleSurface.py")
			if not path.exists(aFile):
				print("Error: could not find frzout script. Aborting...")
				return False
			copy(aFile, job_dir)

			#generating slurm scripts:
			self.__gen_slurm_job_hydro(job_dir, job_id)

		rmtree(path.join(work_dir, "avgsd"))

	def __gen_slurm_job_urqmd(self, src_dir, jobid):
		with open(path.join(src_dir, "jobscript.slurm"), 'w') as f:
			f.write("#!/bin/bash\n")
			f.write("#\n")
			f.write(f"#SBATCH --job-name=urqmd{jobid:d}\n")
			f.write("#SBATCH --output=outputfile.txt\n")
			f.write("#\n")
			f.write("#SBATCH --ntasks=1\n")
			f.write("#SBATCH --cpus-per-task=1\n")
			f.write("#SBATCH --time=5:00:00\n\n")
			f.write(f"./afterburner particles_in_{jobid:d}.dat particles_out.dat\n\n")
			f.write("echo 'job done' > jobdone.info")

	def gen_urqmd_jobs(self, hydrojobid):
		work_dir  = path.abspath("work")
		hydro_dir = path.join(work_dir, f"hydrojob{hydrojobid:d}")

		for job_id in range(self.params['main']['num_of_urqmd_jobs']):
			
			#generating job directories:
			job_dir = path.join(work_dir, f"urqmdjob{job_id:d}")
			if not path.exists(job_dir): mkdir(job_dir)

			#copying freezout particle lists:
			particle_list_file = path.join(hydro_dir, f"particles_in_{job_id:d}.dat")
			copy(particle_list_file, job_dir)

			#copying executables:
			src_dir = path.abspath("models")
			src_dir = path.join(src_dir, "urqmd-afterburner", "build")
			src_dir = path.join(src_dir, "hadrontransport", "bin")
			for aFile in glob(path.join(src_dir, "*")):
				if not path.exists(aFile):
					print(f"Error: could not find {path.split(aFile)[-1]} executable. Aborting...")
					return False
				else:
					copy(aFile, job_dir)

			self.__gen_slurm_job_urqmd(job_dir, job_id)

		rmtree(hydro_dir)

	def __gen_slurm_job_analysis(self, src_dir, jobid):
		with open(path.join(src_dir, "jobscript.slurm"), 'w') as f:
			f.write("#!/bin/bash\n")
			f.write("#\n")
			f.write(f"#SBATCH --job-name=analysis{jobid:d}\n")
			f.write("#SBATCH --output=outputfile.txt\n")
			f.write("#\n")
			f.write("#SBATCH --ntasks=1\n")
			f.write("#SBATCH --cpus-per-task=1\n")
			f.write("#SBATCH --time=5:00:00\n\n")
			f.write("python3 analyse.py\n")
			f.write("python3 reference_flow.py qn.dat > intflows.dat\n\n")
			f.write("echo 'job done' > jobdone.info")

	def gen_analysis_jobs(self):
		work_dir  = path.abspath("work")
		urqmd_dir = path.join(work_dir, "urqmd")

		for job_id in range(len(self.params['main']['centrality'])):
			
			job_dir = path.join(work_dir, f"analysisjob{job_id:d}")
			if not path.exists(job_dir): mkdir(job_dir)

			#copying analysis scripts:
			src_dir = path.abspath("utils")
			for aFile in ["analyse.py", "reference_flow.py"]:
				copy(path.join(src_dir, aFile), job_dir)

			#exporting parameters to json file:
			json_params = json.dumps(self.params, indent=4)
			with open(path.join(job_dir, "params.json"), 'w') as f: f.write(json_params)

			#copying urqmd out particle files:
			rename(path.join(urqmd_dir, f"particles_out_{job_id:d}.dat"), path.join(job_dir, "particles_out.dat"))

			self.__gen_slurm_job_analysis(job_dir, job_id)

		rmtree(urqmd_dir)

	def __gen_eloss_conf(self, dreenasrcdir, dssffsdir, jobdir):
		with open(path.join(jobdir, "dreena.conf"), 'w') as f:
			f.write(f"modelDir = {dreenasrcdir}\n")
			f.write(f"sNN = {self.params['trento']['ecm']:d}GeV\n")
			f.write(f"xB = {self.params['dreena']['xB']:.6f}\n")
			f.write(f"xGridN = {self.params['dreena']['xGridN']:d}\n")
			f.write(f"yGridN = {self.params['dreena']['yGridN']:d}\n")
			f.write(f"phiGridN = {self.params['dreena']['phiGridN']:d}\n")
			f.write(f"TIMESTEP = {self.params['dreena']['TIMESTEP']:.6f}\n")
			f.write(f"TCRIT = {self.params['dreena']['TCRIT']:.6f}\n")		
		if path.exists(path.abspath("models/DSSFFs")):
			with open(path.join(jobdir, "dssffs.conf"), 'w') as f:
				f.write(f"modelDir = {dssffsdir}\n")
				f.write(f"sNN = {self.params['trento']['ecm']:d}GeV\n")

	def __gen_slurm_job_dreena(self, jobdir, jobid):
		with open(path.join(jobdir, "jobscript.slurm"), 'w') as f:
			f.write("#!/bin/bash\n")
			f.write("#\n")
			f.write("#SBATCH --job-name=eloss%d\n" % jobid)
			f.write("#SBATCH --output=outputfile.txt\n")
			f.write("#\n")
			f.write("#SBATCH --ntasks=1\n")
			f.write(f"#SBATCH --cpus-per-task={self.params['dreena']['NUM_THREADS']:d}\n")
			f.write("#SBATCH --time=1:00:00\n\n")
			f.write("python3 run_eloss.py\n\n")
			f.write("echo 'job done' > jobdone.info")

	def gen_dreena_jobs(self, job_id):
		work_dir  = path.abspath("work")

		job_dir = path.join(work_dir, f"dreenajob{job_id:d}")
		if not path.exists(job_dir): mkdir(job_dir)

		#copying DREENAA and DSSFFs executables:
		dreena_src_dir = path.abspath("models/avgictvuddreena")
		copy(path.join(dreena_src_dir, "DREENAA"), job_dir)
		dssffs_src_dir = path.abspath("models/DSSFFs")
		if path.exists(dssffs_src_dir):
			copy(path.join(dssffs_src_dir, "DSSFFs"), job_dir)

		#copying run_eloss.py script
		copy(path.abspath("utils/run_eloss.py"), job_dir)

		#exporting parameters to json file:
		json_params = json.dumps(self.params, indent=4)
		with open(path.join(job_dir, "params.json"), 'w') as f: f.write(json_params)

		#moving binary collsion density and temperature evolution:
		rename(path.join(work_dir, "bcdens",    f"bcdensity{job_id:d}.dat"), path.join(job_dir, "bcdensity.dat"))
		rename(path.join(work_dir, "tempevols",  f"tempevol{job_id:d}.dat"), path.join(job_dir,  "tempevol.dat"))

		self.__gen_eloss_conf(dreena_src_dir, dssffs_src_dir, job_dir)
		self.__gen_slurm_job_dreena(job_dir, job_id)