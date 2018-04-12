from grads.ganum import GaNum
import numpy as np
import pandas as pd
ga = GaNum(Bin='grads')
ga.open('/Users/drigo/Ocean/4_diplom/discharge_in_channel/relief/hhq.ctl', Quiet=False)
h=ga.exp('h')
lat = h.grid.lat
lon = h.grid.lon
val = ga.exp('h').data
lat_=[]
lon_=[]
for j in range(len(lat)):
    for k in range(len(lon)):
            lat_.append(lat[j])
            lon_.append(lon[k])
data = np.column_stack((lat_, lon_,val.ravel()))
df = pd.DataFrame(data=data,columns=['Lat', 'Long', 'Depth'])
df.to_csv('hhq.dat', sep = '\t')