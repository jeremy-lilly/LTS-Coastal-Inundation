#!/usr/bin/env python

# Author: Steven Brus

import netCDF4
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import numpy as np
import glob
import pprint
import datetime
import os
import yaml
import pprint
import subprocess
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy import spatial
import argparse as ap

plt.switch_backend('agg')
cartopy.config['pre_existing_data_dir'] = \
        os.getenv('CARTOPY_DIR', cartopy.config.get('pre_existing_data_dir'))


################################################################################################
################################################################################################

def read_pointstats(pointstats_file):

  pointstats_nc = netCDF4.Dataset(pointstats_file,'r')
  data = {}
  data['date'] = pointstats_nc.variables['xtime'][:]
  data['datetime'] = []
  for date in data['date']:
    d = b''.join(date).strip()
    data['datetime'].append(datetime.datetime.strptime(d.decode('ascii').strip('\x00'),'%Y-%m-%d_%H:%M:%S'))
  data['datetime'] = np.asarray(data['datetime'],dtype='O')
  data['lon'] = np.degrees(pointstats_nc.variables['lonCellPointStats'][:])
  data['lon'] = np.mod(data['lon']+180.0,360.0)-180.0
  data['lat'] = np.degrees(pointstats_nc.variables['latCellPointStats'][:])
  data['ssh'] = pointstats_nc.variables['sshPointStats'][:]

  return data

################################################################################################
################################################################################################

def read_station_data(obs_file,min_date,max_date):

  frmt = '%Y %m %d %H %M'

  # Initialize variable for observation data
  obs_data = {}
  obs_data['ssh'] = []
  obs_data['datetime'] = []

  # Get data from observation file between min and max output times
  f = open(obs_file)
  obs = f.read().splitlines()
  for line in obs[1:]:
    if line.find('#') >= 0 or len(line.strip()) == 0 or not line[0].isdigit():
      continue
    try:                                                               # NOAA-COOPS format
      date = line[0:16]
      date_time = datetime.datetime.strptime(date,frmt)
      col = 5
      convert = 1.0
    except:                                                            # USGS station format
      date = line[0:19]
      date_time = datetime.datetime.strptime(date,'%m-%d-%Y %H:%M:%S')
      col = 2
      convert = 0.3048
    if date_time >= datetime.datetime.strptime(min_date,frmt) and \
       date_time <= datetime.datetime.strptime(max_date,frmt):
      obs_data['datetime'].append(date_time)
      obs_data['ssh'].append(line.split()[col])

  # Convert observation data and replace fill values with nan
  obs_data['ssh'] = np.asarray(obs_data['ssh'])
  obs_data['ssh'] = obs_data['ssh'].astype(np.float64)*convert
  fill_val = 99.0
  obs_data['ssh'][obs_data['ssh'] >= fill_val] = np.nan

  obs_data['datetime'] = np.asarray(obs_data['datetime'],dtype='O')

  return obs_data

################################################################################################
################################################################################################

def read_station_file(station_file,stations={}):

  # Initialize stations dictionary
  if len(stations) == 0:
    stations['name'] = []
    stations['lon'] = []
    stations['lat'] = []

  # Read in stations names and location
  f = open(station_file)
  lines = f.read().splitlines()
  for sta in lines:
    val = sta.split()
    stations['name'].append(val[2].strip("'"))
    stations['lon'].append(float(val[0]))
    stations['lat'].append(float(val[1]))
  nstations = len(stations['name'])
  stations['lon'] = np.asarray(stations['lon'])
  stations['lat'] = np.asarray(stations['lat'])

  return stations

################################################################################################
################################################################################################

