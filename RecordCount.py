from ApexScrape import *
import datetime


class RecordCount(object):

    def __init__(self, stores):
        self.begin_date = (datetime.datetime.now() - datetime.timedelta(100)).strftime('%m/%d/%Y')
        self.end_date = datetime.datetime.now().strftime('%m/%d/%Y')
        self.stores = stores
        for fiver in self.stores.keys():
            self.count_records(fiver)

    def count_records(self, fiver):
        STORE = Apex(self.stores[fiver])
        for c in STORE.customers.keys():
            STORE.getDevices(c)
        url = 'https://fastsolutions.mroadmin.com/ReportManager/transactionReportAction_viewTransaction.action'
        params = OrderedDict((
            ('page', 1),
            ('beginDate', self.begin_date),
            ('endDate', self.end_date),
            ('checkBoxFileds', 'Date|ActionDate'),
            ('companyId', STORE.comId),
            ('searchFlag', 'SEARCH'),
            ('companyType', 'OWNER')
        ))
        print 'Looking for data for ' + fiver
        try:
            request = STORE.s.post(url, params=params)
        except:
            request = self.relog(url, params, fiver)
        soup = BeautifulSoup.BeautifulSoup(request.content)
        total = int(re.search('(?<=Total:&nbsp;)[\d]+', str(soup.contents[1].contents[0].contents[0].contents[0])).group())
        with open('record_count_stores.txt', 'a') as f:
            f.write('{}\t{}\n'.format(fiver, str(total)))

        for c in STORE.customers.keys():
            params = OrderedDict((
                ('page', 1),
                ('beginDate', self.begin_date),
                ('endDate', self.end_date),
                ('checkBoxFileds', 'Date|ActionDate'),
                ('companyId', STORE.comId),
                ('siteIdTmp', STORE.customers[c]),
                ('searchFlag', 'SEARCH'),
                ('companyType', 'OWNER')
            ))
            try:
                request = STORE.s.post(url, params=params)
            except:
                request = self.relog(url, params, fiver)
            soup = BeautifulSoup.BeautifulSoup(request.content)
            total = int(re.search('(?<=Total:&nbsp;)[\d]+', str(soup.contents[1].contents[0].contents[0].contents[0])).group())
            with open('record_count_customers.txt', 'a') as f:
                f.write('{}\t{}\n'.format(c, str(total)))

    def relog(self, url, params, fiver):
        print 'relogging'
        login = OrderedDict((('user.login_id', self.stores[fiver][0]), ('user.password', self.stores[fiver][1])))
        self.s = requests.Session()
        self.s.post('https://fastsolutions.mroadmin.com/APEX-Login/account_login.action', data=login)
        # If at first you don't succeed ...
        while True:
            try:
                request = self.s.post(url, params=params)
            except:
                continue
            return request


if __name__ == '__main__':
<<<<<<< HEAD
    # insert store logins
=======

































>>>>>>> 468a53c8734d607079bc95f2cd332de475f87e5a

    RecordCount(stores)

