__author__ = 'johnnymo87'
import requests
import json
import BeautifulSoup
import re
from collections import OrderedDict
import HTMLParser


class Apex(object):

    def __init__(self, (username, password)):
        print username, password
        self.login = OrderedDict((('user.login_id', username), ('user.password', password)))
        self.s = requests.Session()
        self.s.post('https://fastsolutions.mroadmin.com/APEX-Login/account_login.action', data=self.login)
        self.branch = None
        self.comId = None
        self.customers = {}
        self.getCustomers()
        self.devices = {}
        self.html_parser = HTMLParser.HTMLParser()

    def relog(self, url, params):
        print 'relogging'
        self.s = requests.Session()
        self.s.post('https://fastsolutions.mroadmin.com/APEX-Login/account_login.action', data=self.login)
        # If at first you don't succeed ...
        while True:
            try:
                request = self.s.post(url, params=params)
            except:
                continue
            return request

    def getCustomers(self):
        print 'Getting customers'
        request = self.s.get("https://fastsolutions.mroadmin.com/Apex-Device/siteAction_viewSitesOwnedByMyCompany.action")
        data = request.content.split('|')
        machines = data[-2]
        output = json.loads(machines)
        self.comId = data[-1].strip()
        for o in output:
            self.customers[o['siteName']] = o['siteId']
        return self.customers.keys()

    def getDevices(self, customerName):
        print 'Getting devices for', customerName
        params = OrderedDict((
            ('actionSequence',20),
            ('requestId', self.customers[customerName]),
            ('comId', self.comId),
            ('newSortColumn',0),
            ('oldSortColumn',0),
            ('sortFlag','null'),
            ('sortCancel',0),
            ('siteType','owner')
        ))
        request = self.s.get("https://fastsolutions.mroadmin.com/Apex-Device/deviceBinAction_initDevicesList.action", params=params)
        data = request.content.split('|')
        machines = data[-2]
        output = json.loads(machines)
        names = []
        i = 2
        for o in output:
            if o['deviceName'] in self.devices:
                self.devices[o['deviceName'] + '.' + str(i)] = (self.comId, self.customers[customerName], o['deviceId'])
                names.append(o['deviceName'] + '.' + str(i))
                i += 1
            else:
                self.devices[o['deviceName']] = (self.comId, self.customers[customerName], o['deviceId'])
                names.append(o['deviceName'])
        return names

    def getPkgQty(self, device):
        print 'Getting package quantities for', device
        pkgQty = {}
        params = OrderedDict((
            ('page', 1),
            ('companyId', self.devices[device][0]),
            ('siteId', self.devices[device][1])
        ))
        request = self.s.get("https://fastsolutions.mroadmin.com/ProductManager/product_listSiteProductAjax.action", params=params)
        data = request.content.split('|')
        soup = BeautifulSoup.BeautifulSoup(data[0])
        total = int(re.search('(?<=Total:&nbsp;)[\d]+', str(soup.contents[1].contents[0].contents[0].contents[0])).group())
        if total % 20 != 0:
            page = [20 for i in range((total - total % 20) / 20)]
            page.append(total % 20)
        else:
            page = [20 for i in range((total - total % 20) / 20)]
        for lines in page:
            row = json.loads(data[-2])
            for j in range(lines):
                SKU = re.search('[\d\w\[\]-]+', str(row[j]['productNum1'])).group()
                pkg = int(row[j]['packageQty'])
                pkgQty[SKU] = pkg
            params['page'] += 1
            request = self.s.get("https://fastsolutions.mroadmin.com/ProductManager/product_listSiteProductAjax.action", params=params)
            data = request.content.split('|')
        return pkgQty

    def getCoils(self, device):
        pkgQty = self.getPkgQty(device)
        print 'Getting coils for', device
        parts = {}
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
            description = str(self.html_parser.unescape(row.contents[3].contents[0].strip()))
            if row.contents[5].contents[1].contents:
                SKU = re.search('[\d\w\[\]-]+', str(row.contents[5].contents[1].contents[0].strip()))
                QTY = re.search('[\d.]+', str(row.contents[7].contents[0]))
                MAX = re.search('[\d.]+', str(row.contents[11].contents[0]))
                MIN = re.search('[\d.]+', str(row.contents[13].contents[0]))
                SKU, QTY, MAX, MIN = SKU.group(), int(float(QTY.group())), int(float(MAX.group())), int(float(MIN.group()))
                QTY, MAX, MIN = map(lambda x: x * pkgQty[SKU], [QTY, MAX, MIN])
                if SKU in parts:
                    QTY, MAX, MIN = map(lambda x: x[1] + parts[SKU][x[0]], [('QTY', QTY), ('MAX', MAX), ('MIN', MIN)])
                parts[SKU] = {'description': description, 'QTY': QTY, 'MAX': MAX, 'MIN': MIN}
            else:
                print 'Data missing from position ' + str(int(float(row.contents[1].contents[0])))
        for i in range(lockers):
            row = soup.find('tr', {'id': 'lockerTr'+str(i)})
            description = str(self.html_parser.unescape(row.contents[3].contents[0].strip()))
            if row.contents[5].contents[1].contents:
                SKU = re.search('[\d\w\[\]-]+', str(row.contents[5].contents[1].contents[0].strip()))
                QTY = re.search('[\d.]+', str(row.contents[7].contents[0]))
                MAX = re.search('[\d.]+', str(row.contents[9].contents[0]))
                MIN = re.search('[\d.]+', str(row.contents[11].contents[0]))
                SKU, QTY, MAX, MIN = SKU.group(), int(float(QTY.group())), int(float(MAX.group())), int(float(MIN.group()))
                QTY, MAX, MIN = map(lambda x: x * pkgQty[SKU], [QTY, MAX, MIN])
                if SKU in parts:
                    QTY, MAX, MIN = map(lambda x: x[1] + parts[SKU][x[0]], [('QTY', QTY), ('MAX', MAX), ('MIN', MIN)])
                parts[SKU] = {'description': description, 'QTY': QTY, 'MAX': MAX, 'MIN': MIN}
            else:
                print 'Data missing from position ' + str(int(float(row.contents[1].contents[0])))
        return parts

    def getReport(self, device, beginDate, endDate):
        """Assembles transaction report, returns list of (descrip, SKU, QTY)"""
        print 'Getting report for', device, 'for', beginDate, 'through', endDate
        report = []
        params = OrderedDict((
            ('page', 1),
            ('beginDate', beginDate),
            ('endDate', endDate),
            ('checkBoxFileds', 'SKU|ProductNum1,Quantity Dispensed|QtyDispensed,Package Qty|PackageQty'),
            ('companyId', self.devices[device][0]),
            ('siteIdTmp', self.devices[device][1]),
            ('deviceId', self.devices[device][2]),
            ('searchFlag', 'SEARCH'),
            ('companyType', 'OWNER')
        ))
        request = self.s.get("https://fastsolutions.mroadmin.com/ReportManager/transactionReportAction_viewTransaction.action", params=params)
        soup = BeautifulSoup.BeautifulSoup(request.content)
        total = int(re.search('(?<=Total:&nbsp;)[\d]+', str(soup.contents[1].contents[0].contents[0].contents[0])).group())
        if total % 20 != 0:
            page = [20 for i in range((total - total % 20) / 20)]
            page.append(total % 20)
        else:
            page = [20 for i in range((total - total % 20) / 20)]
        p = 0
        for lines in page:
            p += 1
            for j in range(1, lines + 1):
                row = soup.contents[1].contents[j]
                SKU = re.search('[\d-]+\[?', str(row.contents[0].contents[0]))
                dispense = re.search('[\d]+', str(row.contents[1].contents[0]))
                pkg = re.search('[\d]+', str(row.contents[2].contents[0]))
                if SKU and dispense and pkg:
                    SKU = str(SKU.group())
                    QTY = str(int(dispense.group()) * int(pkg.group()))
                    report.append((SKU, QTY))
                else:
                    print 'Data missing on page ' + str(p) + ', line ' + str(j)
            params['page'] += 1
            request = self.s.get("https://fastsolutions.mroadmin.com/ReportManager/transactionReportAction_viewTransaction.action", params=params)
            soup = BeautifulSoup.BeautifulSoup(request.content)
        return report

    def getUsage(self, device, beginDate, endDate):
        """Assembles usage summary report, returns raw json."""
        print 'Getting report for', device, 'for', beginDate, 'through', endDate
        params = OrderedDict((
            ('company.companyId', self.devices[device][0]),
            ('siteIdTmp', self.devices[device][1]),
            ('deviceIdTemp', self.devices[device][2]),
            ('beginDate', beginDate),
            ('endDate', endDate),
            ('reportType', 'owner'),
            ('currencyCode', 'USD')
        ))
        try:
            request = self.s.post("https://fastsolutions.mroadmin.com/ReportManager/usageReportAction_getOwnerReportByDeviceBinValue.action", params=params)
        except:
            request = self.relog("https://fastsolutions.mroadmin.com/ReportManager/usageReportAction_getOwnerReportByDeviceBinValue.action", params)
        data = request.content.split('|')
        data = json.loads(data[-1])
        if len(data) <= 1:
            print 'No reporting data found!'
        return data[:-1]

    def lookUpUsage(self, SKU, usageReport):
        QTY = 0
        for u in usageReport:
            if str(u['productNum1']).strip() == SKU:
                QTY += int(u['packageQty']) * int(u['qtyDispensed'])
        return QTY

    def writeQuote(self, filename, data):
        with open(filename + '.txt', 'w') as f:
            f.writelines('\t'.join(i) + '\n' for i in data)

if __name__ == '__main__':
    FLJA1 = Apex(('Nhodges', 'password'))
