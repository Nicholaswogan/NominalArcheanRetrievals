# NominalArchean

This repository contains scripts to run batch retrievals with `rfast`.

# Requirements

Following commands download all code needed to reproduce results. Must have a Fortran and C compiler.

```sh
# create conda environment
conda create -n archean -c conda-forge -c astropy python=3.9 numpy scipy numba pyyaml scikit-build cython jupyter matplotlib astropy emcee corner

# activate
conda activate archean

# photochem v0.2.5
wget https://github.com/Nicholaswogan/photochem/archive/refs/tags/v0.2.5.zip
unzip v0.2.5.zip
cd photochem-0.2.5
python -m pip install --no-deps --no-build-isolation .
cd ..
rm -rf photochem-0.2.5 v0.2.5.zip

# ImpactAtmosphere v4.2.7
git clone https://github.com/Nicholaswogan/rfast.git
cd rfast
git checkout 6d6ac25d597767ce43e46e02e73d8b1b543ea205
python -m numpy.f2py -c lblabc_input.f95 -m lblabc_input
cd ..
```