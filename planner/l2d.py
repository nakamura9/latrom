class List2D(list):
    def __init__(self, *args, **kwargs):
        super(List2D, self).__init__(*args, **kwargs)
        self.is_flattened = False
    def flatten(self):
        res = []
        if self.is_flattened:
            return self
        for row in self:
            for i in row:
                res.append(i)
        self = res
        return res
    
    def reshape(self, shape):
        i = 0
        res = []
        for row in range(shape[0]):
            res.append(self[i * shape[1]: (1 + i) * shape[1]])
            i += 1
        return res

    @property
    def shape(self):
        if isinstance(self[0], list):
            return(len(self), len(self[0]))
        return len(self),
