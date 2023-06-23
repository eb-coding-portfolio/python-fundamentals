import folium
import geocoder
import sys
import pandas as pd
import json as j

def ingest_data(source, file_url):
    """


    :param source: parameter to pass in to tell the function where to source the data from. only options are 'labor' for bureau of labor
    statistics data, 'redfin' for housing market data, 'permits' for census building permits data, and 'pop' for population data from the census
    :param file_url: this should be the file url on the website where you can click to download the file. This should be the full url, no need to modify.
    :return: returns a dataframe of the source data complete unmodified
    """
    source_df = pd.DataFrame()
    if source.lower() not in ('labor','redfin','permits','pop'):
        print(f'This source is not supported, please enter labor, redfin, permits, or pop ')
        sys.exit()
    elif source.lower() == 'redfin':
       source_df = pd.read_csv(file_url, sep='\t', compression='gzip')
    elif source.lower() == 'labor':
        pass
    elif source.lower() == 'permits':
        pass
    elif source.lower() == 'pop':
        pass
    return source_df

def get_max(metric, input_max_df):
    """
    :param metric: metric that you would like to get the latest value from and see render in the folium map
    :param input_max_df: this is the input data frame to perform operations on
    :return: dataframe to use in folium
    """

    max_dates = input_max_df.groupby('region')['period_end'].max().reset_index()
    merged_df = pd.merge(input_max_df, max_dates, on=['region', 'period_end'], suffixes=('_left', '_right'), how='inner')

    return merged_df[['region', 'period_end', metric]]

def create_choropleth_map(geo_json, map_metric, map_df):
    """

    :param geo_json: link to geo json file to us as lat/long boundaries for states
    :param metric: the metric that we will use to shade the US map by
    :param map_df: dataframe for the map to us to plot the metric
    :return: folium map object that plots that shades the map of the us by the metric provided
    """

    map = folium.Map(location=[37.0902, -95.7129], zoom_start=5)

    # # Create a choropleth map layer
    folium.Choropleth(
          geo_data=geo_json,  # GeoJSON file for state boundaries
          name='choropleth',
          data=map_df,
          columns=['region', map_metric],  # Columns from your dataset
          key_on='feature.properties.NAME',
          fill_color='YlGnBu',  # Color scheme (you can choose from various options)
          fill_opacity=0.7,
          line_opacity=0.2,
          legend_name=map_metric  # Legend title
      ).add_to(map)
    #
    folium.TileLayer('Stamen Toner').add_to(map)
    folium.LayerControl().add_to(map)
    return map


# def format_us_map(map_obj, json):
#     # Load the GeoJSON file of US state boundaries
#
#     us_states_geojson =  json
#
#     # Filter the GeoJSON features to include only the 50 states
#     filtered_features = [feature for feature in us_states_geojson['features'] if
#                          feature['properties']['region'] == 'United States']
#
#     # Create a new GeoJSON object with only the filtered features
#     filtered_geojson = {
#         'type': 'FeatureCollection',
#         'features': filtered_features
#     }
#
#     # Remove existing GeoJSON layer from the map
#     for layer in map_obj._children:
#         if isinstance(layer, folium.GeoJson):
#             map_obj.remove_layer(layer)
#
#     # Add the filtered GeoJSON layer to the map
#     folium.GeoJson(filtered_geojson).add_to(map_obj)
#
#     # Return the updated map object
#     return map_obj



working_df = ingest_data('redfin','https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/state_market_tracker.tsv000.gz')

working_df = working_df[working_df['property_type'] == 'All Residential']
date_columns = ['period_end', 'period_begin']
working_df[date_columns] = working_df[date_columns].apply(pd.to_datetime)

metric_columns = [col for col in working_df.columns if working_df[col].dtype == 'float64']
print(metric_columns)
metric = input("What metric would you like to analyze? (select one from list above) ").strip().lower()

folium_df = get_max(metric, working_df)

folium_df.to_csv(r'C:\Users\ebald\Documents\Real Estate Application\results.csv', index=False)

geo_json = 'https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_040_00_500k.json'


us_map = create_choropleth_map(geo_json, metric, folium_df)

formated_us_map = format_us_map(us_map, geo_json)

formated_us_map.save('us_map.html')


#
# # Create a choropleth map layer
# folium.Choropleth(
#     geo_data='https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_040_00_500k.json',  # GeoJSON file for state boundaries
#     name='choropleth',
#     data=result_df,
#     columns=['region', 'median_sale_price_yoy'],  # Columns from your dataset
#     key_on='feature.properties.NAME',
#     fill_color='YlOrRd',  # Color scheme (you can choose from various options)
#     fill_opacity=0.7,
#     line_opacity=0.2,
#     legend_name='median_sale_price_yoy'  # Legend title
# ).add_to(us_map)
#
# folium.LayerControl().add_to(us_map)
#
# us_map.save('us_map.html')
