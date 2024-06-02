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