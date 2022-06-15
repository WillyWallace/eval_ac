"""
this routine visualizes the results of the absolute calibration with liquid nitrogen of the
microwave radiometer HATPRO from RPG
"""
import matplotlib.pyplot as plt
from eval_ac.convert_abscal_his import HatproBinAbscalHis

# ### begin user specifications
FILE = '../example_data/ABSCAL.HIS'
# # plot specifications
latest_plot_kwargs = {'lw': '2'}
second_latest_plot_kwargs = {'lw': '2'}
older_plot_kwargs = {'lw': '1', 'color': 'lightgrey'}
# ### end user specifications

obj = HatproBinAbscalHis(FILE)

ds_small = obj.xrdata[['gain', 'temp_noise', 'temp_sys', 'alpha']]

with plt.style.context(['default']):

    figure, ax = plt.subplots(4, 2, figsize=(10, 4*2.5))

    i = 0
    for variables in ds_small.data_vars:
        # print(vars)
        ds_small.isel(n_samples=slice(1, -2), freq=slice(0, 7))[variables].plot(
            hue='n_samples',
            ax=ax[i, 0],
            label='',
            **older_plot_kwargs)
        ds_small.isel(n_samples=0, freq=slice(0, 7))[variables].plot(
            hue='n_samples',
            ax=ax[i, 0],
            label='old',
            **older_plot_kwargs)
        ds_small.isel(n_samples=-2, freq=slice(0, 7))[variables].plot(
            hue='n_samples',
            ax=ax[i, 0],
            label='previous',
            **second_latest_plot_kwargs)
        ds_small.isel(n_samples=-1, freq=slice(0, 7))[variables].plot(
            hue='n_samples',
            ax=ax[i, 0],
            label='latest',
            **latest_plot_kwargs)
        ax[i, 0].set_title(ds_small[variables].attrs['long_name'])
        ax[i, 0].legend()

        ds_small.isel(n_samples=slice(1, -2), freq=slice(7, 14))[variables].plot(
            hue='n_samples',
            ax=ax[i, 1],
            label='',
            **older_plot_kwargs)
        ds_small.isel(n_samples=0, freq=slice(7, 14))[variables].plot(
            hue='n_samples',
            ax=ax[i, 1],
            label='old',
            **older_plot_kwargs)
        ds_small.isel(n_samples=-2, freq=slice(7, 14))[variables].plot(
            hue='n_samples',
            ax=ax[i, 1],
            label='previous',
            **second_latest_plot_kwargs)
        ds_small.isel(n_samples=-1, freq=slice(7, 14))[variables].plot(
            hue='n_samples',
            ax=ax[i, 1],
            label='latest',
            **latest_plot_kwargs)
        ax[i, 1].set_title(ds_small[variables].attrs['long_name'])
        ax[i, 1].legend()

        i = i + 1

    plt.tight_layout()
    # plt.show()
    plt.savefig('results_ln2_cal.png')
