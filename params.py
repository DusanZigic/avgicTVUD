params = {
	#############################################################################################################
	#simulation, run and path parameters:
	'main': {
			'centrality': ['10-20%', '10-30%', '20-30%', '20-40%', '30-40%', '30-50%', '40-50%'], #centralities

			'trento_event_n':  250000, #number of trento initial condition events;

			'num_of_trento_jobs': 100, #number of trento jobs to be create

			'maxsamples': 		 1000, #number of separate particle ensembles from the freeze-out surface (so-called “oversampling”)
			
			'num_of_urqmd_jobs':  100, #number of urqmd jobs to be run in parallel

			'remove_work': 		    1, #remove work directory: 0 - do not remove, 1 - remove

			'batch_system':   'slurm', #batch system: local or slurm

			'recompile':            0, #option to recompile executables: 0 - do not recompile, 1 - recompile
									   #could be used when trento, hydro, urqmd, dreena or dss codes are modified
	},

	#############################################################################################################
	#trento parameters:
	'trento': {
			'projectile':  'Pb',			    #projectile and target options: p, d, Cu, Cu2, Xe, Xe2, Au, Au2, Pb, U, U2, U3
			'target':	   'Pb',			    #for more details see: http://qcd.phy.duke.edu/trento/
			'ecm':		    5020,			    #collision energy in GeV; trento parameter is nucleon-nucleon cross section,
											    #which is correlated to ecm (see http://qcd.phy.duke.edu/trento/)
			'p':		   0.0,				    #reduced thickness parameter p
			'k':		   1.19,			    #gamma distribution shape parameter for nucleon fluctuations
			'w':		   0.500,			    #Gaussian nucleon width in fm
			'd':		   0.500,			    #minimum nucleon-nucleon distance (fm) for Woods-Saxon nuclei (spherical and deformed)
			'norm': 	   85.00,			    #overall normalization factor

			'grid_max':	   20.05,   		    #x and y maximum of the grid in fm
			'grid_step':   0.1,	   			    #size of grid cell in fm
								   			    #TRENTO grid must be the same as the hydro grid
			'random_seed': 0,	   			    #random seed for TRENTO event generator; if set to positive integer each TRENTO run
								   			    #will produce same events
			'x_hist':      [-15.0, 15.0, 0.25], #bcdensity histogram ranges and bin width for x axes
			'y_hist':      [-15.0, 15.0, 0.25], #bcdensity histogram ranges and bin width for y axes
	},

	#############################################################################################################
	#freestram parameters:
	'freestream': {
			'turn_on': 			 0, #turn freestream on or off: 1 - on, 0 - off
			'tau_freestream': 1.16, #freestreaming time in fm
									#if freestream is turned on, hydro T0 parameter is automaticaly updated to
									#tau_freestream value - there is no need to manually change T0 below
	},

	#############################################################################################################
	#osu-hydro parameters:
	'hydro': {
			'T0':              1.0,      		 #initial time [fm]
			'IEin':            1,        		 #read initial condition as energy (0) or entropy (1) density
			'InitialURead':    0,        		 #read initial flow and viscous terms if not 0
			'Initialpitensor': 0,        		 #initialize shear tensor with zeros (0) or by Navier-Stokes (1)

			'DT':              0.025,    		 #timestep [fm]
			'DXY':             0.10,     		 #spatial step [fm]
			'NLS':             200,      		 #lattice size from origin (total size = 2*LS + 1)

			'Edec':            0.265,    		 #decoupling energy density [GeV/fm^3]
			'NDT':             1,        		 #freeze-out step in tau direction
			'NDXY':            1,        		 #freeze-out step in x, y directions

			'ViscousEqsType':  2,        		 #old Israel-Stewart (1) or updated 14-moment expansion (2)

			'VisT0':           0.154,    		 #temperature of minimum eta/s [GeV]
			'VisHRG':          0.15,     		 #constant eta/s below T0
			'VisMin':          0.15,     		 #eta/s at T0
			'VisSlope':        0.00,      		 #slope of (eta/s)(T) above T0 [GeV^-1]
			'VisCrv':          0.00,      		 #curvature of (eta/s)(T) above T0 (see readme)
			'VisBeta':         0.833333, 		 #shear relaxation time tau_pi = 6*VisBeta*eta/(sT)

			'VisBulkT0':       0.183,    		 #peak location of Cauchy (zeta/s)(T) [GeV]
			'VisBulkMax':      0.001,    		 #maximum value of zeta/s (at T0)
			'VisBulkWidth':    0.001,    		 #width of (zeta/s)(T) [GeV]
			'IRelaxBulk':      4,        		 #bulk relaxation time: critical slowing down (0), constant (1), 1.5/(2*pi*T) (2), ?? (3), 14-moment result (4)
			'BulkTau':         5.0,      		 #constant bulk relaxation time for IRelaxBulk == 1

	},

	#############################################################################################################
	#analysis parameters:
	'analysis': {
			'save_files': '', 						#chose which files to save;
							  						#options: dndpt.dat - pT spectrum of charged hadrons at mid(pseudo)rapidity |eta|<0.5
							  						#		  identified.dat - multiplicities and mean transverse momenta of pions, kaons and protons at midrapidity |y| < 0.5
							  						#		  qn.dat - flow vectors of charged particles at midrapidity |eta|<0.8 and 0.2 < pT < 5.0 GeV for harmonics n=1 to 8
							  						#		  intflows.dat - integrated flows calculated from qn
							  						#if left empty, all files will be saved
			
			'id_cuts': [[-0.5, 0.5], [0.0, 'inf']], #y and pT cuts for identified multiplicities and mean pT
												    #standard values:  ALICE: |y|<0.5, 0.0<pT<inf, 1910.07678
												   	#				  PHENIX: |y|<0.5, 0.0<pT<inf, nucl-ex/0307022
			'vn_cuts': [[-0.8, 0.8], [0.2, 5.0]],   #eta and pT cuts for integrated v_n
													#standard values: ALICE: |eta|<0.8, 0.20<pT<5.0, 1602.01119
													#				   STAR: |eta|<1.3, 0.15<pT<2.0, nucl-ex/0409033
	},

	#############################################################################################################
	#dreena parameters:
	'dreena': {
			'particles':      '', #chose which particles to calculate;
							      #options: ch (charged hadrons), d (d meson), b (b meson); if left empty, all particles will be calculated
			'xB':		     0.6, #chromo-magnetic to chromo-electric mass ratio
			'xGridN':         50, #number of x points in x-y plane
			'yGridN':	      50, #number of y points in x-y plane
			'phiGridN':	      25, #number of phi angles
			'TIMESTEP':      0.1, #jet's timestep
			'TCRIT':	   0.155, #critical temperature - below TCRIT jet's energy loss stops
			'NUM_THREADS':   100, #number of threads; if set to 0, it's value is set to 3*phiGridN since that loop is parallelized
								  #and there are 3 energy loss calculations running in parallel: heavy flavour, light quarks and gluons
	}
}
