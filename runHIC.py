#!/usr/bin/env python3

from utils.prerequisites import prerequisites
from utils.update_parameters import update_params
from utils.generate_jobs import generateJobs
from utils.submit_jobs import submitJobs
from params import params

from subprocess import call

if __name__ == '__main__':

	# updating parameters:
	update_params()

	cp = prerequisites(params)
	gj = generateJobs(params)
	sj = submitJobs(params)

	# checking prerequisites and executiables and recompile:
	cp.check_prerequisites()
	cp.check_execs()
	cp.recompile()

	#####################################################################
	#running trento:
	gj.gen_trento_jobs()
	sj.submit_trento_jobs()
	cd.collect_trento()

	#####################################################################
	#averaging trento:
	gj.gen_trentoavg_jobs()
	sj.submit_trentoavg_jobs()
	cd.collect_trentoavg()

	#####################################################################
	#running freestream+hydro+frzout:
	gj.gen_hydro_jobs()
	sj.submit_hydro_jobs()
	cd.collect_hydro()
	
	#####################################################################
	#running urqmd:
	for hydro_job_id in range(len(params['main']['centrality'])):
		gj.gen_urqmd_jobs(hydro_job_id)
		sj.submit_urqmd_jobs()
		cd.collect_urqmd(hydro_job_id)

	#####################################################################
	#running analysis:
	gj.gen_analysis_jobs()
	sj.submit_analysis_jobs()
	cd.collect_analysis()

	#####################################################################
	#running energy loss:
	for cent_job_id in range(len(params['main']['centrality'])):
		gj.gen_dreena_jobs(cent_job_id)
		sj.submit_dreena_jobs(cent_job_id)
		cd.collect_dreena(cent_job_id)

	#####################################################################
	#collect all model predictions:
	cd.collect_all()