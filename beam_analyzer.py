import cv2
import os
import glob
import numpy as np
import math

class BeamAnalyzer:
    def __init__(self, folder_path, pixel_size_mm=0.0055):
        self.folder_path = folder_path
        self.pixel_size_mm = pixel_size_mm
        self.results = []
        self.file_list = []
        # Define the filename sets for each group
        self.group1_names = ["A1.tif", "B1.tif", "C1.tif", "D1.tif"]
        self.group2_names = ["A2.tif", "B2.tif", "C2.tif", "D2.tif"]

    def find_images(self):
        search_path = os.path.join(self.folder_path, "*.tif")
        self.file_list = glob.glob(search_path)
        print(f"Found {len(self.file_list)} images.")

    def process_beams(self):
        for file_path in self.file_list:
            img = cv2.imread(file_path, 0)
            blurred = cv2.GaussianBlur(img, (11, 11), 0)
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                (x, y), radius = cv2.minEnclosingCircle(largest_contour)

                self.results.append({
                    "filename": os.path.basename(file_path),
                    "center": (float(x), float(y)),
                    "radius": float(radius)
                })
            else:
                print(f"No Circle found in: {os.path.basename(file_path)}")

    def save_visuals(self):
        output_folder = os.path.join(self.folder_path, "processed_results")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"Created Folder :{output_folder}")
        for res in self.results:
            img_path = os.path.join(self.folder_path, res['filename'])
            img = cv2.imread(img_path, 1)
            center_x = int(res['center'][0])
            center_y = int(res['center'][1])
            radius = int(res['radius'])
            cv2.circle(img, (center_x, center_y), radius, (0, 0, 255), 2)
            cv2.circle(img, (center_x, center_y), 3, (0, 0, 255), 2)
            save_path = os.path.join(output_folder, f"check_{res['filename']}")
            cv2.imwrite(save_path, img)
        print(f'Processed Images Saved')

    def analyze_groups(self): 
        self.masterx, self.mastery, self.masterR = {}, {}, {}
        
        # Grouping by filename
        Group_Z1 = [res for res in self.results if res['filename'] in self.group1_names]
        Group_Z2 = [res for res in self.results if res['filename'] in self.group2_names]

        for i, group in enumerate([Group_Z1, Group_Z2], 1):
            if len(group) < 3:
                print(f"Group{i} has too few points.")
                continue
            points = np.array([res['center'] for res in group], dtype=np.float32)
            (mx, my), m_radius = cv2.minEnclosingCircle(points)
            self.masterx[i], self.mastery[i], self.masterR[i] = mx, my, m_radius
            print(f"Group {i} Master Center: ({mx:.2f}, {my:.2f}), Radius: {m_radius:.2f}")

    def Pointing(self): 
        self.rel_x, self.rel_y, self.rel_r, self.rel_theta = {}, {}, {}, {}
        sum_theta1, sum_theta2 = 0, 0


        self.beta = ((self.masterR[2] - self.masterR[1]) * self.pixel_size_mm) / 15 *1000 #mrad

        for res in self.results:
            name = res['filename']
            group_id = 1 if name in self.group1_names else 2
            
            mx, my = self.masterx[group_id], self.mastery[group_id]
            x, y = res['center']
            dx, dy = x - mx, y - my
            r_local = math.sqrt(dx**2 + dy**2)
            theta_rad = math.atan2(dy, dx)*(-1)

            if group_id == 1: sum_theta1 += theta_rad
            else: sum_theta2 += theta_rad

            self.rel_x[name], self.rel_y[name] = dx, dy
            self.rel_r[name], self.rel_theta[name] = r_local, theta_rad

        self.theta_diff = (sum_theta1 - sum_theta2)/4
        
        # Fixed: Applied pixel size to group 1 master radius
        d = (self.masterR[1] * self.pixel_size_mm) * self.theta_diff
        self.gamma = d / 15 * 1000 #mrad
        self.delta = math.sqrt(self.gamma**2 + self.beta**2)

        print(f'Beta: {self.beta:.6f}, Gamma: {self.gamma:.6f}, Delta: {self.delta:.6f}')
