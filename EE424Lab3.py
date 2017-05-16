### Clustering algorithm ###

def euclid_dist(centroid, point):
    varia = 0
    for i in range(min(len(centroid), len(point))):
        varia += (int(point[i])-int(centroid[i]))**2
    return (varia)**.5

def spectral_angle(centroid, point):
    varia = 0
    magnitude = 0
    for i in point:
        magnitude+=i**2
    magnitude= magnitude**0.5
    for i in range(min(len(centroid), len(point))):
        varia += (float(point[i])/magnitude-float(centroid[i]))**2
    return (varia)**.5


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
        xyz=self.xyz
        magnitude = 0
        for i in xyz: magnitude+=i**2
        magnitude= magnitude**0.5
        self.axyz=(xyz[0]/magnitude,xyz[1]/magnitude,xyz[2]/magnitude)
    def __repr__(self):
        return "coordinates: "+repr(self.xyz)+" centroid: "+repr(self.number) + "\n"

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy

centroids = list((centroid(x,(0,0,0)) for x in range(10)))
points = list()

centroid_spacing = 200

if True:    dist_fn = spectral_angle
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
    ### initialize centroids to various points
    for i in range(min(len(centroids),len(points))):
        centroids[i].xyz = points[i*centroid_spacing].xyz
    print(centroids)

    ############Training (and classifying)
    for i in range(20):
        ### epoch loop
        print("loop:",i)
        while i >= 10: i -= 10 ###allow for more loops with less skipping

        ### reset all centroid point lists
        for centroid in centroids:
            centroid.update()
            centroid.points = list()
        for p in range(i,len(points),10): ###skip through points to speed clustering
            point = points[p]
            if point.centroid:
                point.centdist=dist_fn(point.centroid.axyz,point.xyz)
            ### loop through points
            for centroid in centroids:
                ###determine closest centorid
                dist = dist_fn(centroid.axyz,point.xyz)
                if dist <= point.centdist:
                    point.centroid = centroid
                    point.centdist = dist
            ### add point to closest centroid
            point.centroid.points.append(point)
        
        ##update centroids values
#### FIXUP: The spectral angle centroids are averaged in a non-normalized form, This might be undesireable
        from copy import deepcopy
        old_centroids = deepcopy(centroids)
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
        ### show centroid movement
        for new,old in zip(centroids,old_centroids):
            (newx,newy,newz)=new.xyz
            (oldx,oldy,oldz)=old.xyz
            print("Centroid",new.number)
            print("Dx:",newx-oldx,"Dy:",newy-oldy,"Dz:",newz-oldz)

                
    ##### classifying only
    print("classify")
    for centroid in centroids:
            centroid.points = list()
    for point in points:
        if point.centroid:
            point.centdist=dist_fn(point.centroid.axyz,point.xyz)
        ### loop through points
        for centroid in centroids:
            ###determine closest centorid
            dist = dist_fn(centroid.axyz,point.xyz)
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
    plt.imshow(img)
    plt.show()
