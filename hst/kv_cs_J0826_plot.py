#This is a program to plot the effective radius of different models for the J0826 galaxy

import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

#sersic values:
#These values are from independant trials for each filter
s_F475W_indep_s = 0.240
s_F814W_indep_s = 0.372

#These values are from galfitm where x and y values are allowed to be different between filters
s_F475W_simul_s = 1.191 
s_F814W_simul_s = 1.191

#These values are from galfitm where x and y positions must remain constant
s_F475W_simul2_s = 1.193
s_F814W_simul2_s = 1.193

s_diff_s = [(s_F475W_indep_s - s_F814W_indep_s), (s_F475W_simul_s - s_F814W_simul_s), (s_F475W_simul2_s - s_F814W_simul2_s)]
F814W_s = [s_F814W_indep_s, s_F814W_simul_s, s_F814W_simul2_s]

#psf values:
#These values are from independant trials for each filter
#m_F475W_indep_p = 19.349
#m_F814W_indep_p = 19.188

#These values are from galfitm where x and y values are allowed to be different between filters
#m_F475W_simul_p = 19.656 
#m_F814W_simul_p = 19.165

#These values are from galfitm where x and y positions must remain constant
#m_F475W_simul2_p = 19.640
#m_F814W_simul2_p = 19.215

#m_diff_p = [(m_F475W_indep_p - m_F814W_indep_p), (m_F475W_simul_p - m_F814W_simul_p), (m_F475W_simul2_p - m_F814W_simul2_p)]
#F814W_p = [m_F814W_indep_p, m_F814W_simul_p, m_F814W_simul2_p]

with PdfPages('kv_cs_J0826_plot.pdf') as pdf:
    fig = plt.figure()
    plt.suptitle('J0826 Difference in Effective Radius Between Filters')
    ax = fig.add_subplot(2,1,1)
    plt.xlabel('Effective Radius of F814W')
    plt.ylabel('s_F475W - s_F814W')
##    plt.scatter(F814W_s, m_diff_s, label = 'sersic')
##    plt.scatter(F814W_p, m_diff_p, label = 'psf')
##    plt.legend(loc=3)
    labels = ['sersic independent (r_e, x, y, magnitude allowed to vary)', 'sersic simultaneous (x, y, magnitude allowed to vary)', 'sersic semi-simultaneous (magnitude allowed to vary)']
    colors = ['lightcoral', 'firebrick', 'darkorange']
    marker = ['o', 's', 'D']
    for i in range(0,3):
        if i < 3:
            plt.scatter(F814W_s[i], s_diff_s[i], s = 60, label = labels[i], color = colors[i], marker = marker[i])
        #if i >= 3:
            #plt.scatter(F814W_p[i-3],m_diff_p[i-3], label = labels[i], color = colors[i])
    plt.legend(loc=9, bbox_to_anchor=(0.5, -0.25))


    pdf.savefig(dpi=1000)
    plt.close()

os.system('open %s &' % 'kv_cs_J0826_plot.pdf')

#on plot, values go from left to right as follows: indep, simul, simul2
