#!/usr/bin/env python3

from os import path, listdir, mkdir, rename
from shutil import copy, rmtree, copyfile
from glob import glob
import json
from params import params

####################################################################################################################################################
#TRENTO FUNCTIONS:

def gen_trento_conf(src_dir, jobid):
# function that generates trento conf file

	cross_section = {
		200:  4.23,
		2760: 6.40,
		5020: 7.00,
		7000: 7.32,
	}

	event_n_per_job = [params['main']['trento_event_n']//params['main']['num_of_trento_jobs']]*params['main']['num_of_trento_jobs']
	for i in range(params['main']['trento_event_n']-sum(event_n_per_job)):
		event_n_per_job[i % params['main']['num_of_trento_jobs']] += 1
	event_n_per_job = event_n_per_job[jobid]

	with open(path.join(src_dir, 'trento.conf'), 'w') as f:
		f.write(f"projectile = {params['trento']['projectile']}\n")
		f.write(f"projectile = {params['trento']['target']}\n")
		
		f.write(f"number-events = {event_n_per_job:d}\n")
		
		f.write(f"grid-max = {params['trento']['grid_max']:.6f}\n")
		f.write(f"grid-step = {params['trento']['grid_step']:.6f}\n")
		
		f.write(f"cross-section = {cross_section[params['trento']['ecm']]:.2f}\n")
		
		f.write(f"reduced-thickness = {params['trento']['p']:.6f}\n")
		f.write(f"normalization = {params['trento']['norm']:.6f}\n")
		f.write(f"fluctuation = {params['trento']['k']:.6f}\n")
		f.write(f"nucleon-width = {params['trento']['w']:.6f}\n")
		f.write(f"nucleon-min-dist = {params['trento']['d']:.6f}\n")
		
		f.write("ncoll = true\n")
		f.write("no-header = true\n")
		f.write(f"output = {path.join(src_dir, 'eventstemp')}\n")
		if params['trento']['random_seed'] and params['trento']['random_seed'] > 0:
			f.write(f"random-seed = {params['trento']['random_seed']:d}\n")

def gen_slurm_job_trento(src_dir, jobid):
#function that generates slurm job scripts for trento jobs
	
	trento_src_dir  = path.abspath("models")
	trento_src_dir  = path.join(trento_src_dir, "trento", "build", "src")

	event_n_per_job = [params['main']['trento_event_n']//params['main']['num_of_trento_jobs']]*params['main']['num_of_trento_jobs']
	for i in range(params['main']['trento_event_n']-sum(event_n_per_job)):
		event_n_per_job[i % params['main']['num_of_trento_jobs']] += 1
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

def gen_trento_jobs():
#function that generates trento jobs
	
	work_dir = path.abspath("work")
	if path.exists(work_dir): rmtree(work_dir)
	mkdir(work_dir)

	#exporting parameters to json file:
	json_params = json.dumps(params, indent=4)
	with open(path.join(work_dir, "params.json"), 'w') as f: f.write(json_params)

	for job_id in range(params['main']['num_of_trento_jobs']):		
		job_dir = path.join(work_dir, 'trentojob%d' % job_id)
		if not path.exists(job_dir): mkdir(job_dir)
		copy(path.abspath("utils/gen_bcp.py"), job_dir)
		gen_trento_conf(job_dir, job_id)
		gen_slurm_job_trento(job_dir, job_id)

def gen_slurm_job_trentoavg(jobdir, jobid, srcdir, eidlow, eidhigh):
#function that generates slurm job scripts for trentoavg jobs
	
	with open(path.join(jobdir, "jobscript.slurm"), 'w') as f:
		f.write("#!/bin/bash\n")
		f.write("#\n")
		f.write(f"#SBATCH --job-name=trentoavg{jobid:d}\n")
		f.write(f"#SBATCH --output=outputfile.txt\n")
		f.write("#\n")
		f.write("#SBATCH --ntasks=1\n")
		f.write("#SBATCH --cpus-per-task=1\n")
		f.write("#SBATCH --time=5:00:00\n\n")
		f.write(f"./trentoavgc {srcdir} {eidlow:d} {eidhigh:d} ")
		f.write(f"{params['trento']['x_hist'][0]:.6f} {params['trento']['x_hist'][1]:.6f} {params['trento']['x_hist'][2]:.6f} ")
		f.write(f"{params['trento']['y_hist'][0]:.6f} {params['trento']['y_hist'][1]:.6f} {params['trento']['y_hist'][2]:.6f}\n\n")
		f.write("echo 'job done' > jobdone.info")

def gen_trentoavg_jobs():
#function that generates initial condition averagin jobs

	work_dir = path.abspath("work")

	for job_id in range(len(params['main']['centrality'])):		
		job_dir = path.join(work_dir, f"trentoavgjob{job_id:d}")
		if not path.exists(job_dir): mkdir(job_dir)

		#exporting parameters to json file:
		json_params = json.dumps(params, indent=4)
		with open(path.join(job_dir, 'params.json'), 'w') as f: f.write(json_params)

		#copying calculation script:
		copy(path.abspath("models/trentoavgc/trentoavgc"),  job_dir)

		#calculating eventIDs for given centrality:
		centrality    = params['main']['centrality'][job_id]
		tot_event_n   = params['main']['trento_event_n']
		cent_low      = int(centrality.replace('%', '').split('-')[0])
		event_id_low  = int(cent_low*tot_event_n/100)
		cent_high     = int(centrality.replace('%', '').split('-')[1])
		event_id_high = int(cent_high*tot_event_n/100 - 1)
		src_dir  	  = path.abspath("work/trentoic")

		#exporting slurm job script:
		gen_slurm_job_trentoavg(job_dir, job_id, src_dir, event_id_low, event_id_high)

####################################################################################################################################################
#OSU-HYDRO FUNCTIONS:

def gen_hydro_conf(src_dir):
# function that exports hydro parameters
	
	with open(path.join(src_dir, "osu-hydro.conf"), 'w') as f:
		f.write(f"{params['hydro']['T0']:.6f}\n")
		f.write(f"{params['hydro']['IEin']:d}\n")
		f.write(f"{params['hydro']['InitialURead']:d}\n")
		f.write(f"{params['hydro']['Initialpitensor']:d}\n\n")

		f.write(f"{params['hydro']['DT']:.6f}\n")
		f.write(f"{params['hydro']['DXY']:.6f}\n")
		f.write(f"{params['hydro']['NLS']:d}\n\n")

		f.write(f"{params['hydro']['Edec']:.6f}\n")
		f.write(f"{params['hydro']['NDT']:d}\n")
		f.write(f"{params['hydro']['NDXY']:d}\n\n")

		f.write(f"{params['hydro']['ViscousEqsType']:d}\n\n")

		f.write(f"{params['hydro']['VisT0']:.6f}\n")
		f.write(f"{params['hydro']['VisHRG']:.6f}\n")
		f.write(f"{params['hydro']['VisMin']:.6f}\n")
		f.write(f"{params['hydro']['VisSlope']:.6f}\n")
		f.write(f"{params['hydro']['VisCrv']:.6f}\n")
		f.write(f"{params['hydro']['VisBeta']:.6f}\n\n")

		f.write(f"{params['hydro']['VisBulkT0']:.6f}\n")
		f.write(f"{params['hydro']['VisBulkMax']:.6f}\n")
		f.write(f"{params['hydro']['VisBulkWidth']:.6f}\n")
		f.write(f"{params['hydro']['IRelaxBulk']:d}\n")
		f.write(f"{params['hydro']['BulkTau']:.6f}\n")

def gen_slurm_job_hydro(src_dir, jobid):
# function that generates slurm scripts for hydro jobs
	
	with open(path.join(src_dir, "jobscript.slurm"), 'w') as f:
		f.write("#!/bin/bash\n")
		f.write("#\n")
		f.write(f"#SBATCH --job-name=hydro{jobid:d}\n")
		f.write("#SBATCH --output=outputfile.txt\n")
		f.write("#\n")
		f.write("#SBATCH --ntasks=1\n")
		f.write("#SBATCH --cpus-per-task=1\n")
		f.write("#SBATCH --time=5:00:00\n\n")
		if params['freestream']['turn_on'] == 1:
			f.write("python3 streamIC.py\n\n")
		f.write("./osu-hydro\n\n")
		f.write("python3 sampleSurface.py\n\n")
		f.write("echo 'job done' > jobdone.info")

def gen_hydro_jobs():
# function that generates osu-hydro jobs

	work_dir = path.abspath("work")

	for job_id in range(len(params['main']['centrality'])):
		
		job_dir = path.join(work_dir, f"hydrojob{job_id:d}")
		if not path.exists(job_dir): mkdir(job_dir)

		#exporting parameters to json file:
		json_params = json.dumps(params, indent=4)
		with open(path.join(job_dir, "params.json"), 'w') as f: f.write(json_params)

		#copying initial conditions:
		rename(path.join(work_dir, "avgsd", f"sdavg{job_id:d}.dat"), path.join(job_dir, "sd.dat"))

		#copying freestream script:
		if params['freestream']['turn_on'] == 1:
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
		gen_hydro_conf(job_dir)

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
		gen_slurm_job_hydro(job_dir, job_id)

	rmtree(path.join(work_dir, "avgsd"))

	return True

####################################################################################################################################################
#URQMD FUNCTIONS:

def gen_slurm_job_urqmd(src_dir, jobid):
# function that generates slurm scripts for urqmd jobs
	
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

def gen_urqmd_jobs(hydrojobid):
# function that generates osu-hydro jobs

	work_dir  = path.abspath("work")
	hydro_dir = path.join(work_dir, f"hydrojob{hydrojobid:d}")

	for job_id in range(params['main']['num_of_urqmd_jobs']):
		
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

		gen_slurm_job_urqmd(job_dir, job_id)

	rmtree(hydro_dir)

	return True

####################################################################################################################################################
#ANALYSIS FUNCTIONS:

def gen_slurm_job_analysis(src_dir, jobid):
# function that generates slurm scripts for analysis jobs
	
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

def gen_analysis_jobs():
# function that generates analysis job

	work_dir  = path.abspath("work")
	urqmd_dir = path.join(work_dir, "urqmd")

	for job_id in range(len(params['main']['centrality'])):
		
		job_dir = path.join(work_dir, f"analysisjob{job_id:d}")
		if not path.exists(job_dir): mkdir(job_dir)

		#copying analysis scripts:
		src_dir = path.abspath("models")
		src_dir = path.join(src_dir, "analysis")
		for aFile in glob(path.join(src_dir, '*')):
			if not path.exists(aFile):
				print(f"Error: could not find {path.split(aFile)[-1]} scipt. Aborting...")
				return False
			copy(aFile, job_dir)

		#exporting parameters to json file:
		json_params = json.dumps(params, indent=4)
		with open(path.join(job_dir, "params.json"), 'w') as f: f.write(json_params)

		#copying urqmd out particle files:
		rename(path.join(urqmd_dir, f"particles_out_{job_id:d}.dat"), path.join(job_dir, "particles_out.dat"))

		gen_slurm_job_analysis(job_dir, job_id)

	rmtree(urqmd_dir)

	return True

####################################################################################################################################################
#DREENA FUNCTIONS:

def gen_dreena_conf(dsrcdir, jobdir):
# function that exports dreena parameters
	
	with open(path.join(jobdir, "dreena.conf"), 'w') as f:
		f.write(f"srcDirectory = {dsrcdir}\n")
		f.write(f"sNN = {params['trento']['ecm']:d}GeV\n")
		f.write(f"xB = {params['dreena']['xB']:.6f}\n")
		f.write(f"xGridN = {params['dreena']['xGridN']:d}\n")
		f.write(f"yGridN = {params['dreena']['yGridN']:d}\n")
		f.write(f"phiGridN = {params['dreena']['phiGridN']:d}\n")
		f.write(f"TIMESTEP = {params['dreena']['TIMESTEP']:.6f}\n")
		f.write(f"TCRIT = {params['dreena']['TCRIT']:.6f}\n")

def gen_slurm_job_dreena(jobdir, jobid):
# function that generates slurm scripts for dreena jobs
	
	with open(path.join(jobdir, "jobscript.slurm"), 'w') as f:
		f.write("#!/bin/bash\n")
		f.write("#\n")
		f.write("#SBATCH --job-name=eloss%d\n" % jobid)
		f.write("#SBATCH --output=outputfile.txt\n")
		f.write("#\n")
		f.write("#SBATCH --ntasks=1\n")
		f.write(f"#SBATCH --cpus-per-task={params['dreena']['NUM_THREADS']:d}\n")
		f.write("#SBATCH --time=1:00:00\n\n")
		f.write("python3 run_eloss.py\n\n")
		f.write("echo 'job done' > jobdone.info")

def gen_dreena_jobs(job_id):
# function that generates energy loss jobs

	work_dir  = path.abspath("work")

	job_dir = path.join(work_dir, f"dreenajob{job_id:d}")
	if not path.exists(job_dir): mkdir(job_dir)

	#copying DREENAA and DSSFFs executables:
	dreena_src_dir = path.abspath("models/dreena")
	copy(path.join(dreena_src_dir, "DREENAA"), job_dir)

	#copying run_eloss.py script
	copy(path.abspath("utils/run_eloss.py"), job_dir)

	#exporting parameters to json file:
	json_params = json.dumps(params, indent=4)
	with open(path.join(job_dir, "params.json"), 'w') as f: f.write(json_params)

	#moving binary collsion density and temperature evolution:
	rename(path.join(work_dir, "bcdens",    f"bcdensity{job_id:d}.dat"), path.join(job_dir, "bcdensity.dat"))
	rename(path.join(work_dir, "tempevols",  f"tempevol{job_id:d}.dat"), path.join(job_dir,  "tempevol.dat"))

	gen_dreena_conf(dreena_src_dir, job_dir)
	gen_slurm_job_dreena(job_dir, job_id)