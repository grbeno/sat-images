import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
import math


class Poly():
    """ Preparation for analysis: Just draw around with points the polygon you would like to get! 
        -> you will get a masked image ready for analysis """

    def __init__(self, image):
        self.img1 = cv2.imread(image)
        self.img2 = cv2.cvtColor(self.img1, cv2.COLOR_BGR2RGB)
        self.fig = plt.figure()
        self.dir = os.path.dirname(image)
        self.points = []
        self.pts = []

    def getCoord(self):
        " show image, call __onclick(), return coordinates " 
        plt.imshow(self.img2)
        cid = self.fig.canvas.mpl_connect('button_press_event', self.__onclick)
        plt.show()
        return self.points

    def __onclick(self,event):
        " onclick event -> draw the points, add pixel's x,y coordinates to list "
        self.points.append((event.xdata,event.ydata))
        plt.plot(event.xdata, event.ydata, '.', color='white', markersize=16)
        self.fig.canvas.draw()

    def mask(self):
        " ... " 
        self.pts = np.array(self.points, np.dtype('int'))

        # Crop the bounding rect
        rect = cv2.boundingRect(self.pts)
        x,y,w,h = rect
        croped = self.img1[y:y+h, x:x+w].copy()
        # Make mask
        self.pts = self.pts - self.pts.min(axis=0)
        mask = np.zeros(croped.shape[:2], np.uint8)
        cv2.drawContours(mask, [self.pts], -1, (255, 255, 255), -1, cv2.LINE_AA)
        # Do bit-op
        dst = cv2.bitwise_and(croped, croped, mask=mask)
        # Add the white background
        bg = np.ones_like(croped, np.uint8)*255
        cv2.bitwise_not(bg,bg, mask=mask)
        res = bg + dst
        if os.path.exists("masked") == False:
            os.mkdir("masked")
        masked = f"masked\\masked{len(os.listdir('masked'))+1}.png"
        cv2.imwrite(masked,res)
        
        # Show image
        cv2.imshow('image',res)
        cv2.waitKey(0)   
        
        # Closing all open windows 
        cv2.destroyAllWindows()

        return masked


class Stainer():
    """ STAINER 'foltozó múdszer'/METHOD: Processing images based on the different scales of gray 
        -> changing them with brighter colors to be more spectacular 
        -> it returns with the relative frequencies. """

    def __init__(self, image,colors):
        self.image = image
        self.colors = colors
        self.stColorInts = [(0,254,255)]
        self.stColors = []
        self.stData = []
        self.dir = os.path.dirname(image)
        
        if os.path.exists("stainer") == False:
            os.mkdir("stainer")
        self.res_img = f'stainer\\stain{len(os.listdir("stainer"))+1}.png'


    def __createStColors(self):
        " Szürkeárnyalatok intervallumai + átfestő/foltozó színek -- grayscaled intervals + colors to stain - min:2, max:16"
        decrease = [0,0,127,84,63,50,42,36,31,28,25,23,21,19,18,16,15] # decrease from 254&('from' values) till lowest, with [i]
        blueColors = [
            (240,248,255),(230,230,250),(135,206,250),(0,191,255),(176,195,222),
            (30,144,255),(70,130,180),(95,158,160),(72,61,139),(65,105,225),
            (138,43,226),(0,109,176),(75,0,130),(0,0,255),(0,0,128),(0,0,57)
        ]
        for i in range(self.colors):
            intvs_len = len(self.stColorInts)-1
            start = self.stColorInts[intvs_len][1]-decrease[self.colors]
            end = self.stColorInts[intvs_len][1]-1
            index = intvs_len
            add_intv = tuple([index,start,end])
            self.stColorInts.append(add_intv)
        
        bright_blues = math.ceil(self.colors/2)
        dark_blues = self.colors - bright_blues
        self.stColors = blueColors[:bright_blues] + blueColors[-dark_blues:]
        self.stColors.insert(0,(255,255,255)) # 0. background


    def stain(self):
        " Stainer folt/színbecslő módszer - Stainer method for colour measuring "
        gray = cv2.imread(self.image)
        gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        new = cv2.imread(self.image)
        height, width = new.shape[1], new.shape[0]
        size = height * width

        self.__createStColors()
        self.stData = [0 for x in range(len(self.stColors))]
        for i in range(width):
            for j in range(height):
                for(index,start,end) in self.stColorInts:
                    if start <= gray[i,j] and gray[i,j] <= end:
                        new[i,j]= self.stColors[index]    
                        count=self.stData[index]
                        self.stData[index]=count+1
                        break
        
        new = cv2.cvtColor(new, cv2.COLOR_BGR2RGB)
        cv2.imwrite(self.res_img, new)
        
        # Show image
        cv2.imshow('image',new)
        cv2.waitKey(0)   
        
        # Closing all open windows 
        cv2.destroyAllWindows()
        
        self.stData = [float(format(data/(size-self.stData[0])*100,'.2f')) for data in self.stData]
        return self.stData
