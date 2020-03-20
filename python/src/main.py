import os

import pandas as pd

from common.directions_api_utils import request_directions
from common.geospatial_utils import haversine_np

GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']


def file_to_dataframe(path: str) -> pd.DataFrame(columns=["vin", "timestamp", "lon", "lat"]):
    """
    Read a .csv - file from the input path and return a dataframe
    """

    df = pd.read_table(path, header=None, names=["vin", "timestamp", "lon", "lat"], sep=",")

    if len(df) > 200:
        df = df.assign(time=pd.DatetimeIndex(df["timestamp"]))
        df.drop('timestamp', axis=1, inplace=True)
        df.drop_duplicates(inplace=True)
        return df.reset_index(drop=True)


def define_journey(df):
    """
    If the time between two consecutive coordinates is more than 1000 seconds, a new trip/journes starts
    """
    df = df.assign(journey_id=(df["dt"] >= 1000).cumsum() + 1)
    df.loc[df['dt'] >= 1000, ['dt']] = 0
    return df.fillna(0)


def enrich_with_google_api(df):
    enriched_df = pd.DataFrame()
    for index, row in df.iterrows():
        if row['dt'] > 20:
            result = request_directions(lat1=df.loc[index - 1].lat, lng_1=df.loc[index - 1].lon, lat2=row.lat,
                                        lng_2=row.lon, api_key=GOOGLE_API_KEY)
            for coords in result['routes'][0]['legs'][0]['steps']:
                new_point = {'vin': row.vin,
                             'lat': coords['end_location']['lat'],
                             'lon': coords['end_location']['lng'],
                             'interpolation_group': row.interpolation_group,
                             'time': row.time}
                enriched_df = enriched_df.append(new_point, ignore_index=True)
        enriched_df = enriched_df.append(row)
    return enriched_df.reset_index(drop=True)


def append_cum_mileage(df):
    df = df.assign(mileage=haversine_np(
        df.lon,
        df.lat,
        df.lon.shift(),
        df.lat.shift()))
    df = df.assign(mileage_cum_sum=df.groupby('interpolation_group').mileage.cumsum())
    return df


def interpolate_time_of_enriched_gps_points(group_df):
    result = pd.DataFrame()
    total_distance = group_df.mileage.sum()
    group_df = group_df.assign(
        seconds=(group_df.dt.max() - group_df.mileage_cum_sum / total_distance * group_df.dt.max()))
    for index, row in group_df.iterrows():
        try:
            row.time = group_df.time.max() - pd.Timedelta(seconds=row.seconds)
            result = result.append(row)
        except:
            pass
    return result


def increase_gps_points_control_flow(df):
    df = df.assign(dt=df.time.diff().dt.total_seconds())
    df = df.assign(interpolation_group=(df["dt"] > 20).cumsum())
    enriched_df = enrich_with_google_api(df)
    mileage_df = append_cum_mileage(enriched_df)
    final_df = pd.DataFrame()
    for group, data in mileage_df.groupby('interpolation_group'):
        final_df = final_df.append(interpolate_time_of_enriched_gps_points(data))
    journey_df = define_journey(final_df)
    return journey_df.drop(['mileage', 'mileage_cum_sum', 'seconds', 'interpolation_group'], axis=1)


def main_control_flow(number_files):
    for file in os.listdir('./../data')[:number_files]:
        df = file_to_dataframe(path='{}/{}'.format('./../data', file))
        upsampled_data = increase_gps_points_control_flow(df[:10])

        # store the upsampled data to your database


if __name__ == "__main__":
    main_control_flow(number_files=1)
