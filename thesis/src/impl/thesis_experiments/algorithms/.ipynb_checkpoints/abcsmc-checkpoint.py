#### imports
import numpy as np
import pylab as plt
from scipy.stats import norm, cauchy, multivariate_normal as mvn, uniform
from enum import Enum


############################################## Sequential Monte Carlo #####################################################
class smc:
    def __init__(self, sigma_x, nparticles=1000):
        self.particles = None                                           # Particles themselves
        self.nparticles = nparticles                                    # Number of particles
        self.weights = np.ones(self.nparticles) / self.nparticles       # Weights of particles
        self.sigma_x = sigma_x                                          # State noise std. dev.
        self.t = 0                                                      # Time step

        # loggers
        self.log_mean = []                                             # Logger the mean of X var evolution  
        self.log_ess = []                                              # Logger for eff. sample size

    def resample(self):
        """Multinomial resampling"""
        # resolve indexes        
        cumulative_sum = np.cumsum(self.weights)
        cumulative_sum[-1] = 1.
        indexes = np.searchsorted(cumulative_sum, np.random.random(self.nparticles))
    
        # resample according to indexes
        self.particles = self.particles[indexes]
        self.weights = np.ones(self.nparticles)
        self.normalize_weights()
            
    def normalize_weights(self):
        """Normalization of weights"""
        self.weights /= self.weights.sum()
        
    def _finish_update(self, new_logweights):
        """Finishes SMC updates. It's called with new_weights, raw unnormalized LOG weights (log-likelihoods...)"""
        wghts = np.log(self.weights) + new_logweights
        wghts -= wghts.max()
        self.weights = np.exp(wghts)
        self.normalize_weights()

        # log estimates
        dim = 1 if len(self.particles.shape) == 1 else len(self.particles[0])
        if dim > 1:
            self.log_mean.append([self.weights.dot(self.particles[:,i]) for i in range(dim)])
        else:
            self.log_mean.append(self.weights.dot(self.particles))

        self.t += 1
        ess = 1./np.sum(self.weights ** 2.)
        self.log_ess.append(ess)
        
    def smc_update(self):
        """SMC update. Method calculates new *raw* weights and calls _finish_update() to update the old ones and normalize!"""
        pass

    
    
############################################## Bootstrap Particle Filter (PF) ##############################################
class particlefilter(smc):
    def __init__(self, sigma_x, nparticles, sigma_y, log = False):
        """Constructor"""
        super().__init__(sigma_x, nparticles)
        self.sigma_y = sigma_y                                              # PF must know observ. noise standard dev.
        if log:
            print(f"PF filter init")
        
    def smc_update(self, y_true):
        """Particle filter measurement update"""
        means = self.simulate_y()
        
        if isinstance(self.sigma_y, (list, np.ndarray)):
            new_logweights = mvn.logpdf(means, y_true, self.sigma_y)
        else:
            new_logweights = norm.logpdf(means, loc=y_true, scale=self.sigma_y)                
        self._finish_update(new_logweights)    

        

        
############################################## ABC Kernels ##############################################
class Kernel:
    def __init__(self, p: float, nparticles: int, particles_in_ci: int):
        self.p = p
        self.scale = 1.0
        self.nparticles = nparticles
        self.particles_in_ci = particles_in_ci
    def tune_scale(self, last_particle_in_ci: float, u: np.ndarray, y_true: float):
        pass
    def evaluate_kernel(self, u: np.ndarray, y_true: float) -> np.ndarray:
        pass

## - Gaussian
class GaussianKernel(Kernel):
    """Gaussian kernel N(., epsilon^2)"""
    def tune_scale(self, last_particle_in_ci: float, u: np.ndarray, y_true: float):
        self.scale = np.abs(last_particle_in_ci - y_true)/norm.ppf(self.p)       # epsilon = st.dev.

    def evaluate_kernel(self, u: np.ndarray, y_true: float) -> np.ndarray:
        return norm.logpdf(x=u, loc=y_true, scale=self.scale)  # gaussian kernel is a normal pdf :)

## - Cauchy
class CauchyKernel(Kernel):
    def tune_scale(self, last_particle_in_ci: float, u: np.ndarray, y_true: float):
        self.scale = np.abs(last_particle_in_ci - y_true)/np.tan(np.pi * (self.p - .5))
    
    def evaluate_kernel(self, u: np.ndarray, y_true: float) -> np.ndarray:
        return cauchy.logpdf(x=u, loc=y_true, scale=self.scale)

## - Uniform
class UniformKernel(Kernel):
    def tune_scale(self, last_particle_in_ci: float, u: np.ndarray, y_true: float):
        self.scale = np.abs(last_particle_in_ci - y_true)/uniform.ppf(q=((self.p + 1) / 2))

    def evaluate_kernel(self, u: np.ndarray, y_true: float) -> np.ndarray:
        return uniform.logpdf(x=u, loc=y_true, scale=self.scale)

