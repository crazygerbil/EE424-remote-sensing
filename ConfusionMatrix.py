### Clustering algorithm ###

use_spectral_angle = True
#### note, also search for "###here" and change things
###### actually should be fine now

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy
from time import clock
from copy import deepcopy

####centroids = list((centroid(x,(0,0,0)) for x in range(10)))
points = list()
points2 = list()

import functools

@functools.lru_cache(maxsize=None)
def euclid_dist(centroid, point):
    varia = 0
    for i in range(min(len(centroid), len(point))):
        varia += (float(point[i])-centroid[i])**2
    return (varia)**.5

### makes it take up way more memory, but reduces calculation time by ~20%
@functools.lru_cache(maxsize=None)
def spectral_angle(centroid, point):
    varia = 0
    point = normalize(point)
    for i in range(min(len(centroid), len(point))):
        varia += (point[i]-float(centroid[i]))**2
    return (varia)**.5

@functools.lru_cache(maxsize=None)
def normalize(xyz):
    magnitude = 0
    for i in xyz: magnitude+=i**2
    magnitude= magnitude**0.5
    return (float(xyz[0])/magnitude,
            float(xyz[1])/magnitude,
            float(xyz[2])/magnitude)

def print_cent_move(centroids,old_centroids,total_changed=False,percent=0):
    ### show centroid movement
    maxi_move = 0
    for new,old in zip(centroids,old_centroids):
        new.update() ###update axyz
###here
        (newx,newy,newz)=new.axyz
        (oldx,oldy,oldz)=old.axyz
        print("Centroid",new.number,"\tPopulation:%7d"%len(new.points),
              "\tchange: {:+8d}".format(len(new.points)-len(old.points)))
        #print("Dx:",newx-oldx,"Dy:",newy-oldy,"Dz:",newz-oldz)
        (pdx,pdy,pdz)=((newx-oldx)*100/oldx,
                       (newy-oldy)*100/oldy,
                       (newz-oldz)*100/oldz)
        maxi_move= max(abs(maxi_move),abs(pdx),abs(pdy),abs(pdz))
        #print("x: %6.2f%%"%pdx,"\ty: %6.2f%%"%pdy,"\tz: %6.2f%%"%pdz)
    print("Maximum change: %6.2f%%"%maxi_move)
    if total_changed:
        print("Points changed: {:6d} {:6.3f}%".format(total_changed,percent))
    return maxi_move

def print_stats(centroids,maxi_move,passes):
    for centroid in centroids:
        print("Centroid %d"%centroid.number)
        print("Population:",len(centroid.points),
              "or {:6.3f}%".format(100*len(centroid.points)/(512*512)))

        ###Position
        print("Center:",end="")
        if (len(centroid.xyz) != 3): raise("dimensionality")
###here Maybe
        for i,axis in zip(centroid.xyz,("\t2:\t","\t4:\t","\t7:\t")):
            print(axis,i,sep="",end="")
        print()

        ###Std Dev
        print("Std. Dev.: ",end="")
        centroid.calc_std_dev()
        if (len(centroid.std_devs) != 3): raise("dimensionality")
        for i,axis in zip(centroid.std_devs,("2:\t","\t4:\t","\t7:\t")):
            print(axis,i,sep="",end="")
        print()

        ### Avg distance:
        print("Avg. distance from centroid: ",end="")
        if (len(centroid.std_devs) != 3): raise("dimensionality")
        print(centroid.calc_avg_dist())

        ###end centroid
        print()
    print("Convergence Threshold Nominal:{:6.2f}%\tActual:{:6.2f}%".format\
          (end_threshold,maxi_move))
    print("Cluster convergence passes: {:d}, +1 final classification pass"\
          .format(passes+1))


class point(object):
    def __init__(self, imgpoint):
        self.centroid = None
        self.xyz=imgpoint
        self.centdist = 100000
    def __repr__(self):
        return "coordinates: "+repr(self.xyz)+"centroid: "+repr(self.centroid) + ", " + repr(self.centdist)+"\n"
    
