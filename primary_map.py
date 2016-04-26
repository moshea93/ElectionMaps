#command line: python -m SimpleHTTPServer 8000
#browser: http://localhost:8000/vega_template.html
import pandas as pd
import json
import vincent

import json
import vincent

from vincent import *

state_topo = r'us_states.topo.json'
county_topo = r'us_counties.topo.json'
county_geo = r'us_counties.geo.json'

with open('us_counties.topo.json', 'r') as f:
	        get_id = json.load(f)

geometries = get_id['objects']['us_counties.geo']['geometries']
county_codes = [x['properties']['FIPS'] for x in geometries]
county_df = pd.DataFrame({'FIPS': county_codes})
#print county_df #3405 rows

votefrac_df = pd.read_csv('results.csv', header = 0, usecols = ['fips','candidate','vote_share'], dtype = {'fips': str})
votefrac_df.rename(columns = {'fips':'FIPS'}, inplace = True)
votefrac_df = votefrac_df[votefrac_df.candidate == 'Hillary Clinton']

merged = pd.merge(votefrac_df, county_df, on='FIPS', how='left')
merged = merged.fillna(value=0)
geo_data = [{'name': 'counties',
             'url': county_topo,
             'feature': 'us_counties.geo'},
            {'name': 'states',
             'url': state_topo,
             'feature': 'us_states.geo'}
	     ]

vis = vincent.Map(data=merged, geo_data=geo_data, scale=1500,
	        projection='albersUsa', data_bind='vote_share',
		data_key='FIPS', map_key={'counties': 'properties.FIPS'})
del vis.marks[1].properties.update
vis.marks[0].properties.enter.stroke.value = '#fff'
vis.marks[0].properties.enter.stroke_opacity = ValueRef(value=0.5)
vis.scales['color'].type = 'threshold'
vis.scales['color'].domain = [0,25,40,47,50,53,60,75]
vis.scales['color'].range = ['#053061', '#67001f', '#b2182b', '#f4a582', '#fddbc7', '#d1e5f0', '#92c5de', '#2166ac', '#053061']
vis.legend(title='Hillary Vote Share')
vis.to_json('vega.json', html_out = True, html_path='bar_template.html')
