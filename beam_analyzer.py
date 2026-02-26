import cv2
import os
import glob
import numpy as np
import math

class BeamAnalyzer:
    def __init__(self,folder_path):
        self.folder_path = folder_path
        self.results = []
        self.file_list = []
    def find_images(self):
        search_path = os.path.join(self.folder_path,"*.tif")
        self.file_list = glob.glob(search_path)
        print(f"Found {len(self.file_list)} images.")
    def process_beams(self):
        for file_path in self.file_list:
            img = cv2.imread(file_path, 0 ) # 1. Load the image in grayscale
            blurred = cv2.GaussianBlur(img, (5, 5), 0)

            # 3. Automatic Thresholding (Otsu's Method)
            # This finds the best "cut-off" point between beam and background
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # 4. Find the outlines (contours)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                # 5. Pick the LARGEST white shape (The Beam)
                largest_contour = max(contours, key=cv2.contourArea)

                # 6. Fit the minimum enclosing circle
                (x, y), radius = cv2.minEnclosingCircle(largest_contour)

                self.results.append({"filename":os.path.basename(file_path),
                                     "center":(float(x),float(y)),
                                     "radius": float(radius)
                                     })
            else:
                print(f"No Circle found in: {os.path.basename(file_path)}")
   
    def save_visuals(self):
        output_folder=os.path.join(self.folder_path,"processed_results") # Create a "results" folder inside your image folder
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"Created Folder :{output_folder}")
        for res in self.results:
            img_path = os.path.join(self.folder_path,res['filename']) # Load the original image again to draw on it
            img = cv2.imread(img_path,1)#load it in color (1) so we can draw a RED circle

            center_x=int(res['center'][0])
            center_y=int(res['center'][1])
            radius=int(res['radius'])

            cv2.circle(img,(center_x,center_y),radius,(0,0,255),2) #Draw the Outer Circle
            cv2.circle(img, (center_x, center_y), 3, (0, 0, 255), 2) #Draw the Center Dot

            save_path=os.path.join(output_folder,f"check_{res['filename']}")
            cv2.imwrite(save_path,img)
        print(f'Processed Images Saved')
    
    def analyze_groups(self,radius_threshold):

        self.masterx = {}
        self.mastery = {}
        self.masterR = {}

        Group_Z1=[res for res in self.results if res['radius']<radius_threshold] #Split  results into two groups based on a radius size
        Group_Z2=[res for res in self.results if res['radius']>radius_threshold]

        for i, group in enumerate([Group_Z1,Group_Z2],1):
            if len(group) <3:
                print(f"Group{i} has too few point to fit a circle")
                continue

            points=np.array([res['center'] for res in group], dtype=np.float32)

            (mx,my),m_radius=cv2.minEnclosingCircle(points)
            self.masterx[i]=mx
            self.mastery[i]=my
            self.masterR[i]=m_radius

            print(f"\n--- Group {i} Analysis ({len(group)} images) ---")
            print(f"Master Center: ({mx:.2f}, {my:.2f})")
            print(f"Master Radius (Spread): {m_radius:.2f}")


    def Pointing(self,radius_threshold):
        self.rel_x={}
        self.rel_y={}
        self.rel_r={}
        self.rel_theta={}

        self.alpha=0
        self.beta=0
        self.gamma=0
        self.delta=0

        sum_theta1 = 0
        sum_theta2 = 0

        self.beta=(self.masterR[2]-self.masterR[1])/15


        for res in self.results:

            name = res['filename']
            if res['radius']<radius_threshold:
                group_id=1
            else:
                group_id=2

            mx=self.masterx[group_id]#the Master Center for THIS specific group
            my=self.mastery[group_id]

            x, y = res['center']

            dx=x-mx
            dy=y-my

            r_local=math.sqrt(dx**2+dy**2)
            theta_rad=math.atan2(dy,dx)

            # --- ADD TO SUMS ---
            if group_id == 1:
                sum_theta1 += theta_rad
            else:
                sum_theta2 += theta_rad


            self.rel_x[name] = dx
            self.rel_y[name] = dy
            self.rel_r[name] = r_local
            self.rel_theta[name] = theta_rad

            print(f"File: {name}")
            print(f"  rel_x: {dx}")
            print(f"  rel_y: {dy}")
            print(f"  rel_r: {r_local}")
            print(f"  rel_theta: {theta_rad}")


        # Calculate the final difference (Sum G1 - Sum G2)
        self.theta_diff = sum_theta1 - sum_theta2

        d=self.masterR[1]*self.theta_diff

        self.gamma=d/15

        self.delta=math.sqrt(self.gamma**2+self.beta**2)

        print(f'Beta= {self.beta}')
        print(f'Gamma={self.gamma}')
        print(f'Delta= {self.delta}')



