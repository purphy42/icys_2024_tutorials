#!/usr/bin/env python
import subprocess
import os 
import numpy
import sys
from kdb_remote_client import run as remote_run
from kdb_local_client import run as local_run
from aselite import read_vasp
from aselite import Atoms  # def get_distance(self, a0, a1, mic=False):
#Should find the reactant,saddle,product,compute the forward and reverse barriers, and submit it in the the correct format

#CODE :
#Get numbers of images in system
# for each image: append its energy to array, find max of array ->saddle energy, submit process to kdb

def get_saddle_image_number_and_barriers(path):
    num_img = ( 'grep "IMAGES" INCAR | tail -n 1|cut -c 8-106')
    eng_img = ('grep "energy  without" OUTCAR | tail -n 1|cut -c 67-78')
    temp_NI = (subprocess.check_output(num_img, shell=True).decode("utf-8"))
    temp_NI = temp_NI.strip()
    NI = int(temp_NI[-1])
    Energy_All = []#Array to store energy of each image including reactant and product
    for i in range(0,NI+2):
        os.chdir(path+"/0"+str(i))
        try:
          if "OUTCAR.gz" in os.listdir():
            os.system("gunzip OUTCAR.gz")
          if "OUTCAR" in os.listdir():
            pass
        except:
          print ("No OUTCAR or OUTCAR.gz in directory")
        energy_image = float(subprocess.check_output(eng_img, shell=True)) 
        Energy_All.append(energy_image)
        Sadd_Img = numpy.where(Energy_All==numpy.amax(Energy_All))[0][0]#get index of max of images
    forward_barrier = (numpy.amax(Energy_All)-Energy_All[0])
    reverse_barrier = (numpy.amax(Energy_All)-Energy_All[NI+1])
    print ("forward_barrier: ",forward_barrier)
    print ("reverse_barrier: ",reverse_barrier)
    print ("The saddle is image "+ str( Sadd_Img))
    return Sadd_Img,NI

#state_i = (read_vasp('MIN_1'))	
#state_j = (read_vasp('MIN_2'))

def get_mode(before_saddle,after_saddle):
    #print ("Entered get_mode function")
    mode = []
    before_saddle = (read_vasp(before_saddle))
    a_saddle = (read_vasp(after_saddle))
    #print ("State I Cell: ",before_saddle.get_cell())
    #print ("State I Cell[0]: ",before_saddle.get_cell()[0])
    #print ("State J: ",saddle.get_positions())
    Saddle_Half_Cell = numpy.linalg.norm(a_saddle.get_cell())/2
    movement = a_saddle.get_positions()-before_saddle.get_positions()
    #print ("Movement: ",movement)
    # NEED TO FINISH THIS CODE, How exactly to account for PBC?
    for i in range(len(movement)):
        Dr = numpy.linalg.solve(a_saddle.get_cell().T, movement[i])
        D = numpy.dot(Dr - numpy.round(Dr) * a_saddle.get_pbc(), a_saddle.get_cell())
        movement[i] = D
    mode = movement
    #print ("Mode: ",mode)
    return mode

#allows users to add -l in arguments in case they wish to create a local kdb
def get_options():
    local_insert = False
    for i in sys.argv:
        if i =="-l":
            local_insert = True
    print("Local Insert: ", local_insert)
    return local_insert

path = os.getcwd()#Get the path from where the script is run

def main():
    Saddle_Image,NI = get_saddle_image_number_and_barriers(path)
    reactant = path+"/00/POSCAR"
    saddle = path+"/0"+str(Saddle_Image)+"/CONTCAR"
    #saddle = path+"/05"+"/CONTCAR"
    product = path+"/0"+str(NI+1)+"/POSCAR"
    #print (reactant)
    #print (saddle)
    #print (product)
    if Saddle_Image > NI: #Product is the highest energy image
        mode = get_mode(path+"/0"+str(NI)+"/CONTCAR",product)
    else: #Case that a middle image is the highest energy image
        after_saddle = path+"/0"+str(Saddle_Image+1)+"/CONTCAR"
        mode = get_mode(path+"/0"+str(Saddle_Image-1)+"/CONTCAR",after_saddle)
    #print ("Mode: ",mode)
    os.chdir(path)#Ensure Back at original path
    f = open("MODE.dat", "a")
    for i in range (len(mode)):
       for j in range (3):
        f.write(str(mode[i][j])+"\t")
        if j ==2:
           f.write("\n")
    path_mode = path+"/MODE.txt"
    f.close()
    local_insert = get_options()
    if local_insert:
        os.chdir("/kdb/fri/lihao/0")
        insert_kdb = (local_run(["insert",reactant,saddle,product,path_mode]))
        #insert_kdb = (local_run(["insert",reactant,saddle,product]))
    else:
        #insert_kdb = (remote_run(["insert",reactant,saddle,product,mode])) 
        insert_kdb = (remote_run(["insert",reactant,saddle,product])) 
    return 0

main()

