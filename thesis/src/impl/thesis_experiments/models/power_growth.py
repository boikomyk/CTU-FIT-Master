import numpy as np
from scipy.stats import norm, cauchy
import matplotlib.pylab as plt

class power_growth():
    def __init__(self, sigma_xi, sigma_zeta, sigma_epsilon, rho, k, ndat=500):
        self.sigma_xi = sigma_xi
        self.sigma_zeta = sigma_zeta
        self.sigma_epsilon = sigma_epsilon
        self.rho = rho
        self.k = k
        self.ndat = ndat
    
    
    def generate_x(self, x_0):
        X = np.zeros((self.ndat,2))
        X[0]=x_0

        for t in range(1, self.ndat):
            mu_prev = X[t-1][0]
            nu_prev = X[t-1][1]

            nu_t = self.rho * nu_prev + norm.rvs(scale=self.sigma_zeta)
            mu_t = mu_prev**(1+nu_prev) + norm.rvs(scale=self.sigma_xi)

            X[t]=[mu_t,nu_t]

            if mu_t < 0:
                break    
        return X


    def generate_y(self, X, noisedist='Cauchy', log=False):
        if log:
            print('Measurement noise: {0}'.format(noisedist))

        if noisedist == 'normal':
            noise = np.random.normal(scale=self.sigma_epsilon, size=len(X))
        elif noisedist == 'Cauchy':
            #noise = np.random.standard_cauchy(size=len(X))
            noise = cauchy.rvs(scale=self.sigma_epsilon, size=self.ndat)

        Y = np.zeros(self.ndat)
        for t, mu in enumerate(X[:,0]):
            Y[t]= self.k + mu + noise[t]
            if mu < 0:
                break

        return [Y, noise]

    def plot_generated_data(self,X, Y):
        mu = X[:,0]
        nu = X[:,1]

        plt.figure(figsize=(10,10))
        plt.subplot(3,1,1)
        plt.plot(mu, label=r'$mu_t$')
        plt.legend()

        plt.subplot(3,1,2)
        plt.plot(Y, label=r'$y_t$')
        plt.legend()

        plt.subplot(3,1,3)
        plt.plot(1+nu, label=r'$1+\nu_t$')
        plt.axhline(1, color='red')
        plt.legend()
        plt.show()

    def save_data(self, data):
        np.save('./models/data/pgm_data.npy', data)
    
    def load_data(self):
        return np.load('./models/data/pgm_data.npy')
    
    def save_mse_finals(self, mse_finals, suffix=''):
        np.save(f'./models/mse_finals/pgm_mse_finals_{suffix}.npy', mse_finals)
    
    def load_mse_finals(self, mse_finals, suffix=''):
        return np.load(f'./models/mse_finals/pgm_mse_finals_{suffix}.npy')