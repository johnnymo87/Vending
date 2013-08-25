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
    stores = OrderedDict((
        ('FLPER', ('FastenalFLPER', 'fastenal3')),
        ('FLCRY', ('branchflcry', 'flcry8975')),
        ('FLBRK', ('FastenalFLBRK', 'password')),
        ('FLLAC', ('STOREFLLAC', 'fllacice')),
        ('FLGAN', ('FLGANStore', 'password')),
        ('FLGA1', ('FastenalFLGA1', 'password')),
        ('FLOCA', ('SteveMcMillen', 'password')),
        ('FLOC1', ('branchfloc1', 'k45lm2mf')),
        ('FL002', ('SantosBaez1', 'fastenal')),
        ('FLBEE', ('STOREFLBEE', 'password')),
        ('FLLEE', ('FastenalFLLEE', 'password')),
        ('FLTAV', ('FastenalFLTAV', '123456')),
        ('FLPAA', ('STOREFLPAA', 'password')),
        ('FLJA1', ('Nhodges', 'password')),
        ('FLJA2', ('STOREFLJA2', 'password')),
        ('FLJA3', ('FastenalFLJA3', '16Dutton')),
        ('FLJA4', ('STOREFLJA4', 'support')),
        ('FLJA6', ('FASTENALFLJA6', '7033Commonwealth')),
        ('FLFER', ('FastenalFLFER', 'number1')),
        ('GAWA1', ('BranchGAWA1', 'password')),
        ('GABRU', ('JohnJernigan', 'password')),
        ('FLJA5', ('FastenalFLJA5', 'password')),
        ('FLJAC', ('FastFLJAC', 'password')),
        ('FLGRE', ('branchflgre', 'fastenal')),
        ('FLSTA', ('fastenalflsta', '06749gon')),
        ('FLORM', ('STOREFLORM', 'password')),
        ('FLSAN', ('FastenalFLSAN', 'password')),
        ('FLLON', ('FastenalFLLON', 'Boltandnut1')),
        ('FLOR1', ('FastenalFLOR1', 'password')),
        ('FLOR6', ('FastFLOR6', 'password')),
        ('FLEDG', ('FastenalFLEDG', 'password'))
    ))

    RecordCount(stores)

