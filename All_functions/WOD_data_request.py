import numpy as np
import xarray as xr
import netCDF4
import pandas as pd
from datetime import timedelta, datetime

def request_data_from_url(year, sensor_type='ctd'):
    """
    Input: year and sensor type (ctd as the default choice)
    Output: xarray data from url (root: https://data.nodc.noaa.gov/thredds/dodsC/ncei/wod/)
    """
    url_root = 'https://data.nodc.noaa.gov/thredds/dodsC/ncei/wod/'
    file_name = f'/wod_{sensor_type}_{year}.nc'
    try: 
        ds = xr.open_dataset(url_root + str(year) + file_name, 
            decode_times=False)
    except OSError:
        print(f'{year}: No {sensor_type} data')
        ds = 0
        pass
    return ds

def rewrite_variable(ds3, var_name):
    """
    Input: xarray data, name of the variable to rewrite
    Method: 
    - Loop through the row_size array. 
    - With each row size value, cut/trim the values from begining to begining+row size 
    - Append that cut/trimmed part to the var_rewrite_array
    Result: [array1,array2,array3...] where each array is the list of values for a given cast (lon, lat, time)
    """ 
    var_rewrite_array = []

    starting_index = 0
    for row_size in ds3[f'{var_name}_row_size'].values:
        if np.isnan(row_size): #Empty/No data
            var_rewrite_array.append([-9999])
        else:
            ending_index = starting_index + int(row_size)
            raw_values = np.array(ds3[var_name].values[starting_index:ending_index])
            replace_nan_values = np.where(np.isnan(raw_values), -9999, raw_values)
            var_rewrite_array.append(replace_nan_values)
            starting_index = ending_index
    return np.array(var_rewrite_array)

def rewrite_time_array(ds):
    """
    Input: the time array from the raw dataset. This array contains the number of days from the reference time (1770/1/1)
    Output: the datetime value
    """
    reference_time = datetime(year=1770, month=1, day=1)
    new_datetime_array = [reference_time + timedelta(days=x) for x in ds.time.values]
    return np.array(new_datetime_array)

def create_clean_dataset(ds, output_type='dataframe'):
    """
    Input: the xarray from url request
    Output: the clean xarray/dataframe where 1) the shape of the variables are consistent with the coordinates
    and 2) the coordinates are: lat, lon, time (z is also in the original dataset from url)
    """
    if output_type=='xarray':
        new_coords = {'lat':ds.lat.values,
            'lon':ds.lon.values,
            'time':ds.time.values}

        data_vars = {}
        for var_name in ['Oxygen', 'Temperature', 'Salinity', 'Chlorophyll', 'z']:
            try:
                new_variable_array = rewrite_variable(ds, var_name=var_name)
                data_vars[var_name] = new_variable_array
            except KeyError:
                print(f'No {var_name} available in {ds.id[-15:-3]}')
                pass

        new_ds = xr.Dataset(data_vars=data_vars,
            coords=new_coords,      
            attrs=ds.attrs)
        
        return new_ds
    
    if output_type=='dataframe':
        new_df = pd.DataFrame()
        for coord in ['lat', 'lon']:
            new_df[coord] = ds[coord].values
            
        new_df['time'] = rewrite_time_array(ds)
        
        for var_name in ['Oxygen', 'Temperature', 'Salinity', 'Chlorophyll', 'z']:
            try:
                new_variable_array = rewrite_variable(ds, var_name=var_name)
                new_df[var_name] = new_variable_array
            except KeyError:
                print(f'No {var_name} available in {ds.id[-15:-3]}')
                pass
        return new_df
    
def trim_data_NWAtlantic(ds, datatype='dataframe'):
    """
    Use lat and lon to select the dataset for NWAtlantic
    """
    #The box for nortwest atlantic: 
    lonmin, lonmax = -80, -50
    latmin, latmax = 30, 60
    if datatype == 'xarray':
        return ds.sel(lat=slice(latmin, latmax), lon=slice(lonmin, lonmax))
    if datatype == 'dataframe':
        return ds[(ds['lat']>=latmin)&(ds['lat']<=latmax)&(ds['lon']>=lonmin)&(ds['lon']<=lonmax)]
    
def save_data(ds, year, sensor_type, datatype='dataframe', storage_folder='/shared/marn5895/data/HungJosiahProject/'):
    """
    Save the ds to the storage folder
    """
    if datatype == 'dataframe':
        end_string = 'csv'
    if datatype == 'xarray':
        end_string = 'nc'
        
    data_path = storage_folder + f'WOD_NWA_{year}_{sensor_type}.{end_string}'
    #save dataset to the storage folder:
    if datatype == 'dataframe':
        ds.to_csv(data_path, index=False)
    if datatype == 'xarray':
        ds.to_netcdf(datapath)
        
def WOD_whole_process(year_range, sensor_type_range, save=True, datatype='dataframe'):
    for year in year_range:
        for sensor_type in sensor_type_range:
            url_ds = request_data_from_url(year=year, sensor_type=sensor_type)
            if url_ds: #Only do this step if ds exist (not 0)
                ds = create_clean_dataset(url_ds, datatype)
                ds = trim_data_NWAtlantic(ds, datatype)  
    if save:
        save_data(ds, year, sensor_type, datatype)
    else:
        return ds