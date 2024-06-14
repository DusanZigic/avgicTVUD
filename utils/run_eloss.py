#!/usr/bin/env python3

from os import path
from subprocess import Popen, call
import numpy as np
import json

def integrateRAA(pname):
# function that integrates R_AA(pT, phi) over phi
	raadist   = np.loadtxt(f"{pname:s}.dat")
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

def exportOBS(pname, obs):
# function that exports observables: R_AA(pT) and v_2(pT)
	header = []
	with open(f"{pname:s}.dat", 'r') as f:
		while True:
			line = f.readline().rstrip()
			if line[0] == '#': header.append(line)
			else: break
	p_name = {"bottom": "b", "charm": "d", "chargedhadrons": "ch"}
	header[0] = header[0].replace(pname, p_name[pname])
	header[7] = header[7].replace("R_AA", "v_2")
	header[7] = header[7].replace("phi",  "R_AA")
	with open(f"{p_name[pname]}.dat", 'w') as f:
		for h in header:
			f.write(f"{h}\n")
		for x in obs:
			f.write(f"{x[0]:14.10f}  {x[1]:12.10f}  {x[2]:12.10f}\n")

if __name__ == '__main__':

	main_dir = path.abspath("")

	with open("params.json", 'r') as jsonf: params = json.load(jsonf)

	numthreads = [len([*range(params['dreena']['NUM_THREADS'])][i::3]) for i in range(3)]

	commandStr  = f"export OMP_NUM_THREADS={numthreads[2]:d}; "
	if "b" in params['dreena']['particles']:
		commandStr += "./DREENAA AverageEL --config=dreena.conf --pName=Bottom; "
	if "d" in params['dreena']['particles']:
		commandStr += "./DREENAA AverageEL --config=dreena.conf --pName=Charm;"
	heavyFlavourCommand  = Popen(commandStr, shell=True, cwd=main_dir)

	commandStr = f"export OMP_NUM_THREADS={numthreads[0]:d}; "
	if "ch" in params['dreena']['particles']:
		commandStr += "./DREENAA AverageEL --config=dreena.conf --pName=LQuarks;"
	lightQuarksCommand  = Popen(commandStr, shell=True, cwd=main_dir)
	
	commandStr = f"export OMP_NUM_THREADS={numthreads[1]:d}; "
	if "ch" in params['dreena']['particles']:
		commandStr += "./DREENAA AverageEL --config=dreena.conf --pName=Gluon;"
	gluonCommand  = Popen(commandStr, shell=True, cwd=main_dir)

	lightQuarksCommand.wait()
	gluonCommand.wait()
	heavyFlavourCommand.wait()

	if "ch" in params['dreena']['particles'] and path.exists(path.abspath("dssffs.conf")):
		commandStr  = f"export OMP_NUM_THREADS={params['dreena']['NUM_THREADS']:d}; "
		commandStr += "./DSSFFs --config=dssffs.conf;"
		call(commandStr, shell=True, cwd=main_dir)

	if "b" in params['dreena']['particles']:
		obs = integrateRAA("bottom")
		exportOBS("bottom", obs)

	if "d" in params['dreena']['particles']:
		obs = integrateRAA("charm")
		exportOBS("charm", obs)

	if "ch" in params['dreena']['particles'] and path.exists(path.abspath("dssffs.conf")):
		obs = integrateRAA("chargedhadrons")
		exportOBS("chargedhadrons", obs)


