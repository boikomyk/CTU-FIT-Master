import numpy as np

class mse:
    @staticmethod
    def calculate(prediction: np.ndarray, ground_truth: np.ndarray):
        ndat = len(prediction)
        return np.cumsum((prediction - ground_truth.flatten())**2.)/np.arange(1, ndat+1)
