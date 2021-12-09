import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import cartopy.crs as ccrs       # ccrs contains information about projections
import cartopy                   # contains all other cartopy functions/classes/methods
import cartopy.feature as cfeature
import cmocean
import gsw

def median_from_array(x):
    if len(x[~np.isnan(x)])==0:
        return np.nan
    else:
        return np.median(x[~np.isnan(x)])
    
def mean_from_array(x):
    if len(x[~np.isnan(x)])==0:
        return np.nan
    else:
        return np.mean(x[~np.isnan(x)])
    
def bottom_from_array(x):
    ####STILL NEED REWRITE!!!!!
    if len(x[~np.isnan(x)])==0:
        return np.nan
    else:
        return x[~np.isnan(x)][-1]
    
def max_from_array(x):
    if len(x[~np.isnan(x)])==0:
        return np.nan
    else:
        return np.max(x[~np.isnan(x)])
    
def min_from_array(x):
    if len(x[~np.isnan(x)])==0:
        return np.nan
    else:
        return np.min(x[~np.isnan(x)])
    
def surface_from_array(x):
    if len(x[~np.isnan(x)])==0:
        return np.nan
    else:
        return x[~np.isnan(x)][0]
    
def estimate_median_N_squared(df):
    """
    Documentation: https://teos-10.github.io/GSW-Python/gsw_flat.html
    """
    median_N_squared_array = []
    for i in df.index:
        print(i, end="\r")
        p_array = gsw.p_from_z(z=-df['z'][i], lat=df['lat'][i]).astype(float)
        CT_array = gsw.CT_from_t(SA=df['Salinity'][i].astype(float), t=df['Temperature'][i].astype(float), p=p_array).astype(float)
        N2_values, p_midarray = gsw.Nsquared(SA=df['Salinity'][i].astype(float), CT=CT_array, p=p_array, lat=df['lat'][i], axis=0)
        #print(N2_values)
        median_N_squared_array.append(median_from_array(N2_values))
    df['median_N_squared'] = median_N_squared_array
    
def estimate_N_squared(df):
    """
    Documentation: https://teos-10.github.io/GSW-Python/gsw_flat.html
    """
    N_squared_array = []
    for i in df.index:
        print(i, end="\r")
        p_array = gsw.p_from_z(z=-df['z'][i], lat=df['lat'][i]).astype(float)
        CT_array = gsw.CT_from_t(SA=df['Salinity'][i].astype(float), t=df['Temperature'][i].astype(float), p=p_array).astype(float)
        N2_values, p_midarray = gsw.Nsquared(SA=df['Salinity'][i].astype(float), CT=CT_array, p=p_array, lat=df['lat'][i], axis=0)
        #print(N2_values)
        N_squared_array.append(np.insert(N2_values, 0, np.nan))
    df['N_squared'] = N_squared_array
    
def estimate_surface_var(df, var):
    surface_array = []
    for i in df.index:
        print(i, end="\r")
        surface_array.append(surface_from_array(df[var][i].astype(float)))
    df[f'surface_{var}'] = surface_array

def estimate_median_var(df, var):
    median_array = []
    for i in df.index:
        print(i, end="\r")
        median_array.append(median_from_array(df[var][i].astype(float)))
    df[f'median_{var}'] = median_array

def estimate_depth_average_var(df, var, z_lower=50, z_upper=100):
    depth_avg_array = []
    for i in df.index:
        print(i, end='\r')
        if len(df[var][i][~np.isnan(df[var][i].astype(float))])==0:
            depth_avg_array.append(np.nan)
        else:
            #z_sel = np.logical_and(df['z'].values>z_lower, df['z'].values<z_upper)
            z_sel = (df['z'][i]>z_lower)&(df['z'][i]<z_upper)
            var_sel_array = df[var][i][z_sel] 
            depth_avg_array.append(mean_from_array(var_sel_array.astype(float)))
    df[f'{z_lower}_{z_upper}_{var}'] = depth_avg_array
    
def estimate_depth_min_var(df, var, z_lower=50, z_upper=100):
    depth_min_array = []
    for i in df.index:
        print(i, end='\r')
        if len(df[var][i][~np.isnan(df[var][i].astype(float))])==0:
            depth_min_array.append(np.nan)
        else:
            #z_sel = np.logical_and(df['z'].values>z_lower, df['z'].values<z_upper)
            z_sel = (df['z'][i]>z_lower)&(df['z'][i]<z_upper)
            var_sel_array = df[var][i][z_sel] 
            depth_min_array.append(min_from_array(var_sel_array.astype(float)))
    df[f'{z_lower}_{z_upper}_min_{var}'] = depth_min_array 
    
