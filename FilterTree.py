from filter import *
from loader import *

class FilterTree:
    def __init__(self, filter, leftTree, rightTree):
        self.filter = filter
        self.leftTree = leftTree
        self.rightTree = rightTree
        self.curves = []

    def __init__(self, curves):
        self.filter = None
        self.leftTree = None
        self.rightTree = None
        self.curves = curves

    def has_childs(self):
        return self.rightTree and self.leftTree
    
    def match(self, curvex, curvey):
        if not self.has_childs():
            return curvex, curvey
        
        valid, curvex, curvey = self.filter.apply(curvex, curvey)
        if valid:
            return self.leftTree.match(curvex, curvey)
        return self.rightTree.match(curvex, curvey)
    
def build(target_clusters, filterMakerFunction):
    


    return Filter()
    
