#!/usr/bin/env python3

from os import path, listdir, mkdir, rename
from shutil import copy, rmtree, copyfile
from glob import glob
import json
from params import params

####################################################################################################################################################
#TRENTO FUNCTIONS:
####################################################################################
#function that generates trento conf file:
def gen_trento_conf(src_dir, jobid):

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
		f.write('projectile = {}\n'.format(params['trento']['projectile']))
		f.write('projectile = {}\n'.format(params['trento']['target']))
		
		f.write('number-events = %d\n' % event_n_per_job)
		
		f.write('grid-max = %f\n' % params['trento']['grid_max'])
		f.write('grid-step = %f\n' % params['trento']['grid_step'])
		
		f.write('cross-section = %f\n' % cross_section[params['trento']['ecm']])
		
		f.write('reduced-thickness = {:.6f}\n'.format(params['trento']['p']))
		f.write('normalization = %f\n' % params['trento']['norm'])
		f.write('fluctuation = %f\n' % params['trento']['k'])
		f.write('nucleon-width = %f\n' % params['trento']['w'])
		f.write('nucleon-min-dist = %f\n' % params['trento']['d'])
		
		f.write('ncoll = true\n')
		f.write('no-header = true\n')
		f.write('output = %s\n' % path.join(src_dir, 'eventstemp'))
		if params['trento']['random_seed'] and params['trento']['random_seed'] > 0:
			f.write('random-seed = %d\n' % params['trento']['random_seed'])
