import numpy as np
from scipy.stats import multivariate_normal as mvn, cauchy
import matplotlib.pylab as plt
np.set_printoptions(precision=3)

import sys
sys.path.append('./../utils')
from utils.cartesian_polar_calc import *

class polar_radar():
    def __init__(self, seed=123, ndat=100, q=.5, r=3.):
        self.ndat = ndat
        self.seed = seed
        self.q = q
        self.dt = 1
        self.r = r
        self.A = np.array([[1, 0, self.dt, 0],
                           [0, 1, 0, self.dt],
                           [0, 0, 1,  0],
                           [0, 0, 0,  1]])
        self.Q = self.q**2 * np.array([[self.dt**3/3, 0      , self.dt**2/2, 0      ],
                                      [0,       self.dt**3/3, 0,       self.dt**2/2],
                                      [self.dt**2/2, 0,       self.dt,      0      ],
                                      [0,       self.dt**2/2, 0,       self.dt     ]])
        self.H = cartesian_to_polar
        self.R = self.r**2 *  np.array([[0.01, 0.0,    0.0 ],  # 0.09, 0,      0,
                                        [0.0,  0.0001, 0.0 ],  # 0,    0.0009, 0
                                        [0.0,  0.0,    0.01]]) # 0,    0,      0.09
        
    def generate_x(self, x_0):
        # np.random.seed(self.seed)

        X = np.zeros(shape=(self.ndat, self.A.shape[0]))
        X[0]=x_0
        x = np.array(x_0)
        for t in range(1, self.ndat):
            x = self.A.dot(x) + mvn.rvs(cov=self.Q)
            X[t] = x
        return X
    
    def generate_y(self, X, noisedist='Cauchy', log=False):
        # np.random.seed(self.seed)
        if log:
            print('Measurement noise: {0}'.format(noisedist))

        if noisedist == 'normal':
            noise = mvn.rvs(cov=self.R, size=len(X))
        elif noisedist == 'Cauchy':
            # rho, phi, drho = y
            noise_rho = cauchy.rvs(scale=self.r * 0.01, size=self.ndat)
            noise_phi = cauchy.rvs(scale=self.r * 0.0001, size=self.ndat)
            noise_drho = cauchy.rvs(scale=self.r * 0.01, size=self.ndat)
            
            noise = np.array([[noise_rho[i], noise_phi[i], noise_drho[i]] for i in range(self.ndat)])

        Y = np.zeros(shape=(self.ndat, 3))
        
        for t, x in enumerate(X[:]):
            y = self.H(x) + noise[t]
            Y[t] = y
        return [Y, noise]

    def plot_generated_data(self,X, Y):
        plt.figure(1,figsize=(14,7))
        
        # convert polar measurement values to cartiasian coordinates
        Y_cartesian = np.array([polar_to_cartesian(polar_coordinate) for polar_coordinate in Y])
        
        plt.plot(Y_cartesian[:,0], Y_cartesian[:,1], '+', label=r'$y$ - radar measurement')
        plt.plot(X[:,0], X[:,1])

        plt.figure(2, figsize=(14,4))
        plt.subplot(1,2,1)
        plt.plot(X[:,2])    
        plt.subplot(1,2,2)
        plt.plot(X[:,3])
        plt.show()

    def save_data(self, data):
        np.save('./models/data/prm_data.npy', data)
    
    def load_data(self):
        return np.load('./models/data/prm_data.npy')
    
    def save_mse_finals(self, mse_finals, suffix=''):
        np.save(f'./models/mse_finals/prm_mse_finals_{suffix}.npy', mse_finals)
    
    def load_mse_finals(self, mse_finals, suffix=''):
        return np.load(f'./models/mse_finals/prm_mse_finals_{suffix}.npy')