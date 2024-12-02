# -*- coding: utf-8 -*-
"""
User-related parameters for siman, file is installed to home folder

"""
from __future__ import division, unicode_literals, absolute_import 
from siman.header import CLUSTERS

"""Cluster constants"""
DEFAULT_CLUSTER = 'razor64' #short name of cluster
PATH2ARCHIVE = '' # path to archive; if no files are found at home folder, siman will check here; relative paths should be same

user = 'a.burov'
# Cluster settings
CLUSTERS['razor64'] = {'address':user+'@10.16.77.14', #cluster address
'vasp_com':'mpirun -np 4 vasp_std', #command for VASP perfoming on cluster
'homepath':'/home/'+user, #path to home directory on cluster
'schedule':'SLURM', #type of schedule system using on cluster
'walltime':'0:20:00', #maximum time for job execution, hours:minutes:seconds, after this time since job was started process will be killed by system
'corenum':4, #number of cores for perfoming of one job on cluster
'modules':'source /etc/profile.d/modules.sh; module load devtools/compiler/aocc/4.0.0 devtools/mpi/openmpi/4.1.5/gcc/11.3 q-ch/vasp/5.4.4 \
\nulimit -s unlimited\n\
'
}

"""Local constants"""
PATH2POTENTIALS = '/home/'+user+'/icys_2024/potcars/'
PATH2JMOL = 'java -jar Jmol.jar'
PATH2NEBMAKE = '~/tools/vts/nebmake.py'
pmgkey = "AWqKPyV8EmTRlf1t" #MAPI_KEY can be generated in the following webpage: https://materialsproject.org/dashboard 
EXCLUDE_NODES = False

cluster_tools = 'icys/tools/'
show_head = None # show header for res_loop()

pmgkey = "dzpOVLsVP3VWa3VIOB"

