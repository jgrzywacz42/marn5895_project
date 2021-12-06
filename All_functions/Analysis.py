import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import cartopy.crs as ccrs       # ccrs contains information about projections
import cartopy                   # contains all other cartopy functions/classes/methods
import cartopy.feature as cfeature

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
    bottom_N_squared_array = []
    max_N_squared_array = []
    for i in df.index:
        print(i, end="\r")
        p_array = gsw.p_from_z(z=-df['z'][i], lat=df['lat'][i]).astype(float)
        CT_array = gsw.CT_from_t(SA=df['Salinity'][i].astype(float), t=df['Temperature'][i].astype(float), p=p_array).astype(float)
        N2_values, p_midarray = gsw.Nsquared(SA=df['Salinity'][i].astype(float), CT=CT_array, p=p_array, lat=df['lat'][i], axis=0)
        #print(N2_values)
        median_N_squared_array.append(median_from_array(N2_values))
        bottom_N_squared_array.append(bottom_from_array(N2_values))
        max_N_squared_array.append(max_from_array(N2_values))
    df['median_N_squared'] = median_N_squared_array
    df['bottom_N_squared'] = bottom_N_squared_array
    df['max_N_squared'] = max_N_squared_array
    
def make_animation(new_df):
    #Animation: 
    # Setup the initial plot
    fig = plt.figure(figsize=(6,5))
    ax = plt.axes(projection=ccrs.PlateCarree())
    """
    lonmin, lonmax = -80, -50
    latmin, latmax = 30, 60
    ax.set_extent([lonmin, lonmax, latmin, latmax], crs=ccrs.PlateCarree())
    ax.coastlines()
    ax.add_feature(cartopy.feature.LAND, edgecolor='black', zorder=1)

    temp_im = ax.scatter(new_df.lon.values, new_df.lat.values, 
                         c=new_df.median_N_squared.values, 
                        transform=ccrs.PlateCarree(), cmap='seismic', alpha=0.9,
                        vmin=lower_bound, vmax=upper_bound)
    """
    fig.subplots_adjust(right=0.85)
    cbar_ax = fig.add_axes([0.88, 0.15, 0.04, 0.7])  #[left, bottom, width, height] 
    fig.colorbar(temp_im, cax=cbar_ax, label='Median buoyancy squared (1/s^2)')

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
        ds = new_df.loc[[x.year==year for x in new_df.time],:].dropna(subset=['median_N_squared'])
        if len(ds) > 3: 
            im = ax.scatter(ds.lon.values, ds.lat.values, c=ds.median_N_squared.values, 
                            transform=ccrs.PlateCarree(), alpha=0.9, cmap='seismic',
                            vmin=lower_bound, vmax=upper_bound)
        else:
            im = ax
        return im,

    # Run the animation, applying `update()` for each of the times in the variable
    animation = anim.FuncAnimation(fig, update, frames=range(1999,2005), blit=False)
    animation.save('Stratification.mp4', fps=10, extra_args=['-vcodec', 'libx264'])
    plt.show()
    del animation
    
def coarsen_df(df, var):
    df['round_lat'] = list(map(lambda x: round(x), df['lat']))
    df['lat'] = list(map(lambda x: round(x), df['lat']))
    df['round_lon'] = list(map(lambda x: round(x), df['lon']))
    df['lon'] = list(map(lambda x: round(x), df['lon']))
    return df.groupby(by=["round_lat","round_lon"], dropna=True).mean()