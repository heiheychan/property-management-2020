# property,for_date,transact_date,type,for,amount,recurring,taxable,debt
# 205,01/01/2020,02/01/2020,IN,RENT,3600,1,1,0

import random
from datetime import date, timedelta
from dateutil.relativedelta import *

# Configuration
start_year = 2019
start_month = 1
duration = 13
properties = {'205': {
                'rent': '3850',
                'gas': '150',
                'power': '50',
                'tax': '1000',
                'deposit': '3850'
            }, '289': {
                'rent': '3600',
                'gas': '100',
                'power': '60',
                'tax': '366',
                'deposit': '3600'
            }, '558-L1': {
                'rent': '4000',
                'gas': '200',
                'power': '80',
                'tax': '500',
                'deposit': '4000'
            }}

def generate_two_dates(year, month, d):
    for_date = date(year,month,1) + timedelta(days=d)
    random_delta = random.randint(-5,5)
    transact_date = for_date + timedelta(days=random_delta)
    return [for_date.strftime("%m/%d/%Y"), transact_date.strftime("%m/%d/%Y")]

def generate_one_month(prop, d):
    end_str = ""
    year = d.year
    month = d.month
    # RENT
    d = generate_two_dates(year, month, 0)
    end_str += "{},{},{},IN,RENT,{},1,1,0\n".format(prop, d[0], d[1], properties[prop]['rent'])
    # GAS
    d = generate_two_dates(year, month, 5)
    end_str += "{},{},{},OUT,GAS,{},1,1,0\n".format(prop, d[0], d[1], properties[prop]['gas'])
    # POWER
    d = generate_two_dates(year, month, 3)
    end_str += "{},{},{},OUT,POWER,{},1,1,0\n".format(prop, d[0], d[1], properties[prop]['power'])
    # PROP_TAX - introducing cash concept or accrual concept
    d = generate_two_dates(year, month, 1)
    end_str += "{},{},,OUT,TAX,{},1,1,0\n".format(prop, d[0], str(round(int(properties[prop]['tax'])/3)))
    # PROP_TAX_PAYMENT
    if month in [1,4,7,10]:
        d = generate_two_dates(year, month, 1)
        end_str += "{},,{},OUT,TAX,{},1,1,0\n".format(prop, d[0], properties[prop]['tax'])

    return end_str

def generate_deposit(prop, d):
    year = d.year
    month = d.month
    # Deposit
    d = generate_two_dates(year, month, -20)
    print(d[0])
    return "{},,{},IN,DEPOSIT,{},0,0,1\n".format(prop, d[0], properties[prop]['deposit'])


with open('sample_data.csv', 'a') as f:
    f.write("property,for_date,transact_date,type,for,amount,recurring,taxable,debt\n")
    for one_prop in properties:
        f.write(generate_deposit(one_prop, date(start_year, start_month, 1)))
        for delta in range(duration):
            f.write(generate_one_month(one_prop, date(start_year, start_month, 1) + relativedelta(months=delta)))