def coarsen_df(df, var):
    """
    Similar to coarsen function of xarray. This simple version makes coarsen for box of size 1 degree lat and lon. 
    """
    df['round_lat'] = list(map(lambda x: round(x), df['lat']))
    df['lat'] = list(map(lambda x: round(x), df['lat']))
    df['round_lon'] = list(map(lambda x: round(x), df['lon']))
    df['lon'] = list(map(lambda x: round(x), df['lon']))
    return df.groupby(by=["round_lat","round_lon"], dropna=True).mean()

def make_yearly_maps(new_df, var, want_coarsen=True): 
    full_name_dict = {'median_N_squared':'Median buoyancy squared (1/$s^2$)',
                  'median_Oxygen': 'Median oxygen (µmol/kg)',
                  'median_Chlorophyll': 'Median chlorophyll (µgram/l)',
                 'median_Temperature': 'Median Temeprature ($\degree$C)',
                     'surface_Temperature': 'Median Temeprature ($\degree$C)',
                     '50_100_Oxygen': 'Average oxygen from 50-100m (µmol/kg)',
                      '50_100_min_Oxygen': 'Minimum oxygen from 50-100m (µmol/kg)',
                     '50_100_N_squared': 'Average buoyancy squared from 50-100m (1/$s^2$)',
                     '100_150_N_squared': 'Average buoyancy squared from 100-150m (1/$s^2$)'}
    cmap_dict = {'median_N_squared': 'YlOrRd',
                 'median_Oxygen': cmocean.cm.oxy,
                 'median_Chlorophyll': cmocean.cm.algae,
                'median_Temperature': cmocean.cm.thermal,
                'surface_Temperature': cmocean.cm.thermal,
                '50_100_Oxygen': cmocean.cm.oxy,
                 '50_100_min_Oxygen': cmocean.cm.oxy,
                 '50_100_N_squared': 'YlOrRd',
                 '100_150_N_squared': 'YlOrRd'}
    
    ncols = 6
    nrows = int(np.ceil(54/ncols))
    lower_bound, upper_bound = np.nanquantile(new_df[var], [0.025, 0.975])

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(3*ncols, 3*nrows),
                            subplot_kw={'projection': ccrs.PlateCarree()})
    axes_flat = axes.flat
    i = 0
    for given_year in range(1968,2022):
        print(given_year, end="\r")
        ax = axes_flat[i]
        lonmin, lonmax = -80, -50
        latmin, latmax = 30, 60
        ax.set_extent([lonmin, lonmax, latmin, latmax], crs=ccrs.PlateCarree())
        ds = new_df.loc[[x.year==given_year for x in new_df.time],:].dropna(subset=[var])[['lat','lon', var]]
        if want_coarsen: 
            ds = coarsen_df(ds, var)

        im = ax.scatter(ds.lon.values, ds.lat.values, c=ds[var].values,  
            transform=ccrs.PlateCarree(), alpha=0.7, cmap=cmap_dict[var], marker='s',
            vmin=lower_bound, vmax=upper_bound)

        ax.coastlines()
        ax.add_feature(cartopy.feature.LAND, edgecolor='black', zorder=1)
        ax.set_title(given_year)
        gl = ax.gridlines(draw_labels=True, alpha=0.2, crs=ccrs.PlateCarree())
        gl.xlabels_top = gl.ylabels_right = False
        i += 1

    fig.subplots_adjust(top=0.99)
    cbar_ax = fig.add_axes([0.08, 0.04, 0.8, 0.01])
    fig.colorbar(im, cax=cbar_ax, label=full_name_dict[var], orientation='horizontal')
    fig.show()
    
def closest_value(value, array):
    """
    Source: https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def rigor_classify_geology(df, bathymetry_data):
    """
    From a (lat,lon) of the WOD data, find the the bottom depth by finding the elevation of that (lat,lon) 
    From the elevation, classify that point: 
    - From surface to 1000m (z_max from 0 to 1000): On shelf
    - Below 1000m (z_max greater than 1000): Off shelf 
    """
    classify_array = []
    for i in df.index:
        print(i, end="\r")
        lat_val = closest_value(value=df['lat'][i], array=bathymetry_data.lat.values)
        lon_val = closest_value(value=df['lon'][i], array=bathymetry_data.lon.values)
        max_z = -float(bathymetry_data.sel(lat=lat_val, lon=lon_val).elevation.values)
        
        if max_z >1000:
            classify_array.append('off_shelf')
        else:
            classify_array.append('on_shelf')
    df['geo_classify'] = classify_array
    
    
def classify_geology(df):
    classify_array = []
    for i in df.index:
        print(i, end="\r")
        max_z = max_from_array(df['z'][i].astype(float))
        if max_z >250:
            classify_array.append('off_shelf')
        else:
            classify_array.append('on_shelf')
    df['geo_classify'] = classify_array