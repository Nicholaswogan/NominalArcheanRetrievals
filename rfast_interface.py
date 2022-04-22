import numpy as np
import subprocess as sub
import os
import time

THIS_FILE_DIR = os.path.dirname(os.path.realpath(__file__))+'/'
# constants
LAM_MAX = 1.0 # end of bandpass
TEMPLATE_FOLDER = THIS_FILE_DIR+"NA_rfast/"
TEMPLATE_INPUTS = TEMPLATE_FOLDER+"NA_inputs_template.scr"
TEMPLATE_RPARS = TEMPLATE_FOLDER+"NA_rpars.txt"
RFAST_ROOT = THIS_FILE_DIR+"rfast"

LAMS_PREFIX = "0.5,0.6,"
LAML_PREFIX = "0.6,"
RES_PREFIX = "0,0,"
SNR0_PREFIX = "7,0.01,"
REFRESH_TIME = 5 # seconds
TIMEOUT = 60*60*24*3 # 3 days

def bandpass_extents(B, lam_c):
    Dlam = B*lam_c/(1+B*0.5)
    lam_min = lam_c - 0.5*Dlam
    lam_max = lam_c + 0.5*Dlam
    return lam_min, lam_max, Dlam
    
def bandpass_extents_end(B, lam_1):
    lam_0 = lam_1/(1+B)
    return  lam_0

def make_filenames(root_outdir, prefix, B, res, snr):
    fns_name = \
    prefix+"_"+('B=%.4f'%B)+"_"+('res=%.4f'%res)+"_"+('snr=%.4f'%snr)
    fnn_name = fns_name+'_n'
    fnr_name = fns_name+'_r'
    
    out = {}
    out['output_folder'] = root_outdir+'/'+fns_name
    # set the filenames
    out['fns'] = out['output_folder']+'/'+fns_name
    out['fnn'] = out['output_folder']+'/'+fnn_name
    out['fnr'] = out['output_folder']+'/'+fnr_name
    
    out['rfast_inputs'] = out['output_folder']+'/'+fns_name+'_inputs.scr'
    out['rfast_rpars'] = out['output_folder']+'/'+fns_name+'_rpars.txt'
    return out

def add_extensions_to_files(fns, fnn, fnr):
    fns_raw = fns + '.raw'
    fnn_dat = fnn + '.dat'
    fnr_h5 = fnr + '.h5'
    return fns_raw, fnn_dat, fnr_h5

def make_dirs_and_files(B, res, snr, root_outdir, prefix):
    # variables to set
    # fns
    # fnn
    # fnr
    # lams
    # laml
    # res
    # snr0

    # read template inputs file
    with open(TEMPLATE_INPUTS,'r') as f:
        lines = f.readlines()

    out_files = make_filenames(root_outdir, prefix, B, res, snr)
    lam_min = bandpass_extents_end(B, LAM_MAX)
    lam_max = LAM_MAX

    new_lines = []
    for line in lines:
        tmp = line
        v = line.strip().split()[0]
        if v == 'fns':
            tmp = "fns       = "+out_files['fns']+'\n'
        if v == 'fnn':
            tmp = "fnn       = "+out_files['fnn']+'\n'
        if v == 'fnr':
            tmp = "fnr       = "+out_files['fnr']+'\n'
        if v == 'lams':
            tmp = "lams      = "+LAMS_PREFIX+"%.4f"%lam_min+'\n'
        if v == 'laml':
            tmp = "laml      = "+LAML_PREFIX+"%.4f"%lam_min+",""%.4f"%lam_max+'\n'
        if v == 'res':
            tmp = "res       = "+RES_PREFIX+"%i"%res+'\n'
        if v == 'snr0':
            tmp = "snr0      = "+SNR0_PREFIX+"%i"%snr+'\n'
        new_lines.append(tmp)

    # make the directories and files
    if not os.path.isdir(root_outdir):
        raise Exception('"'+root_outdir+'" does not exist.')

    # if output directory does not exist
    # then we create it
    if os.path.isdir(out_files['output_folder']):
        raise Exception('"'+out_files['output_folder']+'" already exists!')
    else:
        os.mkdir(out_files['output_folder'])

    # write the input file
    with open(out_files['rfast_inputs'],'w') as f:
        for line in new_lines:
            f.write(line)

    # write the rpars file
    with open(TEMPLATE_RPARS,'r') as f:
        lines = f.readlines()
    with open(out_files['rfast_rpars'],'w') as f:
        for line in lines:
            f.write(line)
            
    return out_files

def monitor_processes(all_process):
    start = time.time()
    total = len(all_process)
    while True:
        number_completed = 0
        for process in all_process:
            res = process.poll()
            if res != None:
                number_completed += 1

        fmt = "{:50}"

        print(fmt.format("completed/total = "+str(number_completed)+'/'+str(total)),end='\r')
        if number_completed == total:
            break
        else:
            time.sleep(REFRESH_TIME)
            
        finish = time.time()
        runtime = finish-start
        # we time out after a bit.
        if runtime > TIMEOUT:
            print("TIMEOUT reached. Killing all processes.")
            for process in all_process:
                process.kill()
            
def spawn_retrieval(files):
    # run genspec
    cmd = "python rfast_genspec.py "+files['rfast_inputs']
    res = sub.run(cmd.split(),check=True,cwd=RFAST_ROOT)

    # run noise
    cmd = "python rfast_noise.py "+files['rfast_inputs']
    res = sub.run(cmd.split(),check=True,cwd=RFAST_ROOT)

    # initialize retreival
    cmd = "python rfast_initret.py "+files['rfast_inputs']+' '+files['rfast_rpars']
    res = sub.run(cmd.split(),check=True,cwd=RFAST_ROOT)
    
    cmd = "python rfast_retrieve.py "+files['rfast_inputs']
    process = sub.Popen(cmd.split(),cwd=RFAST_ROOT)
    # just wait for 1 second!
    time.sleep(1)
    
    return process

def spawn_rfast_retreivals(B, res, snr, root_outdir, prefix):
    all_process = []
    for i in range(len(B)):
        files = make_dirs_and_files(B[i], res[i], snr[i], root_outdir, prefix)
        process = spawn_retrieval(files)
        all_process.append(process) 
    monitor_processes(all_process)

def make_input_lists(B_1, res_1, snr_1):
    B = []
    res = []
    snr = []
    for b in B_1:
        for r in res_1:
            for s in snr_1:
                B.append(b)
                res.append(r)
                snr.append(s)
    return B,res,snr

if __name__ == "__main__":
    # must be absolute directory
    root_outdir = ""
    prefix = "MA"
    B_1 = [0.15, 0.2, 0.25]
    res_1 = [70, 140]
    snr_1 = [5, 10, 15, 20] 
    B,res,snr = make_input_lists(B_1, res_1, snr_1)
    spawn_rfast_retreivals(B, res, snr, root_outdir, prefix)
