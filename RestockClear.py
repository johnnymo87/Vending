__author__ = 'johnnymo87'
import requests
import json
import BeautifulSoup
from collections import OrderedDict
import re

s = requests.Session()
login_data = {'user.login_id': 'FastenalFLJA5', 'user.password': 'password'}
# login
request = s.post('https://fastsolutions.mroadmin.com/APEX-Login/account_login.action', data=login_data)

# Greg Smith, Amy Balash: gregsmit@fastenal.com 513-644-0017, abalash@fastenal.com 513-644-0011
# Nathan Thomas: nthomas@fastenal.com 513-644-0025

params = {
    'actionSequence': 13,
    'RequestId': 'undefined',
    'newSortColumn': 0,
    'oldSortColumn': 0,
    'sortFlag': 'null',
    'sortCancel': 0
}
request = s.post('https://fastsolutions.mroadmin.com/APEX-Login/inbox_restockInfoAlert.action', params=params)
data = request.content.split('|')
pages = int(re.search('(?<=/)[\d]+', data[0]).group())
for i in range(pages):
    params = {
        'actionSequence': 13,
        'RequestId': 'undefined',
        'newSortColumn': 0,
        'oldSortColumn': 0,
        'sortFlag': 'null',
        'sortCancel': 0
    }
    request = s.post('https://fastsolutions.mroadmin.com/APEX-Login/inbox_restockInfoAlert.action', params=params)
    data = request.content.split('|')
    data = json.loads(data[-3])
    for d in data:
        print d['restockId']
        params = {
            'searchType': 'KEY_WORDS',
            'RequestId': d['restockId']
        }
        request = s.post('https://fastsolutions.mroadmin.com/RestockManager/restockListManager_toApproveOrRestockOrView.action', params=params)
        soup = BeautifulSoup.BeautifulSoup(request.content)

        data = soup.findAll('tr')
        data = data[11:-3]
        string = ''
        for d in data:
            inputs = d.findAll('input', {'type': 'hidden'})
            if len(inputs) > 0:
                if len(d.findAll('option')) > 1:
                    string += '{}:{}:Cancel,'.format(inputs[0]['value'], inputs[1]['value'])
                else:
                    string += '{}:{}:NoSelected,'.format(inputs[0]['value'], inputs[1]['value'])

        data = soup.findAll('input', {'type': 'hidden'})
        data = [d['value'] for d in data]

        form = OrderedDict((
            ('struts.token.name', data[0]),
            ('struts.token', data[1]),
            ('restockId', data[2]),
            ('restock.restockId', data[3]),
            ('companyId', data[4]),
            ('inventoryString', string[:-1])
        ))
        s.post('https://fastsolutions.mroadmin.com/RestockManager/restockListManager_inventoryRestock.action', data=form)
