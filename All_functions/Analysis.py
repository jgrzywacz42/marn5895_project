import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import cartopy.crs as ccrs       # ccrs contains information about projections
import cartopy                   # contains all other cartopy functions/classes/methods
import cartopy.feature as cfeature
import cmocean

def median_from_array(x):
    if len(x[~np.isnan(x)])==0:
        return np.nan
    else:
        return np.median(x[~np.isnan(x)])
    
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
    
def estimate_buoyancy_frequency(df):
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

def estimate_median_oxygen(df):
    median_oxgyen_array = []
    for i in df.index:
        print(i, end="\r")
        median_N_squared_array.append(median_from_array(df['Oxygen'][i]))
    df['median_oxygen'] = median_oxygen
    
def make_animation(new_df, var, want_coarsen=True):
    #Animation: 
    # Setup the initial plot
    full_name_dict = {'median_N_squared':'Median buoyancy squared (1/$s^2$)',
                      'median_oxygen': 'Median oxygen (µmol/kg)'}
    cmap_dict = {'median_N_squared': 'YlOrRd',
                 'median_oxygen': cmocean.cm.oxy}
    
    fig = plt.figure(figsize=(6,5))
    ax = plt.axes(projection=ccrs.PlateCarree())
    lower_bound, upper_bound = np.nanquantile(new_df[var], [0.025, 0.975])
    temp_im = ax.scatter(new_df.lon.values, new_df.lat.values, 
                         c=new_df[var].values, 
                        transform=ccrs.PlateCarree(), cmap=cmap_dict[var], alpha=0.9,
                        vmin=lower_bound, vmax=upper_bound)
    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.8, 0.15, 0.04, 0.7])  #[left, bottom, width, height] 
    fig.colorbar(temp_im, cax=cbar_ax, label=full_name_dict[var])

    def update(year):
        global new_df, lower_bound, upper_bound
        # Update the plot for a specific time
        print(year, end="\r")
        ax.clear()
        lonmin, lonmax = -80, -50
        latmin, latmax = 30, 60
        ax.set_extent([lonmin, lonmax, latmin, latmax], crs=ccrs.PlateCarree())
        ax.coastlines()
        ax.add_feature(cartopy.feature.LAND, edgecolor='black', zorder=1)
        ax.set_title("Year = %s"%year)
        ds = new_df.loc[[x.year==year for x in new_df.time],:].dropna(subset=[var])
        if want_coarsen:
            ds = coarsen_df(ds, var)
        im = ax.scatter(ds.lon.values, ds.lat.values, c=ds[var].values,  
            transform=ccrs.PlateCarree(), alpha=0.7, cmap=cmap_dict[var], marker='s',
            vmin=lower_bound, vmax=upper_bound)
        return im,

    # Run the animation, applying `update()` for each of the times in the variable
    animation = anim.FuncAnimation(fig, update, frames=range(1999,2022), blit=False)
    #animation.save('Final_stratification.mp4', fps=1, extra_args=['-vcodec', 'libx264'])
    animation.save(f'{var}.gif', fps=1, dpi=80)
    plt.show()
    del animation
    
def coarsen_df(df, var):
    df['round_lat'] = list(map(lambda x: round(x), df['lat']))
    df['lat'] = list(map(lambda x: round(x), df['lat']))
    df['round_lon'] = list(map(lambda x: round(x), df['lon']))
    df['lon'] = list(map(lambda x: round(x), df['lon']))
    return df.groupby(by=["round_lat","round_lon"], dropna=True).mean()