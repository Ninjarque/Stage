import numpy as np
from scipy.interpolate import interp1d

class CurveDistanceCalculator:
    @staticmethod
    def interpolate_curve(x1, y1, x2, y2):
        """
        Interpolate one of the curves so that both curves have the same x-values.
        
        Parameters:
        - x1, y1: Arrays representing the x and y coordinates of the first curve.
        - x2, y2: Arrays representing the x and y coordinates of the second curve.
        
        Returns:
        - x_common: The common x-values for both curves.
        - y1_interp: The y-values of the first curve after interpolation (if needed).
        - y2_interp: The y-values of the second curve after interpolation (if needed).
        """
        if len(x1) > len(x2):
            x_common = x1
            y2_interp = interp1d(x2, y2, kind='linear', fill_value='extrapolate')(x_common)
            y1_interp = y1
        else:
            x_common = x2
            y1_interp = interp1d(x1, y1, kind='linear', fill_value='extrapolate')(x_common)
            y2_interp = y2
        
        return x_common, y1_interp, y2_interp
    
    @staticmethod
    def calculate_rmse(x1, y1, x2, y2):
        """
        Calculate the RMSE (Root Mean Square Error) between two curves.
        
        Parameters:
        - x1, y1: Arrays representing the x and y coordinates of the first curve.
        - x2, y2: Arrays representing the x and y coordinates of the second curve.
        
        Returns:
        - The RMSE value.
        """
        x_common, y1_interp, y2_interp = CurveDistanceCalculator.interpolate_curve(x1, y1, x2, y2)
        
        # Calculate RMSE
        mse = np.mean((y1_interp - y2_interp) ** 2)
        rmse = np.sqrt(mse)
        
        return rmse
