import numpy as np

class AverageManager:
    count = 0
    maxCount = 0
    avg = 0
    lstAvg = 0
    outValues = [0]
    currentV = 0

    def __init__(self, contextSize):
        self.maxCount = contextSize
        self.outValues = [0] * self.maxCount

    def compute(self, newValue):
        self.currentV = (self.currentV + 1) % self.maxCount
        outV = (self.currentV - self.maxCount + 1) % self.maxCount
        self.count = min(self.count + 1, self.maxCount)
        self.avg = self.lstAvg + 1.0/self.count * (newValue - self.outValues[outV])
        self.lstAvg = self.avg
        self.outValues[outV] = newValue
        return self.avg
    
    @staticmethod
    def interpolate_with_precision(datax, datay, precision):
        # Ensure precision is between 0 and 1
        precision = max(0, min(1, precision))

        # Determine the window size based on precision
        window_size = int(len(datay) * (1 - precision)) or 1

        # Create a convolution kernel
        kernel = np.ones(window_size) / window_size

        # Pad datay to handle edge cases in convolution
        pad_size = window_size // 2
        padded_datay = np.pad(datay, (pad_size, pad_size), mode='edge')

        # Perform the convolution
        smoothed_datay = np.convolve(padded_datay, kernel, mode='valid')

        return datax, smoothed_datay