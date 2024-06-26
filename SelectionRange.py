class SelectionRange:
    def __init__(self, start_index, start_pos, end_index, end_pos):
        self.start_index = start_index
        self.end_index = end_index
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.auto_correct()

    def contains(self, index):
        return self.start_index == index or self.end_index == index
    def other_index(self, index):
        if self.contains(index):
            if index == self.start_index:
                return self.end_index
            else:
                return self.start_index
        return -1

    def auto_correct(self):
        if not self.start_pos or not self.end_pos:
            return -1
        if self.start_pos > self.end_pos:
            dt_index = self.start_index
            self.start_index = self.end_index
            self.end_index = dt_index
            dt_pos = self.start_pos
            self.start_pos = self.end_pos
            self.end_pos = dt_pos
        return 0

    def resolve(self, other_range):
        r = self.auto_correct()
        r2 = other_range.auto_correct()
        if r == -1 or r2 == -1:
            return
        if self.start_pos < other_range.start_pos and other_range.end_pos < self.end_pos:
            dt_index = self.end_index
            self.end_index = other_range.end_index
            other_range.end_index = dt_index
            dt_pos = self.end_pos
            self.end_pos = other_range.end_pos
            other_range.end_pos = dt_pos

            dt_index = self.end_index
            self.end_index = other_range.start_index
            other_range.start_index = dt_index
            dt_pos = self.end_pos
            self.end_pos = other_range.start_pos
            other_range.start_pos = dt_pos
            return
        if self.start_pos < other_range.start_pos and other_range.start_pos < self.end_pos:
            dt_index = other_range.start_index
            other_range.start_index = self.end_index
            self.end_index = dt_index
            dt_pos = other_range.start_pos
            other_range.start_pos = self.end_pos
            self.end_pos = dt_pos
            return
        if self.start_pos < other_range.end_pos and other_range.end_pos < self.end_pos:
            dt_index = self.start_index
            self.start_index = other_range.end_index
            other_range.end_index = dt_index
            dt_pos = self.start_pos
            self.start_pos = other_range.end_pos
            other_range.end_pos = dt_pos
            return
        
    def to_dict(self):
        properties = {
            "start_index": self.start_index,
            "end_index": self.end_index,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
        }
        return properties

    @classmethod
    def from_dict(cls, data):
        #print("selection data", data)
        r = cls(0, 0, 0, 0)
        r.start_index = int(data.get("start_index", 0))
        r.end_index = int(data.get("end_index", -1))
        r.start_pos = float(data.get("start_pos", 0))
        r.end_pos = float(data.get("end_pos", 0))
        return r