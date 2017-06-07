### Clustering algorithm ###

use_spectral_angle = False
#### note, also search for "###here" and change things
###### actually should be fine now

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy
from time import clock
from copy import deepcopy

####centroids = list((centroid(x,(0,0,0)) for x in range(10)))
points = list()

centroid_spacing = 200 #600, 200, 72
psuedo_epochs = 40
epoch_size = 1 #2 works, but 20 is much faster, 1 converges in 30 epochs
end_threshold = 1 #percent


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
    #filename = input("FileName: ")
    #filename = r"C:\Users\Harold\Downloads\LandSat\512x512 SANFR_2000_03_03_S2(chs_6,4,2)-RGB-blue.tif"
    #filename = r"C:\Users\Harold\Downloads\LandSat\1990SFv2.tif"
    #filename = r"C:\Users\Harold\Downloads\512x512 SANFR_2000_03_03_S2(chs_7,4,2).tif"
    filename = r"C:\Users\Harold\Dropbox\Projects\rgb-compose-742.png"

    ### read in img file
    img = mpimg.imread(filename)
    for i in range(len(img)):
        for j in range(len(img[i])):
            points.append(point(img[i][j]))
    if not C_INIT_FLAG: ##check if centroids have been initialized
        ### initialize centroids to various points
        for i in range(min(len(centroids),len(points))):
            centroids[i].xyz = points[i*centroid_spacing].xyz
            centroids[i].update()
    print(centroids)

    iter_length=len(points)//epoch_size


    ############Training (and classifying)
    for i in range(psuedo_epochs):
        ### epoch loop
        print("loop:",i,"time:",clock())
        passes = i
        while i >= epoch_size: i -= epoch_size ###allow for more loops with less skipping

        ###make a copy of the centroids list
        old_centroids = deepcopy(centroids)
        ### reset all centroid point lists
        for centroid,old in zip(centroids,old_centroids):
            centroid.update()
            old.update()
            centroid.points = list()
        total_changed = 0
        for p in range(i,len(points),epoch_size): ###skip through points to speed clustering
            point = points[p]
            if point.centroid:
###here
                point.centdist=dist_fn(tuple(point.centroid.axyz),tuple(point.xyz))
            ### loop through points
            change_flag = False # tracks if a point changes centroids
            for centroid in centroids:
                ###determine closest centorid
###here
                dist = dist_fn(tuple(centroid.axyz),tuple(point.xyz))
                if dist < point.centdist:
                    point.centroid = centroid
                    point.centdist = dist
                    change_flag = True
            ### add point to closest centroid
            point.centroid.points.append(point)
            if change_flag: total_changed+=1
        
        ##update centroids values
#### FIXUP: The spectral angle centroids are averaged in a non-normalized form, This might be undesireable
        for centroid in centroids:
            (x,y,z)=(0,0,0)
            length= len(centroid.points)
            if length > 0:
                for point in centroid.points:
                    x+=point.xyz[0]
                    y+=point.xyz[1]
                    z+=point.xyz[2]
                centroid.xyz=(x/length,y/length,z/length)
                centroid.update()
            else:
                print("no points")

        ### Print centroid movement and check if we have converged
        maxi_move=print_cent_move(centroids,old_centroids,total_changed,
                                  100*total_changed/iter_length)
        if maxi_move < end_threshold:
            print("clusters converged, time:",clock())
            break;

                
    ##### classifying only
    print("classify")
    ###make a copy of the centroids list
    old_centroids = deepcopy(centroids)
    ### reset all centroid point lists
    for centroid in centroids:
        centroid.update()
        centroid.points = list()
    for point in points:
        if point.centroid:
###here
            point.centdist=dist_fn(tuple(point.centroid.axyz),tuple(point.xyz))
        ### loop through points
        for centroid in centroids:
            ###determine closest centorid
###here
            dist = dist_fn(tuple(centroid.axyz),tuple(point.xyz))
            if dist <= point.centdist:
                point.centroid = centroid
                point.centdist = dist
        ### add point to closest centroid
        point.centroid.points.append(point)
    ##update centroids
    for centroid in centroids:
        (x,y,z)=(0,0,0)
        length= len(centroid.points)
        if length > 0:
            for point in centroid.points:
                x+=point.xyz[0]
                y+=point.xyz[1]
                z+=point.xyz[2]
            centroid.xyz=(x/length,y/length,z/length)
            centroid.update()
        else:
            print("no points")

    ### table of: cluster pop, centroids, Std. Dev. (each axis),
    ###     intercluster dist, dist from closest cluster, convergence threshold,
    ###     number of iterations used
    maxi_move=print_cent_move(centroids,old_centroids)
    
    print_stats(centroids,maxi_move,passes)

    ########### Update Image
    order= iter(points)
    for i in range(len(img)):
        for j in range(len(img[i])):
            nxt=next(order)
            if nxt.centroid.cp: color= nxt.centroid.color
            else: color= nxt.centroid.xyz
            img[i][j]= color
    ########Display img
    print("Elapsed time:",clock())
    plt.imshow(img)
    plt.show()

######Legendize, Somehow

def showimg():
    plt.imshow(img)
    plt.show()

def saveimg(fname,image):
    mpimg.imsave(fname,image)
