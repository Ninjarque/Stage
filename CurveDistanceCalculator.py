import numpy as np

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
        # Determine the number of points to interpolate
        if len(x1) > len(x2):
            indexes_count = len(x1)
        else:
            indexes_count = len(x2)
        
        # Generate common x-values using linspace
        x_common = np.linspace(min(x1[0], x2[0]), max(x1[-1], x2[-1]), indexes_count)
        
        # Interpolate y-values for both curves
        y1_interp = np.interp(x_common, x1, y1)
        y2_interp = np.interp(x_common, x2, y2)
        
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
        print(y1_interp, y2_interp)
        
        # Calculate RMSE
        mse = np.mean((y1_interp - y2_interp) ** 2)
        rmse = np.sqrt(mse)
        
        return rmse
