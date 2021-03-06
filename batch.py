# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 10:46:02 2018

@author: B
"""

import os
import subprocess
#import numpy as np

imageGroundTruth=[]
xmlGroundTruth=[]
xmlPrediction=[]
overlap=[]
outputPath='../uutls_ahte_overlap_output/'
#os.makedirs('uutls_ahte_overlap_output/')
csv=False


imageGroundTruth_folder='ahte_test_diva_ground_image/'
xmlGroundTruth_folder='ahte_test_ground_xml/'
xmlPrediction_folder='evaluation_xml/ahte_jults_identity_neighbour_rotate180_flip_blobs_raw_result_xml/'
original_image_folder='ahte_test/'

imageGroundTruth=sorted(os.listdir(imageGroundTruth_folder))
xmlGroundTruth=sorted(os.listdir(xmlGroundTruth_folder))
xmlPrediction=sorted(os.listdir(xmlPrediction_folder))
original_image=sorted(os.listdir(original_image_folder))
#original_image.remove('page')
number_of_files=len(os.listdir(imageGroundTruth_folder))
args=[]
for i in range(number_of_files):
    args.append('-igt')
    args.append(imageGroundTruth_folder + imageGroundTruth[i])
    args.append('-xgt')
    args.append(xmlGroundTruth_folder + xmlGroundTruth[i])
    args.append('-xp')
    args.append(xmlPrediction_folder+xmlPrediction[i])
    args.append('-overlap')
    args.append(original_image_folder + original_image[i])
    args.append('-out')
    args.append(outputPath)
pixelIU=[]
lineIU=[]
lineF1=[]
#f=open('uutls_ahte_results.txt','w')
f=open(xmlPrediction_folder[:-1]+'.txt','w')


for i in range(number_of_files):
    cmd=args[i*10:i*10+10]
    cmd.insert(0,'LineSegmentationEvaluator.jar')
    cmd.insert(0,'-jar')
    cmd.insert(0,'java')
    print(cmd)
    p = subprocess.Popen(cmd, universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,bufsize=1)
    stdO,stdE = p.communicate()
    print(stdO)
    
    ind=stdO.find('pixel IU')
    pixeliu=stdO[ind+10:ind+15]


    if '1.0' in pixeliu:
        pixeliu = float(stdO[ind + 10:ind + 13])
    else:
        pixeliu = float(stdO[ind + 10:ind + 15])

    pixelIU.append(pixeliu)

    ind = stdO.find('line F1')
    
    ind=stdO.find('line IU')
    lineiu=stdO[ind+10:ind+15]
    if '1.0' in lineiu or lineiu =='0.8' :
        lineiu = float(stdO[ind + 10:ind + 13])
    else:
        lineiu = float(stdO[ind + 10:ind + 15])
        

    lineIU.append(lineiu)

    ind = stdO.find('line F1')
    linef1 = stdO[ind + 10:ind + 15]
    if '1.0' in linef1 or linef1=='0.8' or '\n' in linef1:
        linef1 = float(stdO[ind + 10:ind + 13])
    else:
        linef1 = float(stdO[ind + 10:ind + 15])


    lineF1.append(linef1)
    
    print('current lineiu ', lineIU)
    print('current pixeliu ', pixelIU)   
    print('current linef1 ', lineF1)
    filename=args[i*10+1].split('/')[1]
    print(filename)
    f.write(filename+'\t line IU=' +str(lineiu)+'\t pixel IU=' +str(pixeliu)+'\t line F1=' +str(linef1)+'\n')

#mean_pixeliu=np.mean(pixelIU)
#mean_lineiu=np.mean(lineIU)
#mean_linef1=np.mean(lineF1)

mean_pixeliu=sum(pixelIU)/len(pixelIU)
mean_lineiu=sum(lineIU)/len(lineIU)
mean_linef1=sum(lineF1)/len(lineF1)

print('mean line iu = ', mean_lineiu)
print('mean pixel iu = ', mean_pixeliu)
print('mean line f1 = ', mean_linef1)
f.write('\n\n\n')
f.write('mean line iu = '+ str(mean_lineiu)+'\n')
f.write('mean pixel iu = '+ str(mean_pixeliu)+'\n')
f.write('mean line f1 = '+ str(mean_linef1))

f.close()