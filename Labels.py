__author__ = 'johnnymo87'
from ApexScrape import *
import string

class Labels(Apex):

    def __init__(self, (username, password), customer):
        Apex.__init__(self, (username, password))
        self.target = customer
        self.assembleDevices()
        # for dev in self.devices:
        #     data = self.getCoils(dev)
        #     filename = "{} {} {}".format(customer, dev, self.devices[dev][2])
        #     self.output(filename, data, 'w')

    def assembleDevices(self):
        for cust in self.customers:
            if string.lower(self.target) in string.lower(cust):
                self.target = cust
                break
        else:
            raise LookupError(self.target, 'not found!')
        self.getDevices(self.target)

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
                parts.append((position, SKU, description))
            else:
                print 'Data missing from position ' + str(int(float(row.contents[1].contents[0])))
        for i in range(lockers):
            row = soup.find('tr', {'id': 'lockerTr'+str(i)})
            if row.contents[5].contents[1].contents:
                position = str(int(float(row.contents[1].contents[0])))
                description = str(self.html_parser.unescape(row.contents[3].contents[0].strip()))
                SKU = re.search('[\d\w\[\]-]+', str(row.contents[5].contents[1].contents[0].strip())).group()
                parts.append((position, SKU, description))
            else:
                print 'Data missing from position ' + str(int(float(row.contents[1].contents[0])))
        return parts


def output(self, filename, data, write_mode):
    with open(filename + '.txt', write_mode) as f:
        for line in data:
            f.write('{}\t{}\t{}\n'.format(line[0], line[1], line[2]))



if __name__ == '__main__':
    #LABELS
    login = ('SteveMcMillen', 'password')
    customer = 'closet'
    labels = Labels(login, customer)
    for dev in labels.devices:
        data = labels.getCoils(dev)
        with open(customer + ' ' + dev + '.txt', 'w') as quote:
            for line in data:
                quote.write('{}\t{}\t{}\n'.format(line[0], line[1], line[2]))
    #QUOTE
##    login = ('FLGANStore', 'password')
##    customer = 'boone'
##    labels = Labels(login, customer)
##    for dev in labels.devices:
##        data = labels.getCoils(dev)
##        with open(customer + ' ' + dev + '.txt', 'w') as quote:
##            for line in data:
##                quote.write('{}\t{}\n'.format(line[1], '1'))
