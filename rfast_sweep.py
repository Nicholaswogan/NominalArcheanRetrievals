import numpy as np
import subprocess as sub
import os
import time

from rfast_interface import RfastInterface

    
if __name__ == "__main__":
    # must be absolute directory
    r = RfastInterface(template_inputs='NA_rfast/NA_inputs_template.scr', \
                       template_rpars='NA_rfast/NA_rpars.txt')
    
    root_outdir = ""

    res_1 = [70,140]
    snr_1 = [5,10,15,20] 
    res = []
    snr = []
    for rr in res_1:
        for s in snr_1:
            res.append(rr)
            snr.append(s)
            
    # 20% bandpass
    lams = list(np.ones(len(res))*0.75)
    laml = list(np.ones(len(res))*0.90)

    for i in range(len(lams)):
        # output directory
        outdir = root_outdir+ \
        ('lams=%.4f'%lams[i])+"_"+('laml=%.4f'%laml[i])+"_"+('res=%.4f'%res[i])+"_"+('snr=%.4f'%snr[i])
        wavl = [lams[i], laml[i]]
        res_l = [res[i]]
        modes_l = [1]
        snr0_l = [snr[i]]
        r.set_wavelength_grid(wavl, res_l, modes_l, snr0_l)
        r.spawn_retieval(outdir)
        
    r.monitor_retrievals()
    