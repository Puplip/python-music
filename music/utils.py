

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
                self.i += self.step
                return self.i
            else:
                self.finished = True
                return StopIteration()
        else:
            if self.i > self.stop:
                self.i += self.step
                return self.i
            else:
                self.finished = True
                return StopIteration()

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
            out.append(NoneList(dims[1:]))
    else:
        for i in range(dims[0]):
            out.append(0)
    return out