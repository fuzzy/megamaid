class Edict(dict):
    def __init__(self, **kwargs):
        dict.__init__(self)
        for key, value in kwargs.items():
            if type(value) is dict:
                dict.__setitem__(self, key, Edict(**value))
            else:
                dict.__setitem__(self, key, value)

    def __getattr__(self, key):
        return dict.__getitem__(self, key)

    def __setattr__(self, key, value):
        dict.__setitem__(self, key, value)
