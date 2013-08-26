__author__ = 'johnnymo87'
from ApexScrape import *
from datetime import timedelta
import string


class Locations(object):

    def __init__(self, login, customers=(), dates=(), time=''):
        """datetime format: mm/dd/YYYY HH:MM:SS (24 hour)"""
        self.branch = Apex(login)
        self.dates = dates
        self.time = time
        if time:
            stamp = "{} {}".format(dates[0], time)
            self.stamp = datetime.strptime(stamp, "%m/%d/%Y %H:%M:%S")
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
        # Not DRY, don't care right now
        if self.time:
            # use usage summary for all days except first day
            second_day = self.stamp + timedelta(days=1)
            second_day = self.stamp.strftime("%m/%d/%Y")
            for cust in self.devices:
                for d in self.devices[cust]:
                    self.reports[d] = []
                    summary = self.branch.getUsage(d, second_day, self.dates[1])
                    for line in summary:
                        if 'productNum1' in line.keys():  # offline vends may leave blanks, ignored by vending tab.
                            self.reports[d].append(
                                (line['productNum1'], int(line['packageQty']) * int(line['qtyDispensed']))
                            )
            # use transaction detail for first day, only append records after stamp
            report = []
            for cust in self.devices:
                for d in self.devices[cust]:
                    report = self.branch.getReport(d, self.dates[0], self.dates[0])
                    print 'Looking for records after ' + self.time
                    for r in report:
                        # r = (datetime, SKU, QTY)
                        if r[0] >= self.stamp:
                            record = (r[1], r[2])
                            self.reports[d].append(record)
        elif self.dates:
            assert len(self.dates[0]) == 10 and len(self.dates[1]) == 10
            for cust in self.devices:
                for d in self.devices[cust]:
                    self.reports[d] = []
                    summary = self.branch.getUsage(d, self.dates[0], self.dates[1])
                    for line in summary:
                        if 'productNum1' in line.keys():  # offline vends may leave blanks, ignored by vending tab.
                            self.reports[d].append(
                                (line['productNum1'], int(line['packageQty']) * int(line['qtyDispensed']))
                            )

    def write(self, filename, device):
        with open(filename + '.txt', 'w') as f:
            for SKU in self.coils[device]:
                if '[' in SKU:
                    QTY = self.coils[device][SKU]['QTY']
                    SKU = re.search('[\d\w-]+', SKU).group()
                    f.write('{}\t{}\n'.format(SKU, QTY))
                elif self.coils[device][SKU]['QTY'] > 0:
                    f.write('{}\t{}\n'.format(SKU, self.coils[device][SKU]['QTY']))
            if self.reports:
                for line in self.reports[device]:
                    if '[' in line[0]:
                        new_SKU = re.search('[\d\w-]+', line[0]).group()
                        line = (new_SKU, line[1]) # 'tuple' object does not support item assignment, must overwite
                    f.write('{}\t{}\n'.format(line[0], line[1]))

if __name__ == '__main__':
    # Locations(('JohnJernigan', 'password'), customers=('auto',))
    Locations(('FastenalFLPER', 'fastenal3'), customers=('chemring',), dates=('08/19/2013', '08/26/2013'), time='09:57:00')
    # Locations(('FastenalFLPER', 'fastenal3'), customers=('aluminum',), dates=('07/31/2013', '08/26/2013'))
