import gather_keys_oauth2 as Oauth2
import fitbit
import pandas as pd 
import numpy as np
import requests
'''
CLIENT_ID='23QZTB'
CLIENT_SECRET = '8b8f778cd7b25dd6e6e3c07e62f3ac59'
REFRESH_TOKEN = 9d90392d0b53a9c3db6d975858cb01829c3e7d92cdb6cf3382fa49895c256446
'''
# Watch_Request object handles authentication and http requests for biometrical data.
# get-functions try to handle the cases when no data is not available (E.g. watch was not worn) by filling nodata with NaN's
# With the API, you can do up to 150 http requests per user / hour. If you doo too many you are going to get a HTTPTooManyRequests -error.
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1FaVEIiLCJzdWIiOiJCSkZRWEQiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJ3aHIgd3BybyB3bnV0IHdzbGUgd2VjZyB3c29jIHdhY3Qgd294eSB3dGVtIHd3ZWkgd2NmIHdzZXQgd2xvYyB3cmVzIiwiZXhwIjoxNjg1Mjk1NDYwLCJpYXQiOjE2ODUyNjY2NjB9.JJP2dKCT2u3tnsUiT0YMdAEYfiOu-bUZO8ZulQvKh-U"

class Watch_Request(object):
    def __init__(self, CLIENT_ID, CLIENT_SECRET):
            server=Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
            server.browser_authorize()
            ACCESS_TOKEN=str(server.fitbit.client.session.token['access_token'])
            REFRESH_TOKEN=str(server.fitbit.client.session.token['refresh_token'])

            self.auth2_client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)

    ## Returns heart rate per second as a dataframe
    def get_hrate(self, startdate, enddate):
        """
        https://api.fitbit.com/1/user/-/activities/heart/date/2023-05-27/1d.json
        1d = period. Supported 1d-7d-10d-1w-1m
        """
        df_list = []
        header = {"Authorization": "Bearer {}".format(ACCESS_TOKEN)}
        all_dates = pd.date_range(start=startdate, end=enddate)
        for day in all_dates:
            day = day.date().strftime("%Y-%m-%d")
            response = requests.get(f"https://api.fitbit.com/1/user/-/activities/heart/date/{day}/1d.json", headers=header).json()
            # delete unnecessary element
            del response["activities-heart"]
            data = response["activities-heart-intraday"]['dataset']
            df = pd.DataFrame(data)
            df_list.append(df)
        return pd.concat(df_list, axis=0)

    ## returns spent calories per minute
    def get_calories(self, s_date, e_date):
        df_list = []
        allDates = pd.date_range(start=s_date, end = e_date)

        for oneDate in allDates:
            oneDate = oneDate.date().strftime("%Y-%m-%d")
            oneDayData = self.auth2_client.intraday_time_series('activities/calories', base_date=oneDate, detail_level='1min')
            df = pd.DataFrame(oneDayData["activities-calories"])
            df_list.append(df)

        final_df = pd.concat(df_list, axis = 0)
        return final_df

    ## returns steps per minute
    def get_steps(self, s_date, e_date):
        df_list = []
        allDates = pd.date_range(start=s_date, end = e_date)

        for oneDate in allDates:
            oneDate = oneDate.date().strftime("%Y-%m-%d")
            oneDayData = self.auth2_client.intraday_time_series('activities/steps', base_date=oneDate, detail_level='1min')
            df = pd.DataFrame(oneDayData["activities-steps"])
            df_list.append(df)

        final_df = pd.concat(df_list, axis = 0)
        return final_df

def save_as_csv(filename, data):
    path = "fitbit-data/"
    data.to_csv(path + filename, index=False)

if __name__ == "__main__":

    #Create object for Fitbit watch data extraction:
    wr = Watch_Request(CLIENT_ID="23QZTB", CLIENT_SECRET="8b8f778cd7b25dd6e6e3c07e62f3ac59")
    
    # stepdata = wr.get_steps("04-17-2023", "05-27-2023")
    # save_as_csv("steps_data.csv", stepdata)

    # heart_rate = wr.get_hrate("2023-05-05", "2023-05-26")
    # save_as_csv("heart_rate_may.csv", heart_rate)

    # calories_data = wr.get_calories("04-17-2023", "05-27-2023")
    # save_as_csv("calories_data.csv", calories_data)
