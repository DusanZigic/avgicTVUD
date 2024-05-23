import sys
import math
import cmath

"""
Calculate 2- and 4-particle cumulant reference flow

Based on
A.~Bilandzic, R.~Snellings and S.~Voloshin,
``Flow analysis with cumulants: Direct calculations,''
Phys. Rev. C 83, 044913 (2011)
doi:10.1103/PhysRevC.83.044913
[arXiv:1010.0233 [nucl-ex]].
"""

Q = {}
for n in range(1, 9):
    Q[n] = None

two_corr_norm = 0.0
two_corr_sum_n2 = 0.0
two_corr_sum_n3 = 0.0

two_corr_single_event_n2 = []
two_corr_single_event_n3 = []
Wtwo_single_event = []

four_corr_norm = 0.0
four_corr_sum_n2 = 0.0
four_corr_sum_n3 = 0.0

four_corr_single_event_n2 = []
four_corr_single_event_n3 = []
Wfour_single_event = []

Nevents = 0
for arg in sys.argv[1:]:
    M = 0
    for n in range(1, 9):
        Q[n] = None
    with open(arg, "r") as qnfile:
        Nevents += 1
        for line in qnfile:
            data = line.split()
            if len(data) == 1:
                try:
                    M = int(data[0])
                except ValueError:
                    continue
            elif len(data) == 3:
                try:
                    n = int(data[0])
                    qn_real = float(data[1])
                    qn_imag = float(data[2])
                    Q[n] = complex(qn_real, qn_imag)
                except ValueError:
                    continue


    # compute 2-particle and 4-particle correlations
    Q_2_2 = Q[2].real**2 + Q[2].imag**2
    Q_3_2 = Q[3].real**2 + Q[3].imag**2
    Wtwo = M * (M - 1)
    two_corr_ev_n2 = (Q_2_2 - M) / Wtwo
    two_corr_ev_n3 = (Q_3_2 - M) / Wtwo
    two_corr_norm += Wtwo
    two_corr_sum_n2 += two_corr_ev_n2 * Wtwo
    two_corr_sum_n3 += two_corr_ev_n3 * Wtwo
    two_corr_single_event_n2.append(two_corr_ev_n2)
    two_corr_single_event_n3.append(two_corr_ev_n3)
    Wtwo_single_event.append(Wtwo)

    Q_2_4 = Q_2_2 * Q_2_2
    Q_3_4 = Q_3_2 * Q_3_2
    Q_4_2 = Q[4].real**2 + Q[4].imag**2
    Q_6_2 = Q[6].real**2 + Q[6].imag**2
    Re_Q4_cQ2_cQ2 = (Q[4] * Q[2].conjugate() * Q[2].conjugate()).real
    Re_Q6_cQ3_cQ3 = (Q[6] * Q[3].conjugate() * Q[3].conjugate()).real
    Wfour = M * (M - 1) * (M - 2) * (M - 3)
    four_corr_ev_n2 = (Q_2_4 + Q_4_2 - 2 * Re_Q4_cQ2_cQ2 - 2 * (2 * (M - 2) * Q_2_2 - M * (M - 3))) / Wfour
    four_corr_ev_n3 = (Q_3_4 + Q_6_2 - 2 * Re_Q6_cQ3_cQ3 - 2 * (2 * (M - 2) * Q_3_2 - M * (M - 3))) / Wfour
    four_corr_norm += Wfour
    four_corr_sum_n2 += four_corr_ev_n2 * Wfour
    four_corr_sum_n3 += four_corr_ev_n3 * Wfour
    four_corr_single_event_n2.append(four_corr_ev_n2)
    four_corr_single_event_n3.append(four_corr_ev_n3)
    Wfour_single_event.append(Wfour)

    cQ_2 = Q[2].conjugate()
    cQ_3 = Q[3].conjugate()
    cQ_4 = Q[4].conjugate()
    cQ_6 = Q[6].conjugate()

