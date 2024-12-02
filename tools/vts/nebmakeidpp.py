#!/usr/bin/env python

from sys import argv
import os, sys

# ASE imports, require module with ASE
import ase
from ase.optimize import FIRE
from ase.neb import NEBTools, SingleCalculatorNEB
from ase.constraints import FixAtoms
from ase.calculators.singlepoint import SinglePointCalculator
from ase.calculators.lj import LennardJones


def block_print():
    sys.stdout = open(os.devnull, 'w')

def enable_print():
    sys.stdout = sys.__stdout__

nimages = int(argv[3])
fmax = 1e-6
nsteps = 300
apply_constraint = True
print(ase.__version__)

if '-h' in argv or 4 < len(argv) < 3:
	print('usage: nebmake_idpp.py POSCAR1 POSCAR2 num_images [-NOIDPP]')
	print
	exit(1)

# read initial and final files 
ini_atoms = ase.io.read(filename=argv[1], format='vasp')
fin_atoms = ase.io.read(filename=argv[2], format='vasp')

#start print blocking 
block_print()

images = [ini_atoms]
for i in range(nimages):
	images.append(ini_atoms.copy())
images.append(fin_atoms)

# Fix all atoms except conductive ones
for image in images:
    c = FixAtoms(indices=[atom.index for atom in image if atom.symbol not in ['Li', 'Na', 'K', 'Rb', 'Pb']])
    image.set_constraint(c)
    image.set_pbc((True, True, True))

# NEB calculations
neb = SingleCalculatorNEB(images)
neb.set_calculators( LennardJones() )

neb.interpolate(apply_constraint=apply_constraint)
neb.idpp_interpolate(fmax=fmax, optimizer=FIRE)

# enable printing and print barrier
enable_print()
images = neb.images
nebtools = NEBTools(images)
barrier, dE = nebtools.get_barrier()
print("Barrier: {}, dE: {}".format(barrier, dE))

for image in images:
    image.set_constraint(None)
    image.set_pbc((True, True, True))

# copy structures to directories
dir_names = ['0'+str(i) if i < 10 else str(i) for i in range(len(images))]
for i, image in zip(dir_names,neb.images):
    if not os.path.isdir(i):
        os.mkdir(i)
    #write_vasp(i+'/POSCAR',image)
    ase.io.write(i+'/POSCAR', image, format='vasp')

print('Ok, all set up here.')
print('For later analysis, put OUTCARs in folders 00 and ' + dir_names[-1])