if __name__ == '__main__':

  parser = ap.ArgumentParser()
  parser.add_argument('--diff', dest='diff', action='store_true')
  parser.add_argument('--all', dest='all_stations', action='store_true')
  args = parser.parse_args()

  pwd = os.getcwd()

  # Read config file
  f = open(pwd+'/plot_ssh.config')
  cfg = yaml.load(f)
  pprint.pprint(cfg)

  # Read in model point output data and create kd-tree
  data = {}
  tree = {}

  for run in cfg['pointstats_file']:
    data[run] = read_pointstats(cfg['pointstats_file'][run])
    points = np.vstack((data[run]['lon'],data[run]['lat'])).T
    tree[run] = spatial.KDTree(points)

  M = [int(i) for i in cfg['max_date'].split()]
  m = [int(i) for i in cfg['min_date'].split()]



  # Read in station file
  stations = read_station_file(cfg['stations_file'])
  keep = ['8534720', '8536110', '8551910', '8557380']


  for i,sta in enumerate(stations['name']):

    if not args.all_stations:
        if sta not in keep: continue

    print(sta)

    # Check if observation file exists
    obs_file = ""
    obs_file_check = cfg['obs_direc']+sta+'_'+cfg['year']+'.txt'
    if os.path.isfile(obs_file_check):
      obs_file = obs_file_check

    obs_file_check = cfg['obs_direc']+sta+'.txt'
    if os.path.isfile(obs_file_check):
      obs_file = obs_file_check

    # Skip to next iteration if not found
    if not obs_file:
      continue

    # Read in observed data and get coordinates
    obs_data = read_station_data(obs_file,cfg['min_date'],cfg['max_date'])
    sta_lon = stations['lon'][i]
    sta_lat = stations['lat'][i]

    # Create figure
    if args.diff:
      fig = plt.figure(figsize=[6,6])
      gs = gridspec.GridSpec(nrows=3,ncols=2,figure=fig)
    else:
      fig = plt.figure(figsize=[6,4])
      gs = gridspec.GridSpec(nrows=2,ncols=2,figure=fig)

    # Plot observation station location
    ax1 = fig.add_subplot(gs[0,0], projection=ccrs.PlateCarree())
    ax1.set_extent([sta_lon-10.0, sta_lon+10.00, sta_lat-7.0 , sta_lat+7.0], crs=ccrs.PlateCarree())
    ax1.add_feature(cfeature.LAND, zorder=100)
    ax1.add_feature(cfeature.LAKES, alpha=0.5, zorder=101)
    ax1.coastlines('50m', zorder=101)
    ax1.plot(sta_lon,sta_lat,'C0o', zorder=102)

    # Plot local observation station location
    ax2 = fig.add_subplot(gs[0,1], projection=ccrs.PlateCarree())
    ax2.set_extent([sta_lon-2.5, sta_lon+2.5, sta_lat-1.75 , sta_lat+1.75], crs=ccrs.PlateCarree())
    ax2.add_feature(cfeature.LAND, zorder=100)
    ax2.add_feature(cfeature.LAKES, alpha=0.5, zorder=101)
    ax2.coastlines('50m', zorder=101)
    ax2.plot(sta_lon,sta_lat,'C0o', zorder=102)

    # Plot observed data
    ax3 = fig.add_subplot(gs[1,:])
    l1, = ax3.plot(obs_data['datetime'],obs_data['ssh'],'C0-')
    labels = ['observed']
    lines = [l1]

    for i,run in enumerate(data):
      Mindex = np.where(data[run]['datetime'] == datetime.datetime(M[0], M[1], M[2], M[3], M[4]))[0][0]
      mindex = np.where(data[run]['datetime'] == datetime.datetime(m[0], m[1], m[2], m[3], m[4]))[0][0]

      # Find closest output point to station location
      d,idx = tree[run].query(np.asarray([sta_lon,sta_lat]))

      # Plot output point location
      ax1.plot(data[run]['lon'][idx],data[run]['lat'][idx],'C'+str(i+1)+'o')
      ax2.plot(data[run]['lon'][idx],data[run]['lat'][idx],'C'+str(i+1)+'o')

      # Plot modelled data
      dateIndex1 = np.where(data[run]['datetime'] == datetime.datetime(2012, 10, 15, 0, 0))[0][0]
      dateIndex2 = np.where(data[run]['datetime'] == datetime.datetime(2012, 10, 27, 0, 0))[0][0]
      avgBeforeStorm = np.mean( data[run]['ssh'][dateIndex1:dateIndex2,idx] )
      data[run]['ssh'][:,idx] = data[run]['ssh'][:,idx] - avgBeforeStorm
      l2, = ax3.plot(data[run]['datetime'],data[run]['ssh'][:,idx],'C'+str(i+1)+'-')
      lines.append(l2)

      obs_dates = [date.timestamp() for date in obs_data['datetime']]
      model_dates = [date.timestamp() for date in data[run]['datetime']]

      #print(obs_data['ssh'])
      #print(data[run]['ssh'][:,idx])
      interpObsDat = np.interp(model_dates, obs_dates, obs_data['ssh'])
      #print(interpObsDat)
      #print(np.array(data[run]['ssh'][:,idx]))
      #print(model_dates[mindex:Mindex])
      rmsErr = np.sqrt(np.mean(np.square(interpObsDat[mindex:Mindex] - data[run]['ssh'][mindex:Mindex,idx])))
      data[run]['err'+str(idx)] = rmsErr
      labels.append(run)
      #labels.append(run + ' {:.3f}'.format(rmsErr))

    # Set figure labels and axis properties and save
    if not args.diff:
      ax3.set_xlabel('time')
    ax3.set_ylabel('ssh (m)')
    ax3.set_xlim([datetime.datetime.strptime(cfg['min_date'],'%Y %m %d %H %M'),datetime.datetime.strptime(cfg['max_date'],'%Y %m %d %H %M')])
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    
    if args.diff:
      ax4 = fig.add_subplot(gs[2,:])
      d,idx = tree['RK4'].query(np.asarray([sta_lon,sta_lat]))
      l3 = ax4.plot( data['RK4']['datetime'],
                     np.absolute( data['RK4']['ssh'][:, idx] - data['LTS3']['ssh'][:, idx] ),
                    '#8f1402'
                   )
      print('Max |RK4 - LTS3| = {}'.format(np.max(np.absolute( data['RK4']['ssh'][:, idx] - data['LTS3']['ssh'][:, idx] ))))
      ax4.set_xlim([datetime.datetime.strptime(cfg['min_date'],'%Y %m %d %H %M'),datetime.datetime.strptime(cfg['max_date'],'%Y %m %d %H %M')])
      ax4.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
      ax4.set_ylabel('| RK4 - LTS3 |')
      ax4.set_yscale('log')
      ax4.set_ylim([10**-7, 10**-1])
      ax4.set_xlabel('time')
   
    
    lgd = plt.legend(lines,labels,loc=9,bbox_to_anchor=(0.5,-0.5),ncol=3,fancybox=False,edgecolor='k')
    st = plt.suptitle('Station '+sta,y = 1.025,fontsize=16)
    fig.tight_layout()
    fig.savefig(sta+'.pdf',bbox_inches='tight',bbox_extra_artists=(lgd,st,))
    plt.close()


  for run in data:
    err = 0
    for station in stations['name']:
      if not args.all_stations:
        if station not in keep: continue
      d,idx = tree[run].query(np.asarray([sta_lon,sta_lat]))
      err += data[run]['err'+str(idx)]
    err = err / len(stations['name'])
    data[run]['avgErr'] = err
    print('{} err = {}'.format(run, data[run]['avgErr']))


  runs = [run for run in data]
  errs = [data[run]['avgErr'] for run in data]
  strErrs = ['{:.3f}'.format(err) for err in errs]

  fig = plt.figure()
  plt.bar(runs, errs, width=0.6)
  for i in range(len(runs)):
    plt.text(i, errs[i]+0.0005, strErrs[i], ha='center')
  ax = plt.gca()
  #ax.set_ylim([0, 0.8])
  plt.setp(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
  plt.xlabel('mesh')
  plt.ylabel('Avg RMS error across stations')
  plt.tight_layout()
  fig.savefig('avgErrs.pdf')

