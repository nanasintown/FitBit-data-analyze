from typing import get_type_hints
import gather_keys_oauth2 as Oauth2
import fitbit
import pandas as pd 
import datetime
import json
import numpy as np
'''
CLIENT_ID='23QZTB'
CLIENT_SECRET='8b8f778cd7b25dd6e6e3c07e62f3ac59'
ACCESS_TOKEN = eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1FaVEIiLCJzdWIiOiJCSkZRWEQiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJ3aHIgd3BybyB3bnV0IHdzbGUgd2VjZyB3c29jIHdhY3Qgd294eSB3dGVtIHd3ZWkgd2NmIHdzZXQgd3JlcyB3bG9jIiwiZXhwIjoxNjg0MjkzNDMxLCJpYXQiOjE2ODQyNjQ2MzF9.pZ_XhOxPfnw00uxbJsZU19TIEf39ruCmA2UmzzHbs-I
REFRESH_TOKEN = 9d90392d0b53a9c3db6d975858cb01829c3e7d92cdb6cf3382fa49895c256446
'''
# Watch_Request object handles authentication and http requests for biometrical data.
# get-functions try to handle the cases when no data is not available (E.g. watch was not worn) by filling nodata with NaN's
# With the API, you can do up to 150 http requests per user / hour. If you doo too many you are going to get a HTTPTooManyRequests -error.
class Watch_Request(object):
    def __init__(self, CLIENT_ID, CLIENT_SECRET):
            server=Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
            server.browser_authorize()
            ACCESS_TOKEN=str(server.fitbit.client.session.token['access_token'])
            REFRESH_TOKEN=str(server.fitbit.client.session.token['refresh_token'])

            self.auth2_client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)

    ## Returns heart rate per second as a dataframe
    def get_hrate(self, s_date, e_date):

        date_list = []
        df_list = []
        allDates = pd.date_range(start=s_date, end = e_date)

        for oneDate in allDates:
            oneDate = oneDate.date().strftime("%Y-%m-%d")
            oneDayData = self.auth2_client.intraday_time_series('activities/heart', base_date=oneDate, detail_level='1sec')
            df = pd.DataFrame(oneDayData['activities-heart-intraday']['dataset'])
            date_list.append(oneDate)
            df_list.append(df)
            
        final_df_list = []

        for date, df in zip(date_list, df_list):
            if len(df) == 0:
                continue
            df.loc[:, 'date'] = pd.to_datetime(date)
            final_df_list.append(df)

        final_df = pd.concat(final_df_list, axis = 0)

        ## Optional Making of the data have more detailed timestamp (day and hour instead of day)
        hoursDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.hour.apply(lambda x: datetime.timedelta(hours = x))
        minutesDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.minute.apply(lambda x: datetime.timedelta(minutes = x))
        secondsDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.second.apply(lambda x: datetime.timedelta(seconds = x))

        # Getting the date to also have the time of the day
        final_df['date'] = final_df['date'] + hoursDelta + minutesDelta + secondsDelta

        return final_df.drop(columns=['time'])
    

    ## returns spent calories per minute
    def get_calories(self, s_date, e_date):

        date_list = []
        df_list = []
        allDates = pd.date_range(start=s_date, end = e_date)

        for oneDate in allDates:
            oneDate = oneDate.date().strftime("%Y-%m-%d")
            oneDayData = self.auth2_client.intraday_time_series('activities/calories', base_date=oneDate, detail_level='1min')
            df = pd.DataFrame(oneDayData["activities-calories"])
            date_list.append(oneDate)
            df_list.append(df)

        final_df = pd.concat(df_list, axis = 0)
        # print(final_df)
        return final_df

    ## returns steps per minute
    def get_steps(self, s_date, e_date):
        date_list = []
        df_list = []
        allDates = pd.date_range(start=s_date, end = e_date)

        for oneDate in allDates:
            oneDate = oneDate.date().strftime("%Y-%m-%d")
            oneDayData = self.auth2_client.intraday_time_series('activities/steps', base_date=oneDate, detail_level='1min')
            df = pd.DataFrame(oneDayData["activities-steps"])
            date_list.append(oneDate)
            df_list.append(df)

        final_df = pd.concat(df_list, axis = 0)
        return final_df
    
    ## Returns activity level per minute.
    ## Level field reflects calculated activity level for that time period ( 0 - sedentary; 1 - lightly active; 2 - fairly active; 3 - very active.)
    def get_activity(self, s_date, e_date):
        date_list = []
        df_list = []
        allDates = pd.date_range(start=s_date, end = e_date)

        for oneDate in allDates:
            oneDate = oneDate.date().strftime("%Y-%m-%d")
            oneDayData = self.auth2_client.intraday_time_series('activities/calories', base_date=oneDate, detail_level='1min')
            
            df = pd.DataFrame(oneDayData['activities-calories-intraday']['dataset'])
            date_list.append(oneDate)
            df_list.append(df)

        final_df_list = []

        for date, df in zip(date_list, df_list):
            if len(df) == 0:
                continue
            df.loc[:, 'date'] = pd.to_datetime(date)
            final_df_list.append(df)

        final_df = pd.concat(final_df_list, axis = 0)
        hoursDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.hour.apply(lambda x: datetime.timedelta(hours = x))
        minutesDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.minute.apply(lambda x: datetime.timedelta(minutes = x))
        secondsDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.second.apply(lambda x: datetime.timedelta(seconds = x))

        final_df['date'] = final_df['date'] + hoursDelta + minutesDelta + secondsDelta
        return final_df.drop(columns=['time', 'mets', 'value'])

    def get_resting_heart(self, s_date, e_date):
        # startTime is first date of data that I want. 
        # You will need to modify for the date you want your data to start
        date_list = []
        df_list = []
        allDates = pd.date_range(start=s_date, end = e_date)
        for oneDate in allDates:
            
            oneDate = oneDate.date().strftime("%Y-%m-%d")
            
            oneDayData = self.auth2_client.intraday_time_series('activities/heart', base_date=oneDate, detail_level='1min')
            try:
                rhr = oneDayData['activities-heart'][0]['value']['restingHeartRate']
            except KeyError:
                rhr = np.nan
            data = [[oneDate, rhr]]
            df = pd.DataFrame(data, columns=['date', 'restingHeartRate'])#['restingHeartRate'])
            date_list.append(oneDate)
            df_list.append(df)
        
        final_df_list = []

        for date, df in zip(date_list, df_list):
            if len(df) == 0:
                continue
            df.loc[:, 'date'] = pd.to_datetime(date)
            final_df_list.append(df)
        
        final_df = pd.concat(final_df_list, axis = 0)
        '''
        hoursDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.hour.apply(lambda x: datetime.timedelta(hours = x))
        minutesDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.minute.apply(lambda x: datetime.timedelta(minutes = x))
        secondsDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.second.apply(lambda x: datetime.timedelta(seconds = x))
        
        final_df['date'] = final_df['date'] + hoursDelta + minutesDelta + secondsDelta
        '''
        return final_df#.drop(columns=['time', 'mets', 'value'])
    
    '''
    Other stuff that can be pulled with intraday-time-series:
    activities/calories
    activities/steps
    activities/distance
    activities/floors
    activities/elevation


    Instead of using that precise intraday-time-series we can extract data using
    the "normal" time-series method, which gives us this less time-dense data:

    activities/calories
    activities/caloriesBMR
    activities/steps
    activities/distance
    activities/floors
    activities/elevation
    activities/minutesSedentary
    activities/minutesLightlyActive
    activities/minutesFairlyActive
    activities/minutesVeryActive
    activities/activityCalories

    Especially these "minutes Lightly / Fairly / Very - active" looks interesting,
    but FitBit does notexplain anywhere what is considered E.g. "very active", 

    https://dev.fitbit.com/build/reference/web-api/activity/#activity-types
    '''

if __name__ == "__main__":

    #Create object for Fitbit watch data extraction:
    wr = Watch_Request(CLIENT_ID="23QZTB", CLIENT_SECRET="8b8f778cd7b25dd6e6e3c07e62f3ac59")
    stepdata = wr.get_steps("05-05-2023", "05-22-2023")
    caloriesData = wr.get_calories("05-05-2023", "05-20-2023")
    print(stepdata)
    print(caloriesData)
    