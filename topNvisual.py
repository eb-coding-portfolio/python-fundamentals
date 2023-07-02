import pandas as pd
import matplotlib.pyplot as plt

file_location = r'C:\Users\Eric C. Balduf\OneDrive\Documents\my-local-repo\python-fundamentals\Data\Redfin\redfin_metro_market_tracker.tsv000'

source_df = pd.read_csv(file_location, sep='\t')


print(list(source_df['state_code'].unique()))
state_input = input('What state would you like to analyze? (choose one code from list above) ').strip().upper()

metric_columns = [col for col in source_df.columns if source_df[col].dtype == 'float64']
print(metric_columns)
metric = input("What metric would you like to analyze? (select one from list above) ").strip().lower()

print(list(source_df['property_type'].unique()))
prop_type_input = input('Which property type would you like to see the tto analyze (select one from list above) ').strip().lower()



def filter_df(state_code, metric_col, prop_type, input_df):

    input_df = input_df[(input_df['property_type'].str.lower() == prop_type) & (input_df['state_code'] == state_code)]

    max_dates = input_df.groupby('region')['period_end'].max().reset_index()
    merged_df = pd.merge(input_df, max_dates, on=['region', 'period_end'], suffixes=('_left', '_right'),
                         how='inner')

    return merged_df[['region', 'state_code', 'period_end', metric_col]].dropna(subset=metric_col)


filtered_df = filter_df(state_input, metric, prop_type_input, source_df)
filtered_df.to_csv(r'C:\Users\Eric C. Balduf\Documents\results.csv', index=False)
filtered_df['Rank'] = filtered_df[metric].rank(ascending=False)
df_ranked = filtered_df.sort_values(by='Rank', ascending=False)
df_ranked.to_csv(r'C:\Users\Eric C. Balduf\Documents\results2.csv', index=False)
top_5 = df_ranked.head(5).sort_values(by='Rank', ascending=True)
top_5.to_csv(r'C:\Users\Eric C. Balduf\Documents\results3.csv', index=False)
bottom_5 = df_ranked.tail(5).sort_values(by='Rank', ascending=True)
bottom_5.to_csv(r'C:\Users\Eric C. Balduf\Documents\results4.csv', index=False)

df_plot = pd.concat([top_5, bottom_5]).drop_duplicates()
df_plot = df_plot.sort_values(by='Rank', ascending=False)
cmap = plt.get_cmap('summer')
bar_colors = cmap(df_plot[metric] / df_plot[metric].max())  # Scale colors based on values

plt.barh(df_plot['region'], df_plot[metric], color=bar_colors)
for i, value in enumerate(df_plot[metric]):
    plt.text(value, i, str(round(value, 2)), va='center', color='blue' if value > 0 else 'red')

plt.title(f'Top 5 and Bottom 5 regions by {metric} for {state_input} and property type {prop_type_input}')
plt.xlabel(metric)
plt.show()