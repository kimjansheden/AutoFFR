from scraper import GetPrices
from enum import Enum

class Of(Enum):
    FFR=1,
    ACF=2

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class Source(Enum):
    mgex=1

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


print(Of.FFR)
ffr = GetPrices(Of.FFR, source=Source.mgex)

ffr.start()
