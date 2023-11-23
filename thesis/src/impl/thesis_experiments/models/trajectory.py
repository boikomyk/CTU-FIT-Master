import numpy as np
from scipy.stats import multivariate_normal as mvn, cauchy
import matplotlib.pylab as plt
np.set_printoptions(precision=3)

class trajectory():
    
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
        self.H = np.array([[1., 0, 0, 0],
                           [0., 1, 0, 0]])
        self.R = self.r**2 * np.eye(2)
        
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
            noise = cauchy.rvs(scale=self.r, size=(self.ndat,self.H.shape[0]))

        Y = np.zeros(shape=(self.ndat, self.H.shape[0]))
        
        for t, x in enumerate(X[:]):
            y = self.H.dot(x) + noise[t]
            Y[t] = y
        return [Y, noise]

    def plot_generated_data(self,X, Y):
        plt.figure(1,figsize=(14,7))
        plt.plot(Y[:,0], Y[:,1], '+')
        plt.plot(X[:,0], X[:,1])

        plt.figure(2, figsize=(14,4))
        plt.subplot(1,2,1)
        plt.plot(X[:,2])    
        plt.subplot(1,2,2)
        plt.plot(X[:,3])
        plt.show()

    def save_data(self, data):
        np.save('./models/data/cvm_data.npy', data)
    
    def load_data(self):
        return np.load('./models/data/cvm_data.npy')
    
    def save_mse_finals(self, mse_finals, suffix=''):
        np.save(f'./models/mse_finals/cvm_mse_finals_{suffix}.npy', mse_finals)
    
    def load_mse_finals(self, mse_finals, suffix=''):
        return np.load(f'./models/mse_finals/cvm_mse_finals_{suffix}.npy')