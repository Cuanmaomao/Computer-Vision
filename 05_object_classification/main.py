# import the necessary packages
import numpy as np
import os
import glob
import cv2.cv as cv
import cv2
import random
from svmFile import *

'''
print "Testing phase is: "
#testing of the classifier
test_path="D:/Test/"
Test_Histogram=[]
entries=os.listdir(test_path)
for pic in entries:
    new_path=test_path+str(pic)
    print new_path
    im = cv2.imread(new_path)
    kpts = fea_det.detect(im)
    kpts, des = des_ext.compute(im, kpts)
    label_Test=h_cluster.predict(des)
    for i in range(0,len(label_Test)):
            LabelHistogram[label_Test[i]-1]+=1
    Test_Histogram=np.append(Test_Histogram,LabelHistogram)
    Result=clf.predict(LabelHistogram)
'''
class video:
    def __init__(self,path):
        global newpath
        self.numberOfSamples = 20
        self.requiredMatches = 2
        self.distanceThreshold = 20
        self.subsamplingFactor = 16
        self.fname=[]
        self.path=path
        newpath = r'Frames'
        if not os.path.exists(newpath): os.makedirs(newpath)
        newpath = r'NewFrames'
        if not os.path.exists(newpath): os.makedirs(newpath)
        bigSampleArray = self.initialFraming(self.path)
        self.processVideo(bigSampleArray)

    def sort_files(self):
        for file in sorted(glob.glob("Frames/*.*")):
            s=file.split ('/')
            a=s[-1].split('\\')
            x=a[-1].split('.')
            self.fname.append(int(x[0]))
        return(sorted(self.fname)) 

    def initialFraming(self,path):
        global cap
        global success
        global frame
        
        sampleIndex=0
        cap = cv2.VideoCapture(path)
        success,frame=cap.read(cv.CV_IMWRITE_JPEG_QUALITY)       
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #gray = cv2.GaussianBlur(gray, (21, 21), 0)
        height,width = gray.shape[:2]
        print "Dimension of the image is: ",height, width, (height*width)

        samples = np.array([[0 for x in range(0,self.numberOfSamples)] for x in range(0,(height*width))])

        tempArray = np.reshape(gray,(height*width)).T
        
        samples[:,sampleIndex]= np.copy(tempArray)
        sampleIndex+=1

        while (success and sampleIndex!=(self.numberOfSamples)):
            success,frame = cap.read(cv.CV_IMWRITE_JPEG_QUALITY)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #gray = cv2.GaussianBlur(gray, (21, 21), 0)
            tempArray = (np.reshape(gray,(height*width))).T
            samples[:,sampleIndex]= np.copy(tempArray)
            sampleIndex+=1

        return samples

    def writeVideo(self):
        height,width=cv2.imread("Frames/1.jpg").shape[:2]
        out = cv2.VideoWriter("changedOutput.ogv",cv.CV_FOURCC('t','h','e','0'), 25.0, (width,height))
        folder=self.sort_files()
            
        for i in folder:
            pic="Frames/"+str(i)+".jpg"
            img=cv2.imread(pic) 
            out.write(img)
        out.release()

    def getNeighbours(self,arrayX,arrayY, height, width):
        neighbourX = [(arrayX-1),arrayX,(arrayX+1),(arrayX-1),(arrayX+1),(arrayX-1),arrayX,(arrayX+1)]
        neighbourY = [(arrayY-1),(arrayY-1),(arrayY-1),arrayY,arrayY,(arrayY+1),(arrayY+1),(arrayY+1)]
##        print "neighbourX , neighburY is: ",neighbourX, neighbourY
        finalX = []
        finalY = []
        for i in range(0,len(neighbourX)):
            if(neighbourX[i]>=height or neighbourY[i]>=width or neighbourX[i]<0 or neighbourY[i]<0):
                temp = 0
            else:
                finalX.append(neighbourX[i])
                finalY.append(neighbourY[i])
       
        return np.array(finalX),np.array(finalY)
    

    def findValues(self,neighbourX, neighbourY, width):
        valueArray =  np.zeros(len(neighbourX))
        for i in range(0,len(neighbourX)):
            valueArray[i] = (width* neighbourX[i]) + neighbourY[i]
            
        return valueArray

    def getPixelLocation(self,p, h, w):
        arrayX=p/w
        arrayY=p%w
        nX, nY = self.getNeighbours(arrayX, arrayY, h, w)
        values = self.findValues(nX, nY, w)
