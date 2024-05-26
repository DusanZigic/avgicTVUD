#!/usr/bin/env python3

from sys import argv, exit
from os import path
from subprocess import Popen, call
import numpy as np
import json

#########################################################################################################################################
def integrateRAA(pname):
	raadist   = np.loadtxt('{0:s}.dat'.format(pname))
	ptpts	  = np.sort(np.unique(raadist[:,0]))
	phipts	  = np.sort(np.unique(raadist[:,1]))
	raa       = np.zeros(ptpts.shape[0])
	v2        = np.zeros(ptpts.shape[0])
	raadist   = raadist[:,2].reshape(ptpts.shape[0], phipts.shape[0])
	gqweights = np.polynomial.legendre.leggauss(phipts.shape[0])[1]*np.pi
	for ipt in range(ptpts.shape[0]):
		norm     = np.sum(gqweights*raadist[ipt])
		raa[ipt] = norm/2.0/np.pi
		v2[ipt]  = np.sum(gqweights*raadist[ipt]*np.cos(2.0*phipts))/norm
	return np.column_stack((ptpts, raa, v2))
#########################################################################################################################################

#########################################################################################################################################
def exportOBS(pname, obs):
	header = []
	with open('{0:s}.dat'.format(pname), 'r') as f:
		while True:
			line = f.readline().rstrip()
			if line[0] == '#': header.append(line)
			else: break
	p_name = {'bottom': 'b', 'charm': 'd', 'chargedhadrons': 'ch'}
	header[0] = header[0].replace(pname, p_name[pname])
	header[7] = header[7].replace('R_AA', 'v_2')
	header[7] = header[7].replace('phi',  'R_AA')
	with open('{0:s}.dat'.format(p_name[pname]), 'w') as f:
		for h in header: f.write(h + '\n')
		for x in obs: f.write('{0:14.10f}  {1:12.10f}  {2:12.10f}\n'.format(x[0], x[1], x[2]))
#########################################################################################################################################

#########################################################################################################################################
if __name__ == '__main__':

	main_dir = path.abspath('')

	with open('params.json', 'r') as jsonf: params = json.load(jsonf)

	numthreads = [len([*range(params['dreena']['NUM_THREADS'])][i::3]) for i in range(3)]

	commandStr  = 'export OMP_NUM_THREADS={0:d}; '.format(numthreads[2])
	commandStr += './DREENAA AverageEL --c=dreena.conf --pName=Bottom; '
	commandStr += './DREENAA AverageEL --c=dreena.conf --pName=Charm;'
	hf_command  = Popen(commandStr, shell=True, cwd=main_dir)

	commandStr  = 'export OMP_NUM_THREADS={0:d}; ./DREENAA AverageEL --c=dreena.conf --pName=LQuarks;'.format(numthreads[0])
	lq_command  = Popen(commandStr, shell=True, cwd=main_dir)

	commandStr  = 'export OMP_NUM_THREADS={0:d}; ./DREENAA AverageEL --c=dreena.conf --pName=Gluon;'.format(numthreads[1])
	gl_command  = Popen(commandStr, shell=True, cwd=main_dir)

	lq_command.wait()
	gl_command.wait()

	commandStr  = 'export OMP_NUM_THREADS={0:d}; ./DSSFFs --c=dssffs.conf;'.format(params['dreena']['NUM_THREADS'])
	ch_command  = Popen(commandStr, shell=True, cwd=main_dir)

	hf_command.wait()
	ch_command.wait()

	obs = integrateRAA('bottom')
	exportOBS('bottom', obs)

	obs = integrateRAA('charm')
	exportOBS('charm', obs)

	obs = integrateRAA('chargedhadrons')
	exportOBS('chargedhadrons', obs)