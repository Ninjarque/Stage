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
        if not bar1.id and bar2.id:
            id = bar2.id
            bar2.id = bar1.id
            bar1.id = id

        if len(bar1.id) >= 5:
            print("Edited an ID to add the MATCHER keyword")
            bar1.id = bar1.id[:6] + ["MATCHER"]
        print("Assigning ID to bar x:", bar2.x, "from:{", bar2.id, "} to:{", bar1.id, "}")
        bar2.id = bar1.id