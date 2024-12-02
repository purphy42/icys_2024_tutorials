#!/usr/bin/env python

from aselite import read_vasp, write_vasp, NEB
from sys import argv
import os

# ASE imports, require module with ASE
from ase.optimize import FIRE
from ase.neb import NEBTools
from ase.constraints import FixAtoms
from ase.calculators.singlepoint import SinglePointCalculator
from ase.calculators.lj import LennardJones

nimages = argv[3]
fmax = 1e-6
nsteps = 200

if '-h' in argv or 4 < len(argv) < 3:
	print('usage: nebmake_idpp.py POSCAR1 POSCAR2 num_images [-NOIDPP]')
	print
	exit(1)

# read initial and final files 
ini_atoms = read_vasp(argv[1])
fin_atoms = read_vasp(argv[2])

images = [ini_atoms]
for i in range(nimages):
	images.append(ini_atoms.copy())
images.append(fin_atoms)

# Fix all atoms except conductive ones
for image in images:
    c = FixAtoms(indices=[atom.index for atom in image if atom.symbol not in ['Li', 'Na', 'K', 'Rb', 'Pb']])
    image.set_constraint(c)

# NEB calculations
neb = SingleCalculatorNEB(images)
neb.set_calculators( LennardJones() )

neb.interpolate()
neb.idpp_interpolate(fmax=fmax, optimizer=FIRE)

images = neb.images
nebtools = NEBTools(images)
barrier, dE = nebtools.get_barrier()
print("Barrier: {}, dE: {}".format(barrier, dE))

# copy structures to directories
dir_names = ['0'+str(i) if i < 10 else str(i) for i in range(len(images))]
for i, image in zip(dir_names,neb.images):
	if not os.path.isdir(i):
		os.mkdir(i)
	write_vasp(i+'/POSCAR',image)
print('Ok, all set up here.')
print('For later analysis, put OUTCARs in folders 00 and ' + dir_names[-1])