# calculate the averages
two_corr_avr_n2 = two_corr_sum_n2 / two_corr_norm
four_corr_avr_n2 = four_corr_sum_n2 / four_corr_norm
two_corr_avr_n3 = two_corr_sum_n3 / two_corr_norm
four_corr_avr_n3 = four_corr_sum_n3 / four_corr_norm

# Standard error of the weighted mean (bootstrap-verified result)
# Gatz & Smith, Atmospheric Environment Volume 29, Issue 11, June 1995, Pages 1185-1193
# First, compute weighted standard deviations of the averages
wvar_twocorr_n2 = 0.0
wvar_twocorr_n3 = 0.0
for i in range(Nevents):
    wvar_twocorr_n2 += (Wtwo_single_event[i]**2 * (two_corr_single_event_n2[i] - two_corr_avr_n2)**2)
    wvar_twocorr_n3 += (Wtwo_single_event[i]**2 *  (two_corr_single_event_n3[i] - two_corr_avr_n3)**2)

wvar_fourcorr_n2 = 0.0
wvar_fourcorr_n3 = 0.0
for i in range(Nevents):
    wvar_fourcorr_n2 += (Wfour_single_event[i]**2 * (four_corr_single_event_n2[i] - four_corr_avr_n2)**2)
    wvar_fourcorr_n3 += (Wfour_single_event[i]**2 * (four_corr_single_event_n3[i] - four_corr_avr_n3)**2)

err_twocorr_n2 = 0.0
err_twocorr_n3 = 0.0
err_fourcorr_n2 = 0.0
err_fourcorr_n3 = 0.0
# the standard error of the weighted mean
if (Nevents > 1):
    err_twocorr_n2 = math.sqrt(Nevents * wvar_twocorr_n2 / ((Nevents - 1) * two_corr_norm**2))
    err_twocorr_n3 = math.sqrt(Nevents * wvar_twocorr_n3 / ((Nevents - 1) * two_corr_norm**2))
    err_fourcorr_n2 = math.sqrt(Nevents * wvar_fourcorr_n2 / ((Nevents - 1) * four_corr_norm**2))
    err_fourcorr_n3 = math.sqrt(Nevents * wvar_fourcorr_n3 / ((Nevents - 1) * four_corr_norm**2))

# The cumulants based on average correlations
c22 = two_corr_avr_n2
c24 = four_corr_avr_n2 - 2 * two_corr_avr_n2**2

c32 = two_corr_avr_n3
c34 = four_corr_avr_n3 - 2 * two_corr_avr_n3**2

# Error propagation ignoring covariance
c24err = math.sqrt(16 * two_corr_avr_n2**2 * err_twocorr_n2**2 + err_fourcorr_n2**2)
c34err = math.sqrt(16 * two_corr_avr_n3**2 * err_twocorr_n3**2 + err_fourcorr_n3**2)

# Finally, the harmonics
try:
    v22 = math.sqrt(c22)
    # Propagated standard deviation
    v22err = err_twocorr_n2 / (2 * v22)
except ValueError:
    v22 = -1.0
    v22err = -1.0 

try:
    v24 = (-c24)**0.25
    v24err = c24err / (4 * abs(c24)) * v24
except ValueError:
    v24 = -1.0
    v24err = -1.0

try:
    v32 = math.sqrt(c32)
    v32err = err_twocorr_n3 / (2 * v32)
except ValueError:
    v32 = -1.0
    v32err = -1.0

try:
    v34 = (-c34)**0.25
    v34err = c34err / (4 * abs(c34)) * v34
except ValueError:
    v34 = -1.0
    v34err = -1.0

print("Integrated flow:")
print("v2{{2}} {:.4f} {:.4f}".format(v22, v22err))
print("v2{{4}} {:.4f} {:.4f}".format(v24, v24err))
print("v3{{2}} {:.4f} {:.4f}".format(v32, v32err))
print("v3{{4}} {:.4f} {:.4f}".format(v34, v34err))
