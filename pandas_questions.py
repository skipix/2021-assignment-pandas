"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv('data/referendum.csv', sep=";")
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    reg = regions[['code', 'name']].rename(
        columns={'code': 'code_reg', 'name': 'name_reg'})
    dep = departments[['region_code', 'code', 'name']].rename(
        columns={'region_code': 'code_reg',
                 'code': 'code_dep', 'name': 'name_dep'})
    return pd.merge(dep, reg, on="code_reg", how='left')


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['code_dep'] = referendum['Department code'].str.zfill(2)
    ans = pd.merge(referendum, regions_and_departments,
                   on='code_dep', how='left')
    ans = ans.dropna()
    return ans


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    ans = referendum_and_areas.groupby(
        ['code_reg', 'name_reg']).sum().reset_index().set_index('code_reg')
    ans = ans.drop(columns="Town code")
    return ans


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    with open('data/regions.geojson') as france:
        df = gpd.read_file(france)
        df.rename(columns={'code': 'code_reg'}, inplace=True)
        df.set_index('code_reg', inplace=True)
        ans = pd.merge(df, referendum_result_by_regions, on='code_reg')
        ans['ratio'] = ans['Choice A'] / (ans['Choice A'] + ans['Choice B'])
        ans.plot('ratio', legend=True)
    return ans.reset_index()


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
