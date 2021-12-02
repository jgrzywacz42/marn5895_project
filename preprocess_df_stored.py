import numpy as np
import pandas as pd
import glob
import os
from datetime import datetime
import ast

def eliminate_comma(array_string, comma_index):
    """
    Turn array string to a list, eliminate the comma from the given index, return the string array
    """
    array_string = list(array_string)
    array_string[comma_index] = ''
    array_string
    array_string = ''.join(array_string)
    return array_string
    
def from_np_array(array_string):
    """
    Turn a array (in string format) to a numpy array
    """
    array_string = ','.join(array_string.replace('[ ', '[').split())
    if array_string[1] == ',':
        array_string = eliminate_comma(array_string, 1)
    if array_string[-2] == ',':
        array_string = eliminate_comma(array_string, -2)
    return np.array(ast.literal_eval(array_string))

def process_df(df):
    #Transfer the string time to datetime value. 
    #The split in x.split('.')[0] is to account for the decimals behind the number of seconds ('1969-01-07 21:00:00.000000')
    df['time'] = list(map(lambda x: datetime.strptime(x.split('.')[0], '%Y-%m-%d %H:%M:%S'),
                          df['time']))
    
    for var in ['Temperature', 'Salinity', 'z', 'Oxygen', 'Chlorophyll']:
        try:
            df[var] = list(map(lambda x: from_np_array(x),
                               df[var]))
        except KeyError:
            print(f'No {var} in dataset')
            pass
    return df
    