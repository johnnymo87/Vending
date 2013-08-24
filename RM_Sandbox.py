from ApexScrape import *

FLGAN = Apex(('FLGANStore', 'password'))

for c in FLGAN.customers:
    FLGAN.getDevices(c)

device = FLGAN.devices.keys()[2] # 'Main Shop'
begin_date = '08/01/2013'
end_date = '08/23/2013'

##report = FLGAN.getReport(device, '08/01/2013', '08/23/2013')
##print report
url = "https://fastsolutions.mroadmin.com/ReportManager/transactionReportAction_viewTransaction.action"
params = OrderedDict((
            ('page', 1),
            ('beginDate', begin_date),
            ('endDate', end_date),
            ('checkBoxFileds', 'Date|ActionDate,Product SKU|ProductNum1,Quantity Dispensed|QtyDispensed,Package Qty|PackageQty'),
            ('companyId', FLGAN.devices[device][0]),
            ('siteIdTmp', FLGAN.devices[device][1]),
            ('deviceId', FLGAN.devices[device][2]),
            ('searchFlag', 'SEARCH'),
            ('companyType', 'OWNER')
        ))
print 'Getting report for', device, 'for', begin_date, 'through', end_date
request = FLGAN.s.get(url, params=params)
soup = BeautifulSoup.BeautifulSoup(request.content)
stamp = str(soup.contents[1].contents[1].contents[0].contents[0])
stamp = re.search('[\d\- :]+', stamp)
if stamp:
    stamp = stamp.group().strip()

from datetime import datetime
stamp = datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S")
print str(stamp)
