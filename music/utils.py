

from typing import List


class RangeFloat():
    def __init__(self, start : float, stop : float, step : float):

        self.i = start
        self.stop = stop
        self.step = step
        self.finished = False
        

        assert step != 0.0, "step cannot be 0"

        self.up = self.step > 0

        if self.up:
            assert stop > start
        else:
            assert stop < start
        
    def __next__(self):
        if self.finished:
            raise Exception("__next__ called after end of itteration")
        if self.up:
            if self.i < self.stop:
                ret = self.i
                self.i += self.step
                return ret
            else:
                self.finished = True
                raise StopIteration
        else:
            if self.i > self.stop:
                ret = self.i
                self.i += self.step
                return ret
            else:
                self.finished = True
                raise StopIteration

    def __iter__(self):
        return self

def NoneList(dims : List[int]):
    out = list()
    if len(dims) > 1:
        for i in range(dims[0]):
            out.append(NoneList(dims[1:]))
    else:
        for i in range(dims[0]):
            out.append(None)
    return out

def ZeroList(dims : List[int]):
    out = list()
    if len(dims) > 1:
        for i in range(dims[0]):
            out.append(ZeroList(dims[1:]))
    else:
        for i in range(dims[0]):
            out.append(0)
    return out

class CacheDict(dict):
    def __init__(self, max_count : int):
        self.max_count = max_count
        self.dict = dict()
    def __contains__(self, x):
        return x in self.dict
    def __getitem__(self, x):
        return self.dict[x]
    def __setitem__(self, x, y):
        self.dict[x] = y
        if len(self.dict) > self.max_count:
            self.dict.pop(next(iter(self.dict)))
    
