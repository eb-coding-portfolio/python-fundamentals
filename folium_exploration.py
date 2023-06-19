import pandas as pd
import folium
import geocoder
import pandas as pd

state_data_url = 'https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/state_market_tracker.tsv000.gz'
redfin_df_states = pd.read_csv(state_data_url, sep='\t', compression='gzip')
redfin_df_states = redfin_df_states[redfin_df_states['property_type'] == 'All Residential']

date_columns = ['period_end', 'period_begin']

redfin_df_states[date_columns] = redfin_df_states[date_columns].apply(pd.to_datetime)



max_dates = redfin_df_states.groupby('region')['period_end'].max().reset_index()

merged_df = pd.merge(redfin_df_states, max_dates, on=['region', 'period_end'], suffixes=('_left', '_right'), how='inner')


result_df = merged_df[['region','period_end','median_sale_price_yoy']]


#result_df.to_csv(r'C:\Users\Eric C. Balduf\result.csv', index=False)

#print(redfin_df_states.dtypes)




# my_map = folium.Map(location=['42.3522', '-71.0564'], zoom_start=17, width=500, control_scale=True)
#
# hvp_location = geocoder.osm('One Financial Center, Boston, MA 02110')
#
# folium.Marker([hvp_location.lat, hvp_location.lng], popup='HarbourVest Partners').add_to(my_map)
#
# my_map.save('map.html')
#
us_map = folium.Map(location=[37.0902, -95.7129], zoom_start=5)

# Create a choropleth map layer
folium.Choropleth(
    geo_data='https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_040_00_500k.json',  # GeoJSON file for state boundaries
    name='choropleth',
    data=result_df,
    columns=['region', 'median_sale_price_yoy'],  # Columns from your dataset
    key_on='feature.properties.NAME',
    fill_color='YlOrRd',  # Color scheme (you can choose from various options)
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='median_sale_price_yoy'  # Legend title
).add_to(us_map)

folium.LayerControl().add_to(us_map)

us_map.save('us_map.html')
