import unittest
import utils
from datetime import datetime
import time

class KnowValues(unittest.TestCase):
    knownValues = (
        ('20090101','20090201',['20090101','20090201','month']),
        ('20090112','20090201',['20090112','20090201','day']),
        ('20090112','20090120',['20090112','20090120','day']),
        ('20090101','20090223',['20090101','20090201','20090223','month','day']),
        ('20090125','20090301',['20090125','20090201','20090301','day','month']),
        ('20090112','20090820',['20090112','20090201','20090801','20090820','day','month','day']),
    )
    
    def testKnownValues(self):                          
        for str_s, str_e, res_k in self.knownValues:
                        
            start_date = datetime(year=int(str_s[0:4]), month=int(str_s[4:6]),day=int(str_s[6:8]))
            
            end_date = datetime(year=int(str_e[0:4]), month=int(str_e[4:6]),day=int(str_e[6:8]))
            
            temp = utils.split_month(start_date, end_date)
            
            result = []
            
            for date in temp:
                try:
                    result.append(date.strftime('%Y%m%d'))
                except:
                    result.append(date)

            self.assertEqual(res_k, result)
            

unittest.main()


    