####################################################################################
#function that generates slurm job scripts for trento jobs:
def gen_slurm_job_trento(src_dir, jobid):
	
	trento_src_dir  = path.abspath('models')
	trento_src_dir  = path.join(trento_src_dir, 'trento', 'build', 'src')

	event_n_per_job = [params['main']['trento_event_n']//params['main']['num_of_trento_jobs']]*params['main']['num_of_trento_jobs']
	for i in range(params['main']['trento_event_n']-sum(event_n_per_job)):
		event_n_per_job[i % params['main']['num_of_trento_jobs']] += 1
	event_n_per_job = event_n_per_job[jobid]

	with open(path.join(src_dir, 'jobscript.slurm'), 'w') as f:
		f.write('#!/bin/bash\n')
		f.write('#\n')
		f.write('#SBATCH --job-name=trento%d\n' % jobid)
		f.write('#SBATCH --output=outputfile.txt\n')
		f.write('#\n')
		f.write('#SBATCH --ntasks=1\n')
		f.write('#SBATCH --cpus-per-task=1\n')
		f.write('#SBATCH --time=%d:00:00\n\n' % (event_n_per_job*0.01))
		f.write('(cd %s\n' % trento_src_dir)
		f.write('	./trento -c %s > %s\n' % (path.join(src_dir, 'trento.conf'), path.join(src_dir, 'trento_events.dat')))
		f.write(')\n\n')
		f.write('python3 gen_bcp.py\n\n')
		f.write('echo "job done" > jobdone.info')
####################################################################################
#function that generates trento jobs:
def gen_trento_jobs():
	
	work_dir = path.abspath('work')
	if path.exists(work_dir): rmtree(work_dir)
	mkdir(work_dir)

	#exporting parameters to json file:
	json_params = json.dumps(params, indent=4)
	with open(path.join(work_dir, 'params.json'), 'w') as f: f.write(json_params)

	for job_id in range(params['main']['num_of_trento_jobs']):
		
		job_dir = path.join(work_dir, 'trentojob%d' % job_id)
		if not path.exists(job_dir): mkdir(job_dir)

		copy(path.abspath('utils/gen_bcp.py'), job_dir)

		gen_trento_conf(job_dir, job_id)
		gen_slurm_job_trento(job_dir, job_id)
##################################################################################################################
#function that generates slurm job scripts for trentoavg jobs:
def gen_slurm_job_trentoavg(jobdir, jobid, srcdir, eidlow, eidhigh):
	
	with open(path.join(jobdir, 'jobscript.slurm'), 'w') as f:
		f.write('#!/bin/bash\n')
		f.write('#\n')
		f.write('#SBATCH --job-name=trentoavg{0:d}\n'.format(jobid))
		f.write('#SBATCH --output=outputfile.txt\n')
		f.write('#\n')
		f.write('#SBATCH --ntasks=1\n')
		f.write('#SBATCH --cpus-per-task=1\n')
		f.write('#SBATCH --time=5:00:00\n\n')
		f.write('./trentoavgc {0:s} {1:d} {2:d} '.format(srcdir, eidlow, eidhigh))
		f.write('{0:.2f} {1:.2f} {2:.3f} '.format(*params['trento']['x_hist']))
		f.write('{0:.2f} {1:.2f} {2:.3f}\n\n'.format(*params['trento']['y_hist']))
		f.write('echo "job done" > jobdone.info')
####################################################################################
#function that generates initial condition averagin jobs:
def gen_trentoavg_jobs():

	work_dir = path.abspath('work')

	for job_id in range(len(params['main']['centrality'])):
		
		job_dir = path.join(work_dir, 'trentoavgjob%d' % job_id)
		if not path.exists(job_dir): mkdir(job_dir)

		#exporting parameters to json file:
		json_params = json.dumps(params, indent=4)
		with open(path.join(job_dir, 'params.json'), 'w') as f: f.write(json_params)

		#copying calculation script:
		copy(path.abspath('models/trentoavgc/trentoavgc'),  job_dir)

		#calculating eventIDs for given centrality:
		centrality    = params['main']['centrality'][job_id]
		tot_event_n   = params['main']['trento_event_n']
		cent_low      = int(centrality.replace('%', '').split('-')[0])
		event_id_low  = int(cent_low*tot_event_n/100)
		cent_high     = int(centrality.replace('%', '').split('-')[1])
		event_id_high = int(cent_high*tot_event_n/100 - 1)
		src_dir  	  = path.abspath('work/trentoic')

		#exporting slurm job script:
		gen_slurm_job_trentoavg(job_dir, job_id, src_dir, event_id_low, event_id_high)

####################################################################################################################################################
#OSU-HYDRO FUNCTIONS:
####################################################################################
#function that exports hydro parameters:
def gen_hydro_conf(src_dir):
	
	with open(path.join(src_dir, 'osu-hydro.conf'), 'w') as f:
		f.write("%.2f\n"   % params['hydro']['T0'])
		f.write("%d\n"     % params['hydro']['IEin'])
		f.write("%d\n"     % params['hydro']['InitialURead'])
		f.write("%d\n\n"   % params['hydro']['Initialpitensor'])

		f.write("%.3f\n"   % params['hydro']['DT'])
		f.write("%.2f\n"   % params['hydro']['DXY'])
		f.write("%d\n\n"   % params['hydro']['NLS'])

		f.write("%.3f\n"   % params['hydro']['Edec'])
		f.write("%d\n"     % params['hydro']['NDT'])
		f.write("%d\n\n"   % params['hydro']['NDXY'])

		f.write("%d\n\n"   % params['hydro']['ViscousEqsType'])

		f.write("%.3f\n"   % params['hydro']['VisT0'])
		f.write("%.2f\n"   % params['hydro']['VisHRG'])
		f.write("%.2f\n"   % params['hydro']['VisMin'])
		f.write("%.1f\n"   % params['hydro']['VisSlope'])
		f.write("%.1f\n"   % params['hydro']['VisCrv'])
		f.write("%.6f\n\n" % params['hydro']['VisBeta'])

		f.write("%.3f\n"   % params['hydro']['VisBulkT0'])
		f.write("%.3f\n"   % params['hydro']['VisBulkMax'])
		f.write("%.3f\n"   % params['hydro']['VisBulkWidth'])
		f.write("%d\n"     % params['hydro']['IRelaxBulk'])
		f.write("%.1f\n"   % params['hydro']['BulkTau'])
####################################################################################
#function that generates slurm scripts for hydro jobs:
def gen_slurm_job_hydro(src_dir, jobid):
	
	with open(path.join(src_dir, 'jobscript.slurm'), 'w') as f:
		f.write('#!/bin/bash\n')
		f.write('#\n')
		f.write('#SBATCH --job-name=hydro%d\n' % jobid)
		f.write('#SBATCH --output=outputfile.txt\n')
		f.write('#\n')
		f.write('#SBATCH --ntasks=1\n')
		f.write('#SBATCH --cpus-per-task=1\n')
		f.write('#SBATCH --time=5:00:00\n\n')
		if params['freestream']['turn_on'] == 1: f.write('python3 stream_ic.py\n\n')
		f.write('./osu-hydro\n\n')
		f.write('python3 sample_surface.py\n\n')
		f.write('echo "job done" > jobdone.info')
####################################################################################
#function that generates osu-hydro jobs:
def gen_hydro_jobs():

	work_dir = path.abspath('work')

	for job_id in range(len(params['main']['centrality'])):
		
		job_dir = path.join(work_dir, 'hydrojob%d' % job_id)
		if not path.exists(job_dir): mkdir(job_dir)

		#exporting parameters to json file:
		json_params = json.dumps(params, indent=4)
		with open(path.join(job_dir, 'params.json'), 'w') as f: f.write(json_params)

		#copying initial conditions:
		rename(path.join(work_dir, 'avgsd', 'sdavg{0:d}.dat'.format(job_id)), path.join(job_dir, 'sd.dat'))

		#copying freestream script:
		if params['freestream']['turn_on'] == 1:
			aFile = path.abspath('models')
			aFile = path.join(aFile, 'freestream', 'stream_ic.py')
			if not path.exists(aFile):
				print('Error: could not find freestream script. Aborting...')
				return False
			else:
				copy(aFile, job_dir)

		#copying osu-hydro exec
		aFile = path.abspath('models')
		aFile = path.join(aFile, 'osu-hydro', 'build' ,'hydro', 'bin', 'osu-hydro')
		if not path.exists(aFile):
			print('Error: could not find osu-hydro executable. Aborting...')
			return False
		else:
			copy(aFile, job_dir)

		#exporting osu-hydro configuration file:
		gen_hydro_conf(job_dir)

		#copying eos
		aFile = path.abspath('models')
		aFile = path.join(aFile, 'osu-hydro', 'eos', 'eos.dat')
		if not path.exists(aFile):
			print('Error: could not find eos table. Aborting...')
			return False
		else:
			copy(aFile, job_dir)

		#copying sample_surface:
		aFile = path.abspath('models')
		aFile = path.join(aFile, 'frzout', 'sample_surface.py')
		if not path.exists(aFile):
			print('Error: could not find frzout script. Aborting...')
			return False
		else:
			copy(aFile, job_dir)

		#generating slurm scripts:
		gen_slurm_job_hydro(job_dir, job_id)

	rmtree(path.join(work_dir, 'avgsd'))

	return True

####################################################################################################################################################
#URQMD FUNCTIONS:
####################################################################################
#function that generates slurm scripts for hydro jobs:
def gen_slurm_job_urqmd(src_dir, jobid):
	
	with open(path.join(src_dir, 'jobscript.slurm'), 'w') as f:
		f.write('#!/bin/bash\n')
		f.write('#\n')
		f.write('#SBATCH --job-name=urqmd%d\n' % jobid)
		f.write('#SBATCH --output=outputfile.txt\n')
		f.write('#\n')
		f.write('#SBATCH --ntasks=1\n')
		f.write('#SBATCH --cpus-per-task=1\n')
		f.write('#SBATCH --time=5:00:00\n\n')
		f.write('./afterburner particles_in_%d.dat particles_out.dat\n\n' % jobid)
		f.write('echo "job done" > jobdone.info')
####################################################################################
#function that generates osu-hydro jobs:
def gen_urqmd_jobs(hydrojobid):

	work_dir  = path.abspath('work')
	hydro_dir = path.join(work_dir, 'hydrojob%d' % hydrojobid)

	for job_id in range(params['main']['num_of_urqmd_jobs']):
		
		#generating job directories:
		job_dir = path.join(work_dir, 'urqmdjob%d' % job_id)
		if not path.exists(job_dir): mkdir(job_dir)

		#copying freezout particle lists:
		particle_list_file = path.join(hydro_dir, 'particles_in_%d.dat' % job_id)
		copy(particle_list_file, job_dir)

		#copying executables:
		src_dir = path.abspath('models')
		src_dir = path.join(src_dir, 'urqmd-afterburner', 'build')
		src_dir = path.join(src_dir, 'hadrontransport', 'bin')
		for aFile in glob(path.join(src_dir, '*')):
			if not path.exists(aFile):
				print('Error: could not find %s executable. Aborting...' % path.split(aFile)[-1])
				return False
			else:
				copy(aFile, job_dir)

		gen_slurm_job_urqmd(job_dir, job_id)

	rmtree(hydro_dir)

	return True

####################################################################################################################################################
#ANALYSIS FUNCTIONS:
####################################################################################
#function that generates slurm scripts for analysis jobs:
def gen_slurm_job_analysis(src_dir, jobid):
	
	with open(path.join(src_dir, 'jobscript.slurm'), 'w') as f:
		f.write('#!/bin/bash\n')
		f.write('#\n')
		f.write('#SBATCH --job-name=analysis%d\n' % jobid)
		f.write('#SBATCH --output=outputfile.txt\n')
		f.write('#\n')
		f.write('#SBATCH --ntasks=1\n')
		f.write('#SBATCH --cpus-per-task=1\n')
		f.write('#SBATCH --time=5:00:00\n\n')
		f.write('python3 analyse.py\n')
		f.write('python3 reference_flow.py qn.dat > intflows.dat\n\n')
		f.write('echo "job done" > jobdone.info')
####################################################################################
#function that generates analysis jobs:
def gen_analysis_jobs():

	work_dir  = path.abspath('work')
	urqmd_dir = path.join(work_dir, 'urqmd')

	for job_id in range(len(params['main']['centrality'])):
		
		job_dir = path.join(work_dir, 'analysisjob%d' % job_id)
		if not path.exists(job_dir): mkdir(job_dir)

		#copying analysis scripts:
		src_dir = path.abspath('models')
		src_dir = path.join(src_dir, 'analysis')
		for aFile in glob(path.join(src_dir, '*')):
			if not path.exists(aFile):
				print('Error: could not find %s scipt. Aborting...' % path.split(aFile)[-1])
				return False
			else:
				copy(aFile, job_dir)

		#exporting parameters to json file:
		json_params = json.dumps(params, indent=4)
		with open(path.join(job_dir, 'params.json'), 'w') as f: f.write(json_params)

		#copying urqmd out particle files:
		rename(path.join(urqmd_dir, 'particles_out_%d.dat' % job_id), path.join(job_dir, 'particles_out.dat'))

		gen_slurm_job_analysis(job_dir, job_id)

	rmtree(urqmd_dir)

	return True

####################################################################################################################################################
#DREENA FUNCTIONS:
####################################################################################
def gen_dreena_conf(dsrcdir, jobdir):
	with open(path.join(jobdir, 'dreena.conf'), 'w') as f:
		f.write('src_dir_path = {0:s}\n'.format(dsrcdir))
		f.write('sNN = {0:d}GeV\n'.format(params['trento']['ecm']))
		f.write('xB = {0:.1f}\n'.format(params['dreena']['xB']))
		f.write('xGridN = {0:d}\n'.format(params['dreena']['xGridN']))
		f.write('yGridN = {0:d}\n'.format(params['dreena']['yGridN']))
		f.write('phiGridN = {0:d}\n'.format(params['dreena']['phiGridN']))
		f.write('TIMESTEP = {0:.2f}\n'.format(params['dreena']['TIMESTEP']))
		f.write('TCRIT = {0:.3f}\n'.format(params['dreena']['TCRIT']))
####################################################################################
def gen_dssffs_conf(dsrcdir, jobdir):
	with open(path.join(jobdir, 'dssffs.conf'), 'w') as f:
		f.write('src_dir_path = {0:s}\n'.format(path.join(dsrcdir, 'DSSFFsV5.0m')))
		f.write('sNN = {0:d}GeV\n'.format(params['trento']['ecm']))
		f.write('xB = {0:.1f}\n'.format(params['dreena']['xB']))
####################################################################################
def gen_slurm_job_dreena(jobdir, jobid):
	with open(path.join(jobdir, 'jobscript.slurm'), 'w') as f:
		f.write('#!/bin/bash\n')
		f.write('#\n')
		f.write('#SBATCH --job-name=eloss%d\n' % jobid)
		f.write('#SBATCH --output=outputfile.txt\n')
		f.write('#\n')
		f.write('#SBATCH --ntasks=1\n')
		f.write('#SBATCH --cpus-per-task={0:d}\n'.format(params['dreena']['NUM_THREADS']))
		f.write('#SBATCH --time=1:00:00\n\n')
		f.write('python3 run_eloss.py\n\n')
		f.write('echo "job done" > jobdone.info')
####################################################################################
#function that generates energy loss jobs:
def gen_dreena_jobs(job_id):

	work_dir  = path.abspath('work')

	job_dir = path.join(work_dir, 'dreenajob%d' % job_id)
	if not path.exists(job_dir): mkdir(job_dir)

	#copying DREENAA and DSSFFs executables:
	dreena_src_dir = path.abspath('models/dreena')
	copy(path.join(dreena_src_dir, 'DREENAA'), job_dir)
	copy(path.join(dreena_src_dir, 'DSSFFsV5.0m', 'DSSFFs'), job_dir)

	#copying run_eloss.py script
	copy(path.abspath('utils/run_eloss.py'), job_dir)

	#exporting parameters to json file:
	json_params = json.dumps(params, indent=4)
	with open(path.join(job_dir, 'params.json'), 'w') as f: f.write(json_params)

	#moving binary collsion density and temperature evolution:
	rename(path.join(work_dir, 'bcdens',    'bcdensity{0:d}.dat'.format(job_id)), path.join(job_dir, 'bcdensity.dat'))
	rename(path.join(work_dir, 'tempevols',  'tempevol{0:d}.dat'.format(job_id)), path.join(job_dir,  'tempevol.dat'))

	gen_dreena_conf(dreena_src_dir, job_dir)
	gen_dssffs_conf(dreena_src_dir, job_dir)
	gen_slurm_job_dreena(job_dir, job_id)