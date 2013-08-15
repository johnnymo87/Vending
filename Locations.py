__author__ = 'johnnymo87'
from ApexScrape import *
import string


class Locations(object):

    def __init__(self, login, customers=(), dates=()):
        self.branch = Apex(login)
        self.dates = dates
        if customers:
            self.customers = customers
        else:
            self.customers = self.branch.customers.keys()
        self.devices = {}
        self.assembleDevices()
        self.coils = {}
        self.assembleCoils()
        self.reports = {}
        self.assembleUsage()
        for cust in self.customers:
            for d in self.devices[cust]:
                filename = "{} {} {}".format(cust, d, self.branch.devices[d][2])
                self.write(filename, d)

    def assembleDevices(self):
        found = self.branch.customers.keys()
        for c in self.customers:
            self.devices[c] = []
            for f in found:
                if string.lower(c) in string.lower(f):
                    self.devices[c].extend(self.branch.getDevices(f))
                    break
            else:
                raise LookupError(c, 'not found!')


    def assembleCoils(self):
        """Makes a dictionary of dictionaries"""
        for cust in self.devices:
            for d in self.devices[cust]:
                self.coils[d] = self.branch.getCoils(d)

    def assembleUsage(self):
        if self.dates:
            assert len(self.dates[0]) == 10 and len(self.dates[1]) == 10
            for cust in self.devices:
                for d in self.devices[cust]:
                    self.reports[d] = self.branch.getUsage(d, self.dates[0], self.dates[1])

    def write(self, filename, device):
        with open(filename + '.txt', 'w') as f:
            for SKU in self.coils[device]:
                if self.coils[device][SKU]['QTY'] > 0:
                    f.write('{}\t{}\n'.format(SKU, self.coils[device][SKU]['QTY']))
            if self.reports:
                for line in self.reports[device]:
                    if 'productNum1' in line.keys():  # offline vends may leave blanks, ignored by vending tab.
                        f.write('{}\t{}\n'.format(
                            line['productNum1'],
                            int(line['packageQty']) * int(line['qtyDispensed'])
                        ))

if __name__ == '__main__':
    # Locations(('STOREFLJA5', 'password'))
    Locations(('FastenalFLPER', 'fastenal3'), dates=('07/23/2013', '08/15/2013'), customers=('chemring',))
    # Locations(('FastenalFLPER', 'fastenal3'), dates=('06/27/2013', '07/30/2013'))
