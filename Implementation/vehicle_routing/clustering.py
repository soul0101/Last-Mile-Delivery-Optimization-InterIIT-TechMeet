import numpy as np
import copy
import math
def clustered(orders, depot, num_orders):
    shifted_lat = np.array([i.lat - depot.lat for i in orders])
    shifted_lon = np.array([i.lon - depot.lon for i in orders])
    polar_angles = (np.arctan2(shifted_lon,shifted_lat)*180/np.pi).tolist()

    for i in range(len(polar_angles)):
        if polar_angles[i] < 0:
            polar_angles[i]+=360

    orders = [order for _, order in sorted(zip(polar_angles, orders))]
    polar_angles = sorted(polar_angles)
  
    clusters_n = num_orders//500
    cluster = []
    min_spread = math.inf
    for angle in range(0, 360, 5):
        clusters_temp = []
        clusters_polar_temp = []
        
        if len([i for i in polar_angles if i>angle]) > 0:
            idx = polar_angles.index([i for i in polar_angles if i>angle][0])
            temp = orders[idx:] + orders[:idx]
            # print("temp", temp)
            temp_p = polar_angles[idx:] + polar_angles[:idx]
            for c in range(clusters_n):
                clusters_temp.append(temp[c*500: (c+1)*500])
                # print("cluster temp", clusters_temp)
                clusters_polar_temp.append(temp_p[c*500: (c+1)*500])
                # print(np.std(temp_p[c*clusters_n: (c+1)*clusters_n]))
            m = max([np.std(clusters_polar_temp[k]) for k in range(clusters_n)])
            if m < min_spread:
                min_spread = m
                cluster = copy.deepcopy(clusters_temp)
        else:
            break
    return cluster