__author__ = 'johnnymo87'
from ApexScrape import *
import string

class Cross(Apex):

    def __init__(self, (username, password), customer=()):
        Apex.__init__(self, (username, password))
        if customer:
            self.target = customer
        else:
            self.target = self.customers.keys()
        self.assembleDevices()
        with open('thub.txt') as hub:
            lines = hub.readlines()
            self.THUB = [line.strip() for line in lines]
        for cust in self.target:
            for dev in self.devices[cust]:
                data = self.getCoils(dev)
                filename = "{} {} {}".format(cust, dev, self.devices[dev][2])
                self.output(filename, data)

    def assembleDevices(self):
        found = self.customers.keys()
        for cust in self.target:
            self.devices[cust] = []
            for f in found:
                if string.lower(cust) in string.lower(f):
                    valid = f
                    break
            else:
                raise LookupError(cust, 'not found!')
            self.devices[cust].extend(self.getDevices(valid))

    def getCoils(self, device):
        """Returns of list of tuples: (position, SKU, description), all derived from the device manager."""
        print 'Getting coils for', device
        parts = []
        params = OrderedDict((
            ('comId', self.devices[device][0]),
            ('siteId', self.devices[device][1]),
            ('requestId', self.devices[device][2])
        ))
        try:
            request = self.s.post("https://fastsolutions.mroadmin.com/Apex-Device/devicePOGAction_detailPOG.action", params=params)
        except:
            request = self.relog("https://fastsolutions.mroadmin.com/Apex-Device/devicePOGAction_detailPOG.action", params)
        soup = BeautifulSoup.BeautifulSoup(request.content)
        self.branch = str(soup.find('div', {'id': 'head_company_name'}).contents[0][-5:])
        coils = int(soup.find('input', {'id': 'deviceBinCount'})['value'])
        lockers = int(soup.find('input', {'id': 'lockersCount'})['value'])
        for i in range(coils):
            row = soup.find('tr', {'id': 'tr'+str(i)})
            if row.contents[5].contents[1].contents:
                position = str(int(float(row.contents[1].contents[0])))
                description = str(self.html_parser.unescape(row.contents[3].contents[0].strip()))
                SKU = re.search('[\d\w\[\]-]+', str(row.contents[5].contents[1].contents[0].strip())).group()
                if SKU in self.THUB:
                    parts.append((position, SKU, description))
            else:
                print 'Data missing from position ' + str(int(float(row.contents[1].contents[0])))
        for i in range(lockers):
            row = soup.find('tr', {'id': 'lockerTr'+str(i)})
            if row.contents[5].contents[1].contents:
                position = str(int(float(row.contents[1].contents[0])))
                description = str(self.html_parser.unescape(row.contents[3].contents[0].strip()))
                SKU = re.search('[\d\w\[\]-]+', str(row.contents[5].contents[1].contents[0].strip())).group()
                if SKU in self.THUB:
                    parts.append((position, SKU, description))
            else:
                print 'Data missing from position ' + str(int(float(row.contents[1].contents[0])))
        return parts

    def output(self, filename, data):
        with open(filename + '.txt', 'w') as f:
            for line in data:
                f.write('{}\t{}\t{}\n'.format(line[0], line[1], line[2]))


if __name__ == '__main__':
    Cross(('JohnJernigan', 'password'),)
