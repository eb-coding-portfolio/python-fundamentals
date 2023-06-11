import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

file_path = r'C:\Users\Eric C. Balduf\OneDrive\Documents\my-local-repo\python-fundamentals\Data\Redfin\redfin_metro_market_tracker.tsv000'

df_metro = pd.read_csv(file_path, delimiter='\t')

summary_stats = df_metro.describe().round(2)

#print(summary_stats)

desired_stats = summary_stats.loc[['min', '25%', '50%', '75%', 'max']]

columns_to_drop = ['period_duration', 'region_type_id', 'table_id', 'city', 'state', 'property_type_id', 'parent_metro_region_metro_code']

desired_stats_final = desired_stats.drop(columns=columns_to_drop)

column_types = df_metro.dtypes

date_columns = ['period_begin', 'period_end', 'last_updated']

df_metro[date_columns] = df_metro[date_columns].apply(pd.to_datetime)

column_types = df_metro.dtypes

desired_stats_final.to_csv(r'C:\Users\Eric C. Balduf\OneDrive\Documents\df_metro_summary_stats.csv', index_label='Stat')

excel_writer = pd.ExcelWriter(r'C:\Users\Eric C. Balduf\OneDrive\Documents\value_counts_results.xlsx', engine='openpyxl')



for column in df_metro.columns:
    if pd.api.types.is_object_dtype(column_types[column]) or pd.api.types.is_categorical_dtype(column_types[column]):
        value_counts = df_metro[column].value_counts().reset_index()
        sheet_name = column
        value_counts.to_excel(excel_writer, sheet_name=sheet_name, index=False)

excel_writer._save()

null_counts = df_metro.isnull().sum()
null_counts = null_counts.reset_index()
null_counts.columns = ['Column', 'Count']

null_counts.to_excel(excel_writer, sheet_name="null_counts", index=False)


null_counts_pct = (df_metro.isnull().sum() / len(df_metro)) * 100
null_counts_pct = null_counts_pct.reset_index()
null_counts_pct.columns = ['Column', 'Percent of Total Rows']
null_counts_pct = null_counts_pct.sort_values(ascending=False, by='Percent of Total Rows')

null_counts_pct.to_excel(excel_writer, sheet_name="null_counts_pct", index=False)

excel_writer._save()

num_list = []
for col in df_metro.columns:

    if pd.api.types.is_numeric_dtype(df_metro[col]):
        num_list.append(col)

subset_corr_df = df_metro[num_list].drop(columns=columns_to_drop)

exclude_columns = [col for col in subset_corr_df.columns if 'mom' in col or 'yoy' in col]

subset_corr_df_filtered = subset_corr_df.loc[:, ~subset_corr_df.columns.isin(exclude_columns)]


correlation_matrix = subset_corr_df_filtered.corr()

sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')

plt.title('Correlation Matrix')


plt.show()


#Next    4. for all categorical variables, plot a bar chart



