### Clustering algorithm ###

import functools

@functools.lru_cache(maxsize=None)
def euclid_dist(centroid, point):
    varia = 0
    for i in range(min(len(centroid), len(point))):
        varia += (int(point[i])-centroid[i])**2
    return (varia)**.5

#@functools.lru_cache(maxsize=None)
def spectral_angle_old(centroid, point):
    varia = 0
    magnitude = 0
    for i in point:
        magnitude+=i**2
    magnitude= magnitude**0.5
    for i in range(min(len(centroid), len(point))):
        varia += (float(point[i])/magnitude-float(centroid[i]))**2
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

def print_cent_move(centroids,old_centroids):
    ### show centroid movement
    maxi_move = 0
    for new,old in zip(centroids,old_centroids):
        new.update() ###update axyz
###here
        (newx,newy,newz)=new.xyz
        (oldx,oldy,oldz)=old.xyz
        print("Centroid",new.number,"\tPopulation:",len(new.points),
              "\tchange: {:+8d}".format(len(new.points)-len(old.points)))
        #print("Dx:",newx-oldx,"Dy:",newy-oldy,"Dz:",newz-oldz)
        (pdx,pdy,pdz)=((newx-oldx)*100/oldx,
                       (newy-oldy)*100/oldy,
                       (newz-oldz)*100/oldz)
        maxi_move= max(abs(maxi_move),abs(pdx),abs(pdy),abs(pdz))
        print("x: %6.2f%%"%pdx,
              "\ty: %6.2f%%"%pdy,
              "\tz: %6.2f%%"%pdz)
    print("Maximum change: %6.2f%%"%maxi_move)
    return maxi_move



class point(object):
    def __init__(self, imgpoint):
        self.centroid = None
        self.xyz=imgpoint
        self.centdist = 100000
    def __repr__(self):
        return "coordinates: "+repr(self.xyz)+"centroid: "+repr(self.centroid) + ", " + repr(self.centdist)+"\n"
    
class centroid(object):
    def __init__(self, number, xyz):
        self.number = number
        self.xyz=xyz
        self.points = list()
        self.color = (20*number,20*number,20*number)
    def update(self):
        self.axyz=normalize(tuple(self.xyz))
    def __repr__(self):
        return "coordinates: "+repr(self.xyz)+" centroid: "+repr(self.number) + "\n"

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy
from time import clock
from copy import deepcopy

####centroids = list((centroid(x,(0,0,0)) for x in range(10)))
points = list()

centroid_spacing = 72 #600, 200, 72
psuedo_epochs = 100
epoch_size = 20
end_threshold = 2 #percent

### Initialaization of centroids (same as MultiSpec used
centroids = list((centroid(0,(173.6,131.0,136.7)),
                  centroid(1,(145.9,111.4,132.1)),
                  centroid(2,(118.2, 91.8,127.6)),
                  centroid(3,( 90.5, 72.2,123.0)),
                  centroid(4,( 62.8, 52.6,118.4)),
                  centroid(5,( 46.9, 41.4,115.8)),
                  centroid(6,( 42.9, 38.6,115.2)),
                  centroid(7,( 39.0, 35.8,114.5)),
                  centroid(8,( 35.0, 33.0,113.9)),
                  centroid(9,( 31.0, 30.2,113.2))))
C_INIT_FLAG = True
                 

if False:    dist_fn = spectral_angle
else:       dist_fn = euclid_dist

if __name__ == "__main__":
    #filename = input("FileName: ")
    #filename = r"C:\Users\Harold\Downloads\LandSat\512x512 SANFR_2000_03_03_S2(chs_6,4,2)-RGB-blue.tif"
    #filename = r"C:\Users\Harold\Downloads\LandSat\1990SFv2.tif"
    filename = r"C:\Users\Harold\Downloads\512x512 SANFR_2000_03_03_S2(chs_7,4,2).tif"

    ### read in img file
    img = mpimg.imread(filename)
    for i in range(len(img)):
        for j in range(len(img[i])):
            points.append(point(img[i][j]))
    if not C_INIT_FLAG: ##check if centroids have been initialized
        ### initialize centroids to various points
        for i in range(min(len(centroids),len(points))):
            centroids[i].xyz = points[i*centroid_spacing].xyz
    print(centroids)

    ############Training (and classifying)
    for i in range(psuedo_epochs):
        ### epoch loop
        print("loop:",i,"time:",clock())
        while i >= epoch_size: i -= epoch_size ###allow for more loops with less skipping

        ###make a copy of the centroids list
        old_centroids = deepcopy(centroids)
        ### reset all centroid point lists
        for centroid in centroids:
            centroid.update()
            centroid.points = list()
        for p in range(i,len(points),epoch_size): ###skip through points to speed clustering
            point = points[p]
            if point.centroid:
###here
                point.centdist=dist_fn(tuple(point.centroid.xyz),tuple(point.xyz))
            ### loop through points
            for centroid in centroids:
                ###determine closest centorid
###here
                dist = dist_fn(tuple(centroid.xyz),tuple(point.xyz))
                if dist <= point.centdist:
                    point.centroid = centroid
                    point.centdist = dist
            ### add point to closest centroid
            point.centroid.points.append(point)
        
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
            else:
                print("no points")

        if True:
            maxi_move=print_cent_move(centroids,old_centroids)
            if maxi_move < end_threshold:
                print("clusters converged")
                break;
        else:
            ### show centroid movement
            maxi_move = 0
            for new,old in zip(centroids,old_centroids):
                new.update() ###update axyz
    ###here
                (newx,newy,newz)=new.xyz
                (oldx,oldy,oldz)=old.xyz
                print("Centroid",new.number,"\tPopulation:",len(new.points),
                      "\tchange: {:+8d}".format(len(new.points)-len(old.points)))
                #print("Dx:",newx-oldx,"Dy:",newy-oldy,"Dz:",newz-oldz)
                (pdx,pdy,pdz)=((newx-oldx)*100/oldx,
                               (newy-oldy)*100/oldy,
                               (newz-oldz)*100/oldz)
                maxi_move= max(abs(maxi_move),abs(pdx),abs(pdy),abs(pdz))
                print("x: %6.2f%%"%pdx,
                      "\ty: %6.2f%%"%pdy,
                      "\tz: %6.2f%%"%pdz)
            print("Maximum change: %6.2f%%"%maxi_move)
            if maxi_move < end_threshold:
                print("clusters converged")
                break;

                
    ##### classifying only
    print("classify")
    for centroid in centroids:
            centroid.points = list()
    for point in points:
        if point.centroid:
###here
            point.centdist=dist_fn(tuple(point.centroid.xyz),tuple(point.xyz))
        ### loop through points
        for centroid in centroids:
            ###determine closest centorid
###here
            dist = dist_fn(tuple(centroid.xyz),tuple(point.xyz))
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
        else:
            print("no points")

    ### table of: cluster pop, centroids, Std. Dev. (each axis),
    ###     intercluster dist, dist from closest cluster, convergence threshold,
    ###     number of iterations used
    if True:
        for centroid in centroids:
            pass

    ########### Update Image
    order= iter(points)
    for i in range(len(img)):
        for j in range(len(img[i])):
            img[i][j]= next(order).centroid.xyz
    ########Display img
    print("Elapsed time:",clock())
    plt.imshow(img)
    plt.show()

def showimg():
    plt.imshow(img)
    plt.show()
    
