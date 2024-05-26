#!/usr/bin/env python3

from os import path
from re import findall
import numpy as np

if __name__ == '__main__':

	main_dir      = path.abspath('')
	job_id		  = int(findall("\d+", path.split(main_dir)[-1])[0])	
	trento_events = np.empty((0, 6), float)
	bcp 	      = np.empty((0, 2), float)
	
	with open(path.join(main_dir, "trento_events.dat"), 'r') as f:
		for file_line in f:
			line = file_line.rstrip()
			if line[0] == '#':
				data = [float(x) for x in line.replace('#', '').split()]
				data = data[:5]
				data.insert(0, job_id)
				event_id = int(data[1])
				trento_events = np.append(trento_events, np.array([data]), axis=0)
				np.savetxt(path.join(main_dir, 'eventstemp', f"bcp{event_id:d}.dat"), bcp, fmt='%5f')
				bcp = np.empty((0, 2), float)
			else:
				data = [float(x) for x in line.split()]
				bcp = np.append(bcp, np.array([data]), axis=0)
	
	permutation = [0, 1, 5, 2, 3, 4]
	idx = np.empty_like(permutation)
	idx[permutation] = np.arange(len(permutation))
	trento_events[:] = trento_events[:, idx]
	np.savetxt(path.join(main_dir, "trento_events.dat"), trento_events, fmt="%4d %6d %3d %3d %.5f %.5f", header="job_id event_id npart ncoll TATB b")