##        print "values are: ",values
        randomPixel = int(values[random.randint(0,len(values)-1)])
        return randomPixel
        
    def processVideo(self,bigSampleArray):
        Test_Histogram=[]
        global success
        global frame
        global cap
        
        Finalcount=1
        samples= bigSampleArray

        i=0
        TemplateCount = 1
        while success:
##            success,frame = cap.read(cv.CV_IMWRITE_JPEG_QUALITY)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #gray = cv2.GaussianBlur(gray, (21, 21), 0)
            height,width = gray.shape[:2]
            tempArray = np.reshape(gray,(height*width)).T
            segmentationMap = np.copy(tempArray)*0
            for p in range(0,len(bigSampleArray)):
##                print "Value of p is: ",p
                count = index = distance = 0

                while((count < self.requiredMatches) and (index < self.numberOfSamples)):
                    distance = np.linalg.norm(tempArray[p]-samples[p][index])
##                    print "Euclidean distance is: ",distance
                    if (distance < self.distanceThreshold):
                        count += 1
##                        print "count reached" ,count
                    index += 1

                if(count<self.requiredMatches):
                    segmentationMap[p]=255   
                else:
                    segmentationMap[p]=0
                    randomNumber= random.randint(0,self.subsamplingFactor-1)
                    if(randomNumber==0):
                        randomNumber= random.randint(0,self.numberOfSamples-1)
                        samples[p][randomNumber] = tempArray[p]
                    randomNumber = random.randint(0, self.subsamplingFactor-1)
##                    print "Random number detected is: ",randomNumber
                    if(randomNumber==0):
##                        print "Enters randomNumber section"
                        q = self.getPixelLocation(p,height,width)
##                        print "Returned q value is: ",q
                        randomNumber = random.randint(0,self.numberOfSamples-1)
                        samples[q][randomNumber] = tempArray[p]
		#if the `q` key is pressed, break from the loop
		key = cv2.waitKey(1) & 0xFF
            	if key == ord("q"):
                    break
                    
            segmentationMap= np.reshape(segmentationMap,(height,width))

            #cv2.imwrite(NewPath,segmentationMap)
            thresh = cv2.dilate(segmentationMap, None, iterations=2)
            (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                       cv2.CHAIN_APPROX_SIMPLE)
            for c in cnts:
                NewPath="NewFrames/"+ str(TemplateCount) + ".jpg"
                area = cv2.contourArea(c) 
                if area > 1000:
                    #mask = np.zeros_like(gray) # Create mask where white is what we want, black otherwise
                    #cv2.drawContours(mask, [c], 0, 255) # Draw filled contour in mask
                    #out = np.zeros_like(gray) # Extract out the object and place into output image
                    #out[mask == 255] = gray[mask == 255]

                    # Show the output image
                    #cv2.imshow('Output', out)
                    (x, y, w, h) = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    crop_img = gray[y: y + h, x: x + w]
                    #im = cv2.imread(new_path)
                    kpts = fea_det.detect(crop_img)
                    kpts, des = des_ext.compute(im, kpts)
                    label_Test=h_cluster.predict(des)
                    for i in range(0,len(label_Test)):
                            LabelHistogram[label_Test[i]-1]+=1
                    Test_Histogram=np.append(Test_Histogram,LabelHistogram)
                    Result=clf.predict(LabelHistogram)
                    print "Object class is: ", Result
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(frame,"Person",(y/4,x/2), font, 1,(0,255,0),2)
                    #cv2.imwrite(NewPath,crop_img)
                TemplateCount += 1
                cv2.imwrite("Frames/%d.jpg" % Finalcount, frame)           # save frame as JPEG file
                Finalcount += 1

            #cv2.imwrite("Frames/%d.jpg" % Finalcount, frame)           # save frame as JPEG file
            Finalcount += 1
            success,frame = cap.read(cv.CV_IMWRITE_JPEG_QUALITY)
            i+=1

        cv2.destroyAllWindows()
        self.writeVideo()
        

if __name__ == "__main__": 
    path_file='video.avi'
    v = video(path_file)

