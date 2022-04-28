import numpy as np
import subprocess as sub
import os
import time

from rfast_interface import RfastInterface

    
if __name__ == "__main__":
    # must be absolute directory
    r = RfastInterface(template_inputs='NA_rfast/NA_inputs_template.scr', \
                       template_rpars='NA_rfast/NA_rpars.txt')
    
    root_outdir = "/Users/nicholas/Documents/Research_local/NASA/NominalArchean/test_dir/"
    lam0 = 0.75
    B_1 = [.20,.30]
    res_1 = [70, 140]
    snr_1 = [5,10,15,20] 
    
    B = []
    lams = []
    laml = []
    res = []
    snr = []
    for b in B_1:
        for rr in res_1:
            for s in snr_1:
                B.append(b)
                lams.append(lam0)
                laml.append(lam0+lam0*b)
                res.append(rr)
                snr.append(s)
            
    for i in range(len(B)):
        # output directory
        outdir = root_outdir+ \
        ('B=%.4f'%B[i])+"_"+('res=%.4f'%res[i])+"_"+('snr=%.4f'%snr[i])
        wavl = [lams[i], laml[i]]
        res_l = [res[i]]
        modes_l = [1]
        snr0_l = [snr[i]]
        r.set_wavelength_grid(wavl, res_l, modes_l, snr0_l)
        r.spawn_retieval(outdir)
        
    r.monitor_retrievals()
    