#!/usr/bin/env python3

from os import path
import argparse
from params import params

###################################################################################################################################
#updating dictionary parameters:
def update_params():

	parser = argparse.ArgumentParser()

	#simulation parameters:
	parser.add_argument('--centrality', 		type=str)
	parser.add_argument('--trento_event_n',     type=int)
	parser.add_argument('--num_of_trento_jobs', type=int)
	parser.add_argument('--maxsamples', 		type=int)
	parser.add_argument('--num_of_urqmd_jobs',  type=int)
	parser.add_argument('--remove_work', 		type=int)
	parser.add_argument('--batch_system', 		type=str)
	parser.add_argument('--recompile', 			type=int)

	#TRENTO parameters:
	parser.add_argument('--projectile',	type=str)
	parser.add_argument('--target', 	type=str)
	parser.add_argument('--ecm', 		type=int)

	parser.add_argument('--p',    type=float)
	parser.add_argument('--k',    type=float)
	parser.add_argument('--w',    type=float)
	parser.add_argument('--d',    type=float)
	parser.add_argument('--norm', type=float)

	parser.add_argument('--grid_max',  type=float)
	parser.add_argument('--grid_step', type=float)

	parser.add_argument('--random_seed', type=int)

	#freestream parameters:
	parser.add_argument('--turn_on', 		type=int)
	parser.add_argument('--tau_freestream', type=float)
	
	#osu-hydro parameters:
	parser.add_argument('--T0', 			 type=float)
	parser.add_argument('--IEin',            type=int)
	parser.add_argument('--InitialURead',    type=int)
	parser.add_argument('--Initialpitensor', type=int)

	parser.add_argument('--DT',  type=float)
	parser.add_argument('--DXY', type=float)
	parser.add_argument('--NLS', type=int)

	parser.add_argument('--Edec', type=float)
	parser.add_argument('--NDT',  type=int)
	parser.add_argument('--NDXY', type=int)

	parser.add_argument('--ViscousEqsType', type=int)

	parser.add_argument('--VisT0',    type=float)
	parser.add_argument('--VisHRG',   type=float)
	parser.add_argument('--VisMin',   type=float)
	parser.add_argument('--VisSlope', type=float)
	parser.add_argument('--VisCrv',   type=float)
	parser.add_argument('--VisBeta',  type=float)

	parser.add_argument('--VisBulkT0',    type=float)
	parser.add_argument('--VisBulkMax',   type=float)
	parser.add_argument('--VisBulkWidth', type=float)
	parser.add_argument('--IRelaxBulk',   type=int)
	parser.add_argument('--BulkTau',      type=float)

	#analysis parameters:
	parser.add_argument('--analysis_files', type=str)
	parser.add_argument('--id_pT_cuts',     type=str)
	parser.add_argument('--id_y_cuts',      type=str)
	parser.add_argument('--vn_pT_cuts',     type=str)
	parser.add_argument('--vn_eta_cuts',    type=str)

	#DREENA-A parameters:
	parser.add_argument('--particles', type=str)
	parser.add_argument('--xB', 	   type=float)
	parser.add_argument('--xGridN',    type=int)
	parser.add_argument('--yGridN',    type=int)
	parser.add_argument('--phiGridN',  type=int)
	parser.add_argument('--TIMESTEP',  type=float)
	parser.add_argument('--TCRIT',     type=float)

	args = parser.parse_args()

	#main parameters:
	if args.centrality is not None: params['main']['centrality'] = args.centrality.split(',')
	if args.trento_event_n is not None: params['main']['trento_event_n'] = args.trento_event_n
	if args.num_of_trento_jobs is not None: params['main']['num_of_trento_jobs'] = args.num_of_trento_jobs
	if args.maxsamples is not None: params['main']['maxsamples'] = args.maxsamples
	if args.num_of_urqmd_jobs is not None: params['main']['num_of_urqmd_jobs'] = args.num_of_urqmd_jobs
	if args.remove_work is not None: params['main']['remove_work'] = args.remove_work
	if args.batch_system is not None: params['main']['batch_system'] = args.batch_system
	if args.recompile is not None: params['main']['recompile'] = args.recompile

	#TRENTO parameters:
	if args.projectile is not None: params['trento']['projectile'] = args.projectile
	if args.target is not None: params['trento']['target'] = args.target
	if args.ecm is not None: params['trento']['ecm'] = args.ecm

	if args.p is not None: params['trento']['p'] = args.p
	if args.k is not None: params['trento']['k'] = args.k
	if args.w is not None: params['trento']['w'] = args.w
	if args.d is not None: params['trento']['d'] = args.d
	if args.norm is not None: params['trento']['norm'] = args.norm

	if args.grid_max is not None: params['trento']['grid_max'] = args.grid_max
	if args.grid_step is not None: params['trento']['grid_step'] = args.grid_step

	if args.random_seed is not None: params['trento']['random_seed'] = args.random_seed

	#freestream parameters:
	if args.turn_on is not None: params['freestream']['turn_on'] = args.turn_on
	if args.tau_freestream is not None: params['freestream']['tau_freestream'] = args.tau_freestream
	
	#osu-hydro parameters:
	if args.T0 is not None: params['hydro']['T0'] = args.T0
	if args.IEin is not None: params['hydro']['IEin'] = args.IEin
	if args.InitialURead is not None: params['hydro']['InitialURead'] = args.InitialURead
	if args.Initialpitensor is not None: params['hydro']['Initialpitensor'] = args.Initialpitensor

	if args.DT is not None: params['hydro']['DT'] = args.DT
	if args.DXY is not None: params['hydro']['DXY'] = args.DXY
	if args.NLS is not None: params['hydro']['NLS'] = args.NLS

	if args.Edec is not None: params['hydro']['Edec'] = args.Edec
	if args.NDT is not None: params['hydro']['NDT'] = args.NDT
	if args.NDXY is not None: params['hydro']['NDXY'] = args.NDXY

	if args.ViscousEqsType is not None: params['hydro']['ViscousEqsType'] = args.ViscousEqsType

	if args.VisT0 is not None: params['hydro']['VisT0'] = args.VisT0
	if args.VisHRG is not None: params['hydro']['VisHRG'] = args.VisHRG
	if args.VisMin is not None: params['hydro']['VisMin'] = args.VisMin
	if args.VisSlope is not None: params['hydro']['VisSlope'] = args.VisSlope
	if args.VisCrv is not None: params['hydro']['VisCrv'] = args.VisCrv
	if args.VisBeta is not None: params['hydro']['VisBeta'] = args.VisBeta

	if args.VisBulkT0 is not None: params['hydro']['VisBulkT0'] = args.VisBulkT0
	if args.VisBulkMax is not None: params['hydro']['VisBulkMax'] = args.VisBulkMax
	if args.VisBulkWidth is not None: params['hydro']['VisBulkWidth'] = args.VisBulkWidth
	if args.IRelaxBulk is not None: params['hydro']['IRelaxBulk'] = args.IRelaxBulk
	if args.BulkTau is not None: params['hydro']['BulkTau'] = args.BulkTau

	#analysis parameters:
	if args.analysis_files is not None: params['analysis']['save_files'] = args.analysis_files.split(',')

	if args.id_y_cuts   is not None: params['analysis']['id_cuts'][0] = [float(x) for x in args.id_y_cuts.split(',')]
	if args.id_pT_cuts  is not None: params['analysis']['id_cuts'][1] = [float(x) for x in args.id_pT_cuts.split(',')]
	if args.vn_eta_cuts is not None: params['analysis']['vn_cuts'][0] = [float(x) for x in args.vn_eta_cuts.split(',')]
	if args.vn_pT_cuts  is not None: params['analysis']['vn_cuts'][1] = [float(x) for x in args.vn_pT_cuts.split(',')]

	#dreena parameters:
	if args.particles is not None: params['dreena']['particles']   = args.particles.split(',')
	if args.xB 		  is not None: params['dreena']['xB'] 		   = args.xB
	if args.xGridN    is not None: params['dreena']['xGridN']      = args.xGridN
	if args.yGridN    is not None: params['dreena']['yGridN']      = args.yGridN
	if args.phiGridN  is not None: params['dreena']['phiGridN']    = args.phiGridN
	if args.TIMESTEP  is not None: params['dreena']['TIMESTEP']    = args.TIMESTEP
	if args.TCRIT     is not None: params['dreena']['TCRIT']       = args.TCRIT
	if args.TCRIT     is not None: params['dreena']['NUM_THREADS'] = args.NUM_THREADS

	#setting parameters that depend on other dictionary values:
	#freestreaming
	if params['freestream']['turn_on'] == 1:
		params['hydro']['T0'] =  params['freestream']['tau_freestream']   #setting hydro termalization time to freestream time
		params['hydro']['IEin'] = 0										  #setting read initial condition parameter as energy						
		params['hydro']['InitialURead'] = 1								  #setting read initial flow and viscous terms parameter to true
	if params['freestream']['turn_on'] == 0:
		params['hydro']['IEin'] = 1										  #setting read initial condition parameter as entropy
		params['hydro']['InitialURead'] = 0 						      #setting read initial flow and viscous terms parameter to false
	#energy loss
	if params['dreena']['NUM_THREADS'] == 0:
		params['dreena']['NUM_THREADS'] = 3*params['dreena']['phiGridN']  #setting thread number for energy loss calculations to number of phi points

	##########################################################################################################
	analysis_save_files = ['dndpt.dat', 'identified.dat', 'qn.dat', 'intflows.dat']

	#checking if files to save parameter is empty, in which case all possible files are saved:
	if not params['analysis']['save_files'] or len(params['analysis']['save_files']) == 0:
		params['analysis']['save_files'] = analysis_save_files

	#checking if provided save_files parameter is list:
	if not isinstance(params['analysis']['save_files'], list):
		params['analysis']['save_files'] = [params['analysis']['save_files']]
	
	#checking if provided files to save parameters are valid:
	for fs in params['analysis']['save_files']:
		if fs not in analysis_save_files:
			print(f'Error: provided analysis file to save, {fs}, not valid. Aborting...')
			return False

	##########################################################################################################
	dreena_particles = ['Bottom', 'Charm', 'LQuarks', 'Gluon']

	#checking if dreena particles parameter is empty, in which case all possible particles are calculated:
	if not params['dreena']['particles'] or len(params['dreena']['particles']) == 0:
		params['dreena']['particles'] = dreena_particles

	#checking if provided dreena particles parameter is list:
	if not isinstance(params['dreena']['particles'], list):
		params['dreena']['particles'] = [params['dreena']['particles']]

	#checking if provided particles parameter is valid:
	for p in params['dreena']['particles']:
		if p not in dreena_particles:
			print(f'Error: provided dreena particles parameter, {p}, not valid. Aborting...')
			return False

	##########################################################################################################

	return True
###################################################################################################################################