class centroid(object):
    def __init__(self, number, xyz, color=False):
        self.number = number
        self.xyz=xyz
        self.update()
        self.points = list()
        if not color:
            self.color = (20*number,20*number,20*number)
            self.cp=False
        else:
            self.color = color
            self.cp=True
    if use_spectral_angle:
        def update(self):
            self.axyz=normalize(tuple(self.xyz))
    else:
        def update(self):
            self.axyz=self.xyz
    def calc_avg_dist(self):
        total=0
        for point in self.points:
###here
            total+=dist_fn(tuple(self.axyz),tuple(point.xyz))
        return total/len(self.points)
    def calc_std_dev(self):
        dimensionality = len(self.xyz)
        totals_vari=[0]*dimensionality
        for point in self.points:
            for i in range(dimensionality):
                totals_vari[i]+=(point.xyz[i]-self.xyz[i])**2
        self.std_devs=[(i/len(self.points))**0.5 for i in totals_vari]
    def __repr__(self):
        return "coordinates: "+repr(self.xyz)+" centroid: "+repr(self.number) + "\n"


### Assign distance function as desired
if use_spectral_angle:
    dist_fn = spectral_angle
else:
    dist_fn = euclid_dist

### Initialaization of centroids (same as MultiSpec used)
#WARNING: I may have gotten the 2 and 7 channels backwards?
centroids = list((centroid(0,(173.6,131.0,136.7)[::-1]),
                  centroid(1,(145.9,111.4,132.1)[::-1]),
                  centroid(2,(118.2, 91.8,127.6)[::-1]),
                  centroid(3,( 90.5, 72.2,123.0)[::-1]),
                  centroid(4,( 62.8, 52.6,118.4)[::-1]),
                  centroid(5,( 46.9, 41.4,115.8)[::-1]),
                  centroid(6,( 42.9, 38.6,115.2)[::-1]),
                  centroid(7,( 39.0, 35.8,114.5)[::-1]),
                  centroid(8,( 35.0, 33.0,113.9)[::-1]),
                  centroid(9,( 31.0, 30.2,113.2)[::-1])))
C_INIT_FLAG = False


if __name__ == "__main__":
    filename = r"C:\Users\Harold\Dropbox\Projects\rgb-compose-742-dist-classed.png"
    ### read in img file
    img = mpimg.imread(filename)
    classes = dict()
    for i in range(len(img)):
        for j in range(len(img[i])):
            points.append(point(tuple(img[i][j])))
    ### initialize centroids to various points
    for pointy in points:
        if pointy.xyz in classes:
            classes[pointy.xyz] += 1
        else:
            classes[pointy.xyz] = 1
    #print(classes)
    
    filename2 = r"C:\Users\Harold\Dropbox\Projects\rgb-compose-742-r-dist-classed.png"
    ### read in img file
    img2 = mpimg.imread(filename2)
    classes2 = dict()
    for i in range(len(img2)):
        for j in range(len(img2[i])):
            points2.append(point(tuple(img2[i][j])))
    ### initialize centroids to various points
    for pointy in points2:
        if pointy.xyz in classes2:
            classes2[pointy.xyz] += 1
        else:
            classes2[pointy.xyz] = 1
    #print(classes2,classes2.keys(),sep="\n")
    confusion = dict((((i,0) for i in classes.keys())))
    for clas1 in confusion.keys():
        confusion[clas1] = dict((((i,0) for i in classes2.keys())))
        for clas2 in confusion[clas1].keys():
            confusion[clas1][clas2] = 0

    for point1,point2 in zip(points,points2):
        confusion[point1.xyz][point2.xyz] += 1

    for clas1 in confusion.keys():
        for clas2 in confusion[clas1].keys():
            print(confusion[clas1][clas2],end=",\t")
        print()

#sorted(dict((("1",2),("4",1))).items(),key=lambda x: x[1])
#[('4', 1), ('1', 2)]


def showimg():
    plt.imshow(img)
    plt.show()

def saveimg(fname,image):
    mpimg.imsave(fname,image)
