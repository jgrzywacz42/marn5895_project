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
    
def str_to_np_array(array_string):
    """
    Turn a array (in string format) to a numpy array
    """
    if type(array_string) == str:
        array_string = ','.join(array_string.replace('[ ', '[').split())
        if array_string[1] == ',':
            array_string = eliminate_comma(array_string, 1)
        if array_string[-2] == ',':
            array_string = eliminate_comma(array_string, -2)
        array_values = np.array(ast.literal_eval(array_string))
        #replace -9999 with np.nan:
        array_values = np.where(array_values==-9999, np.nan, array_values)
        return array_values
    if type(array_string) == float:
        return np.array([array_string])
    
def remove_Ellipsis(df, var):
    """
    Iterate through each row of the given var's column
    Replace Ellipsis with np.nan
    """
    new_column = []
    for array in df[var]:
        if Ellipsis in array:
            array = np.where(array==Ellipsis, np.nan, array)
        new_column.append(array)
    df[var] = new_column

def process_df(df, inspect=False):
    if inspect:
        weird_index_array = []
        for var in ['Temperature', 'Salinity', 'z', 'Oxygen', 'Chlorophyll']:
            try:
                print(var)
                for i, x in enumerate(df[var]):
                    print(i, end="\r")
                    new_x = str_to_np_array(x)
            except ValueError:
                print(f'Weird {var} at {i}')
                weird_index_array.append(i)
                pass
        return weird_index_array
            
    else:
        for var in ['Temperature', 'Salinity', 'z', 'Oxygen', 'Chlorophyll']:
            try:
                df[var] = list(map(lambda x: str_to_np_array(x),
                                   df[var]))
            except KeyError:
                print(f'No {var} in dataset')
                pass
            
        #Replace Ellipsis:     
        for var in ['Temperature', 'Salinity', 'z', 'Oxygen', 'Chlorophyll']:
            print('Removing Ellipsis in: ', var)
            remove_Ellipsis(df, var)
            
        #Transfer the string time to datetime value. 
        #The split in x.split('.')[0] is to account for the decimals behind the number of seconds ('1969-01-07 21:00:00.000000')
        df['time'] = list(map(lambda x: datetime.strptime(x.split('.')[0], '%Y-%m-%d %H:%M:%S'),
                              df['time']))
        return df
    