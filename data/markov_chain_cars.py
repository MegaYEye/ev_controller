import numpy as np
from scipy import interp
from scipy.interpolate import RegularGridInterpolator
import matplotlib.pyplot as plt
import time
import sqlite3
import itertools
import pandas as pd
from scipy.interpolate import interp1d
import mpl_toolkits.mplot3d.axes3d as p3

horizon = 48
num_interp = 2

data_ev = pd.read_csv('/Users/mathildebadoual/code/ev_controller/data/EV_data.csv')
ID_26 = data_ev['ID:26']     #Car_ID:26
ID_370 = data_ev['ID:370']   #Car_ID:370
ID_545 = data_ev['ID:545']   #Car_ID:545
ID_661 = data_ev['ID:661']   #Car_ID:661
ID_4767 = data_ev['ID:4767'] #Car_ID:4767

#Creating and resizing EV_array into (ID , Week, DOW, HOD)
ev_array = np.array([ID_26, ID_370, ID_545, ID_661, ID_4767])
ev_array.resize(5,47,7,24)

p_list =[ ]  #initializing list containing the probability matrices
for k in range(23):  # 23 cuz probability doesn't count for last timestep
    Num_charging = [0, 0, 0]     #[num_charging now, num_STILL charging at k+1, num_n0t charging at k+1]
    Num_not_charging = [0, 0, 0] #[num_not charging now, num_charging next k, num STILL not charging next k]
    for j in range(47):
        for v in range(7):
            if any(i >= 0.3 for i in ev_array[:,j,v,k]): #I use 0.3 as charging benchmark
                Num_charging[0] += 1
                if any(i >= 0.3 for i in ev_array[:,j,v,k+1]):
                    Num_charging[1] += 1
                else:
                    Num_charging[2] += 1
            else:
                Num_not_charging[0] += 1
                if any(i >= 0.3 for i in ev_array[:,j,v,k+1]):
                    Num_not_charging[1] += 1
                else:
                    Num_not_charging[2] += 1
    p_ij = np.zeros((2,2))
    p_ij[0,0] = Num_charging[1]/Num_charging[0]  #probability of moving from i to i
    p_ij[0,1] = Num_charging[2]/Num_charging[0]  #probability of moving from i to j
    p_ij[1,0] = Num_not_charging[1]/Num_not_charging[0]
    p_ij[1,1] = Num_not_charging[2]/Num_not_charging[0]
    p_list.append(p_ij)

P = np.array(p_list)

imagelist = [P[k, :, :] for k in range(23)]

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

X, Y = np.meshgrid(range(num_interp), range(num_interp))
X = X.flatten('F')
Y = Y.flatten('F')
Z = np.zeros_like(X)

dx = 0.5 * np.ones_like(Z)
dy = dx.copy()

# make axesimage object
# the vmin and vmax here are very important to get the color map correct
#im = plt.imshow(imagelist[0], cmap=plt.get_cmap('Reds'))

im = ax.bar3d(X, Y, Z, dx, dy, imagelist[0].flatten())

row_names = ['', '0', '', '', '', '', '1', '']
column_names = ['', '0', '', '', '', '', '1', '']

# function to update figure
def updatefig(j):
    ax.cla()
    ax.set_zlim(0, 1)
    # set the data in the axesimage object
    im = ax.bar3d(X, Y, Z, dx, dy, imagelist[j].flatten())
    ax.w_yaxis.set_ticklabels(row_names)
    ax.w_xaxis.set_ticklabels(column_names)
    ax.set_xlabel('Past state')
    ax.set_ylabel('Next state')
    ax.set_zlabel('Probability')
    ax.set_title('Probability of moving from one state to another at hour : ' + str(j) + ' of the day')
    # return the artists set
    return [im]
# kick off the animation

ani = animation.FuncAnimation(fig, updatefig, frames=range(23),
                              interval=1000)
ani.save('/Users/mathildebadoual/code/ev_controller/report/cars.mp4', writer='ffmpeg')
