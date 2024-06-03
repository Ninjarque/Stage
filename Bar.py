class Bar:
    i = 0
    x = 0
    y = 1.0

    id = []

    def __init__(self, i, x, y = 1.0, id = []):
        self.i = i
        self.x = x
        self.y = y
        self.id = id

    def link(bar1, bar2):
        if not bar1 or not bar2:
            return
        print("Assigning ID to bar x:", bar2.x, "from:{", bar2.id, "} to:{", bar1.id, "}")
        bar2.id = bar1.id