"""Install SynMax Python Client"""

pip install --upgrade synmax-api-python-client

"""Install other Dependencies"""

pip install wheel pandas tqdm plotly-geo plotly geopandas==0.8.1 pyshp shapely

"""Query the production data"""

from synmax.hyperion import HyperionApiClient, ApiPayload
import calendar
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

access_token = '*****************************'
client = HyperionApiClient(access_token=access_token)

payload = ApiPayload(start_date='2021-01-01', end_date='2022-09-01', state_code='TX', production_month=2)
df = client.production_by_well(payload)

"""convert to mcf/d"""

def make_mcf_d(x):
  date_ = pd.to_datetime(x.date)
  days = calendar.monthlen(date_.year, date_.month)

  return x.gas_monthly/days

df['gas_daily'] = df.apply(make_mcf_d, axis=1)

"""examine county-level histograms"""

fig = px.histogram(df[df.county=='Midland'], x='gas_daily')
fig.show()

"""calculate average per county"""

county_df = df[['state_ab', 'county', 'gas_daily']].groupby(['state_ab', 'county'], as_index=False).mean()

"""Get FIPS code Lookup Table"""

fips_df = pd.read_csv('https://raw.githubusercontent.com/kjhealy/fips-codes/master/state_and_county_fips_master.csv')
fips_df['name'] = fips_df.apply(lambda x: x['name'].replace(' County', '').replace(' Parish', ''), axis=1)
fips_df.columns = ['fips', 'county', 'state']

"""merge fips_df with county_df"""
county_df = county_df.merge(fips_df[fips_df.state.=='TX'], how='right', left_on=['state_ab','county'], right_on=['state', 'county'])
county_df['gas_daily'] = county_df['gas_daily'].fillna(0)

"""Create county map"""

fig = ff.create_choropleth(fips=county_df.fips.tolist(), 
                           values=county_df.gas_daily.tolist(),
                           county_outline={'color': 'rgb(255,255,255)', 'width': 0.5},
                           scope=['TX'],
                           binning_endpoints=[75, 125, 250, 500, 1000, 2000, 4000, 8000, 16000, 32000])
fig.show()
