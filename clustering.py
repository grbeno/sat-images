import os
import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


class Clustering():
    """ You will get the data of processed images by the k-mean clustering method. """
    
    # Output data -> results
    percent = []
    centers = []
    
    " Initial instance variables & methods "

    def __init__(self, path,clusters):
        self.path = path
        self.clusters =  self.__cluster_input_correction(clusters) + 1 # clusters: relevant clusters, + 1: background
        self.back = (254,254,254)
        self.image = cv2.imread(self.path)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.image = self.image.reshape((self.image.shape[0] * self.image.shape[1], 3))

        # Calling Clustering method
        self.clustering()


    " Correction & Validation methods here ... "
    
    def __cluster_input_correction(self,clusters):
        " Handle negative & zero inputs: correction to 1 "
        if clusters < 1:
            return 1
        return clusters


    " K-MEANS CLUSTERING "
    
    " 1. Preparation "

    def __distance(self, pix,color):
        " Euclidean distance - detect background pixels - not only the exact color "
        lim, res, channel = 5, 0, 3
        for i in range(channel):
            res = res + (color[i]-pix[i])**2
        if res**(1/2) <= lim:
            return True
        return False


    def __center_find(self, ndarr,bcolor):
        " Find the center in the 'bcolor' domain " 
        ndarr = np.rint(ndarr)
        for i in range(len(ndarr)):
            if self.__distance(ndarr[i],bcolor):
                return i
        return None


    def __get_cldatas(self, color,centers,clt_labels):
        " Delete background color from the centers and the labels belong to "
        if color is not None:
            centers = np.delete(centers,color,0)
            labels = np.delete(clt_labels,np.where(clt_labels == color))
        else:
            labels = clt_labels
        return (centers, list(labels))

    " 2. Clustering "

    def clustering(self):
        " Info: cluster centers == array indexes: e.g. cluster_centers_[0] -> 0 "
        clt = KMeans(n_clusters = self.clusters)
        clt.fit(self.image)
        centers = np.rint(clt.cluster_centers_)
        labels = clt.labels_
        
        # Filtering background
        background = self.__center_find(centers,self.back)
        
        # Update centers, labels with filtered background color
        self.centers, labels = self.__get_cldatas(background,centers,clt.labels_)
        
        for i in range(len(self.centers) + 1): # + 1: replace deleted background
            if i != background:
                j=labels.count(i)
                j=j/len(labels)
                self.percent.append(format(j*100,'.2f'))   
        
        plt.pie(self.percent,colors=np.array(self.centers/255),labels=self.percent)
        if os.path.exists("clusters") == False:
            os.mkdir("clusters")
        plt.savefig(f"clusters\\cls_{len(os.listdir('clusters'))+1}")
        
        # Results <- round down!
        return self.centers.astype(int)