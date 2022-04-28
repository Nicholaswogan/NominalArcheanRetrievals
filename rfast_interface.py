import numpy as np
import subprocess as sub
import os
import time

THIS_FILE_DIR = os.path.dirname(os.path.realpath(__file__))+'/'
RFAST_ROOT = THIS_FILE_DIR+"rfast"

REFRESH_TIME = 4

def read_raw(file):
    f = open(file,'r')
    lines = f.readlines()
    f.close()

    out = {}
    keys = ['wv','dwv','albedo','flux_ratio']
    nw = len(lines)-1
    for key in keys:
        out[key] = np.empty(nw)

    for i,line in enumerate(lines[1:]):
        tmp = line.strip().split('|')[1:-1]
        tmp = [a.strip() for a in tmp]

        for j,key in enumerate(keys):
            out[key][i] = float(tmp[j])
    return out

class RfastInterface():

    def __init__(self, \
                 template_inputs = RFAST_ROOT+"/rfast_inputs.scr", \
                 template_rpars = RFAST_ROOT+"/rfast_rpars.txt", \
                 inputs_name = "rfast_inputs.scr", \
                 rpars_name = "rfast_rpars.txt"):
        
        # path to the template files
        self.template_inputs_n = template_inputs
        self.template_rpars_n = template_rpars
        
        # name of the files we will output
        self.inputs_name = inputs_name
        self.rpars_name = rpars_name
        
        # The lines of the template files
        with open(self.template_inputs_n,'r') as f:    
            self.inputs_f = f.readlines()
        with open(self.template_rpars_n,'r') as f:    
            self.rpars_f = f.readlines()
        
        # Copy lines to _new. The lines we will modify
        self.inputs_new = self.inputs_f
        self.rpars_new = self.rpars_f
        
        # retrieval processes
        self.processes = []
        
    def genspec(self):
        self.set_output_files('tmp', 'tmp_n', 'tmp_r')
        
        # write the input file
        rfast_inputs_f = RFAST_ROOT+'/'+"tmp_inputs.scr"
        with open(rfast_inputs_f, 'w') as f:
            for line in self.inputs_new:
                f.write(line)
        
        cmd = "python rfast_genspec.py "+rfast_inputs_f
        res = sub.run(cmd.split(),check=True,cwd=RFAST_ROOT)
        
        # read the raw file
        out = read_raw(RFAST_ROOT+"/tmp.raw")
        
        # delete tmp files
        os.remove(rfast_inputs_f)
        os.remove(RFAST_ROOT+"/tmp.raw")
        os.remove(RFAST_ROOT+"/tmp.png")
        os.remove(RFAST_ROOT+"/tmp.log")
        
        return out
        
    def reset_files(self):
        self.inputs_new = self.inputs_f
        self.rpars_new = self.rpars_f
        
    def set_output_files(self, fns, fnn, fnr):
        
        new_lines = []
        i = 0
        for line in self.inputs_new:
            tmp = line
            v = line.strip().split()[0]
            if v == 'fns':
                tmp = "fns       = "+fns+'\n'
                i+=1
            if v == 'fnn':
                tmp = "fnn       = "+fnn+'\n'
                i+=1
            if v == 'fnr':
                tmp = "fnr       = "+fnr+'\n'
                i+=1
            new_lines.append(tmp)
            
        if i != 3:
            raise Exception("Issue setting output file")
        
        self.inputs_new = new_lines
        
    def set_line_cia_species(self, species, cia):
        options = ['CH4','CO2','H2O','O2','O3','N2O','CO']
        options_cia = ['CO2','H2','N2','O2']
        for s in species:
            if s not in options:
                raise Exception('"'+s+'" is not an optional line species')
        for s in cia:
            if s not in options_cia:
                raise Exception('"'+s+'" is not an optional cia species')
        
        species_l = ""
        for i in range(len(species)):
            species_l += species[i].lower()
            if i < len(species)-1:
                species_l += ","
        species_c = ""
        for i in range(len(cia)):
            species_c += cia[i].lower()
            if i < len(cia)-1:
                species_c += ","
            
            
        new_lines = []
        i = 0
        for line in self.inputs_new:
            tmp = line
            v = line.strip().split()[0]
            if v == 'species_l':
                tmp = "species_l = "+species_l+'\n'
                i += 1
            if v == 'species_c':
                tmp = "species_c = "+species_c+'\n'
                i += 1
            new_lines.append(tmp)
            
        if i != 2:
            raise Exception("Issue setting line or cia species")
            
        self.inputs_new = new_lines
        
        
    def set_wavelength_grid(self, wavl, res_l, modes_l, snr0_l):
        
        if type(wavl) != type([]):
            raise Exception("wavl must be a list")
            
        # make lams and laml
        lams = ""
        laml = ""
        res = ""
        modes = ""
        snr0 = ""
        for i in range(len(wavl)-1):
            lams += '%f'%wavl[i]
            laml += '%f'%wavl[i+1]
            
            res += '%i'%res_l[i]
            modes += '%i'%modes_l[i]
            snr0 += '%i'%snr0_l[i]
            
            if i < len(wavl)-2:
                lams += ","
                laml += ","
                res += ","
                modes += ","
                snr0 += ","
                
        new_lines = []
        i = 0
        for line in self.inputs_new:
            tmp = line
            v = line.strip().split()[0]
            if v == 'lams':
                tmp = "lams      = "+lams+'\n'
                i += 1
            if v == 'laml':
                tmp = "laml      = "+laml+'\n'
                i += 1
            if v == 'res':
                tmp = "res       = "+res+'\n'
                i += 1
            if v == 'modes':
                tmp = "modes     = "+modes+'\n'
                i += 1
            if v == 'snr0':
                tmp = "snr0      = "+snr0+'\n'
                i += 1
            new_lines.append(tmp)
            
        if i != 5:
            raise Exception("Issue setting wavlength grid")
            
        self.inputs_new = new_lines
        
    def spawn_retieval(self, outdir, fns='tmp', fnn='tmp_n', fnr='tmp_r'):
        
        # make the output directory
        if not os.path.isabs(outdir):
            raise Exception('"'+outdir+'" must be an absolute directory.')
        
        if os.path.isdir(outdir):
            raise Exception('"'+outdir+'" already exists!')
        else:
            os.mkdir(outdir)
            
        # set output file
        self.set_output_files(outdir+'/'+fns, outdir+'/'+fnn, outdir+'/'+fnr)
            
        # write the input file
        rfast_inputs_f = outdir+'/'+self.inputs_name
        with open(rfast_inputs_f, 'w') as f:
            for line in self.inputs_new:
                f.write(line)

        # write the rpars file
        rfast_rpars_f = outdir+'/'+self.rpars_name
        with open(rfast_rpars_f, 'w') as f:
            for line in self.rpars_new:
                f.write(line)
                
        # run scripts
        cmd = "python rfast_genspec.py "+rfast_inputs_f
        res = sub.run(cmd.split(),check=True,cwd=RFAST_ROOT)

        # run noise
        cmd = "python rfast_noise.py "+rfast_inputs_f
        res = sub.run(cmd.split(),check=True,cwd=RFAST_ROOT)

        # initialize retreival
        cmd = "python rfast_initret.py "+rfast_inputs_f+' '+rfast_rpars_f
        res = sub.run(cmd.split(),check=True,cwd=RFAST_ROOT)
        
        cmd = "python rfast_retrieve.py "+rfast_inputs_f
        process = sub.Popen(cmd.split(),cwd=RFAST_ROOT)
        
        self.processes.append(process)
        
    def monitor_retrievals(self):
        total = len(self.processes)
        while True:
            number_completed = 0
            for process in self.processes:
                res = process.poll()
                if res != None:
                    number_completed += 1

            fmt = "{:50}"

            print(fmt.format("completed/total = "+str(number_completed)+'/'+str(total)))#,end='\r')
            if number_completed == total:
                break
            else:
                time.sleep(REFRESH_TIME)
