import datetime
import unittest

from datetime import timedelta

import calendar

model_dict = {
    'hour':{'model':'ModelHourly', 'field':'ctime'},
    'day':{'model':'ModelDaily', 'field':'cday'},
    'week':{'model':'ModelWeekly', 'field':'cweek'},
    'month':{'model':'ModelMonthly', 'field':'cmonth'},
}

def split_month(start_date, end_date):
    '''
    comments
    '''
    # check start_date
    ndays_s = calendar.monthrange(year=start_date.year, month=start_date.month)
    ndays_e = calendar.monthrange(year=end_date.year, month=end_date.month)
    
    tdate_s = start_date.replace(day = int(ndays_s[1])) + timedelta(days=1)
    tdate_e = end_date.replace(day = 1)

    if tdate_e < tdate_s:
        # day
        return [start_date, end_date,'day']

    if start_date.day == 1 and end_date.day == 1:
        # month
        return [start_date, end_date, 'month']
        
    if tdate_e == tdate_s:
        if end_date == tdate_s:
            return [start_date, end_date, 'day']    
        return [start_date, tdate_s, end_date, 'month','day']

    if start_date.day == 1:
        # month, day
        return [start_date, tdate_e, end_date, 'month', 'day']
        
    if end_date.day == 1:
        # day, month
        return [start_date, tdate_s, end_date, 'day','month']

    # day
    return [start_date, tdate_s, tdate_e, end_date, 'day','month','day']
    
    '''
    if tdate_e < tdate_s:
        return [
            {
                'start':start_date,
                'end': end_date,
                'model': model_dict['day']
            },
        ]
    
    return [
        {
            'start':start_date,
            'end':tdate_s,
            'model':model_dict['day']
        },
        {
            'start':tdate_s,
            'end':tdate_e,
            'model':model_dict['month']
        },
        {
            'start':tdate_e,
            'end':end_date,
            'model':model_dict['day']
        },
    ]
    '''
    
    
    