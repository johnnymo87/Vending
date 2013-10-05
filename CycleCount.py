from ApexScrape import *
import string

class CycleCount(Apex):

    def __init__(self, ((username, password)), customer, cc_file):
        Apex.__init__(self, (username, password))
        self.target = customer
        self.target = self.find_target()
        self.PkgQty = self.getPkgQty(self.target)
        self.cc_file = cc_file
        self.process()

    def find_target(self):
        for c in self.customers.keys():
            if string.lower(self.target) in string.lower(c):
                return self.customers[c]
        else:
            raise LookupError(self.target, 'not found!')
        
    def process(self):
        with open(self.cc_file, 'r') as f:
            records = [line.strip().split('\t') for line in f]
        with open('processed_' + self.cc_file, 'w') as f:
            for r in records:
                SKU, QTY = r[0], abs(int(r[1]))
                QTY *= self.PkgQty[SKU]
                SKU = re.search('[\d\w\[\]-]+', SKU).group() # remove bracketed additions
                f.write('{}\t{}\n'.format(SKU, QTY))


if __name__ == '__main__':
    CycleCount(('SantosBaez1', 'fastenal'), 'spx', 'SPX_cycle.txt')