## - QuasiCauchy
class QuasiCauchyKernel(Kernel):
    """quasi-Cauchy kernel of Calvet&Czellar 2012, cf. Silverman."""
    def tune_scale(self, last_particle_in_ci: float, u: np.ndarray, y_true: float):
        sigma = u.std()
        self.scale = 1.06 * sigma * self.nparticles**(-.2)
    
    def evaluate_kernel(self, u: np.ndarray, y_true: float) -> np.ndarray:
        return norm.logpdf(x=u, loc=y_true, scale=self.scale)
    
## - JasraUniform
class JasraUniformKernel(Kernel):
    """Uniform kernel of Jasra 2012"""
    def tune_scale(self, last_particle_in_ci: float, u: np.ndarray, y_true: float):
        self.scale = 0

    def evaluate_kernel(self, u: np.ndarray, y_true: float) -> np.ndarray:
        dists = np.abs(u - y_true)
        ind_sorted = np.argsort(dists)
        
        new_weights = np.zeros(self.nparticles)
        new_weights[ind_sorted[:self.particles_in_ci]] = 1./self.particles_in_ci
        return new_weights 
    


################ related enums
class KernelTypes(Enum):
    Gaussian = 1
    Cauchy = 2
    Uniform = 3
    QuasiCauchy = 4
    JasraUniform = 5
     

def kernel_enums_to_kernel_classes_map(kernel_enum):
    if kernel_enum == KernelTypes.Cauchy:
        return CauchyKernel
    elif kernel_enum == KernelTypes.Uniform:
        return UniformKernel
    elif kernel_enum == KernelTypes.QuasiCauchy:
        return QuasiCauchyKernel
    elif kernel_enum == KernelTypes.JasraUniform:
        return JasraUniformKernel
    else:
        return GaussianKernel

############################################## ABC filter ##############################################
class abcsmc(smc):
    def __init__(self,
                 sigma_x,
                 nparticles,
                 particles_in_ci=300,
                 alpha=.95,
                 kernel_type: KernelTypes =KernelTypes.Gaussian, # Gaussian is default,
                 log = False
        ):
        """Constructor"""
        super().__init__(sigma_x, nparticles)
        self.p = alpha + .5*(1. - alpha)                                # CI is symmetric, 1/2 to each side
        self.log_epsilon = []                                           # Logger for epsilons (kernel scales)
        self.particles_in_ci = particles_in_ci
        self.alpha = alpha
        # init kernel
        self.kernel = kernel_enums_to_kernel_classes_map(kernel_type)(
            p=self.p,
            nparticles=self.nparticles,
            particles_in_ci=self.particles_in_ci,
        )
        if log:
            print(f"ABC filter with kernel '{kernel_type.name}' init")

    def get_last_particle_in_ci(self, u: np.ndarray, y_true: float):
        dists = np.abs(u - y_true)                                     # Calculate L1 distance of observations from y_true
        ind_sorted = np.argsort(dists)                                   # Sort particles distances
        ind_particle_last_in_ci = ind_sorted[self.particles_in_ci]       # Find index of the last particle in CI
        last_particle_in_ci = u[ind_particle_last_in_ci]               # Last particle in CI
        return last_particle_in_ci
    
    def smc_update(self, y_true):
        """Update of SMC filter"""
        
        # simulate pseudo-measurements
        u = self.simulate_y()
        
        measurement_dim = len(y_true) if hasattr(y_true, "__len__") else 1
        new_weights = np.zeros(self.nparticles)

        # multivariate
        if measurement_dim > 1:
            log_scales = []

            for d in range(measurement_dim):
                u_cur_dim = u[:,d]
                y_true_cur_dim = y_true[d]
                last_particle_in_ci = self.get_last_particle_in_ci(u_cur_dim, y_true_cur_dim)

                self.kernel.tune_scale(last_particle_in_ci, u_cur_dim, y_true_cur_dim)
                weights = self.kernel.evaluate_kernel(u_cur_dim, y_true_cur_dim)
                
                new_weights = np.sum([new_weights, weights], axis=0)
                log_scales.append(self.kernel.scale)
                
            self.log_epsilon.append(log_scales)

        # univariate
        else:
            last_particle_in_ci = self.get_last_particle_in_ci(u, y_true)
            self.kernel.tune_scale(last_particle_in_ci, u, y_true)
            new_weights = self.kernel.evaluate_kernel(u, y_true)

            self.log_epsilon.append(self.kernel.scale)

        self._finish_update(new_weights)        
