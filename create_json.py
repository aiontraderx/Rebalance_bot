import os
from datetime import datetime

import numpy as np
import pandas as pd
from config_bot import SETTING_FILE, PERSISTANT_PRICE_FILE, STATUS_FILE, list_setting
from exchange import Exchange
from utilis import _save_json, save_txt




def create_bot_zone(starts=float, gap=float, stop_zone_sell=float, stop_zone_buy=float):
    #     starts = 1800
    #     gap =  0.05 ## zone

    #     stop_zones =500
    #     stop_zone_buy= 3200

    gap_p = starts * gap
    min_range = np.arange(starts, (stop_zone_sell), -gap_p)
    max_range = np.arange(starts, (stop_zone_buy), gap_p)
    all_range = np.concatenate((min_range, max_range), axis=None)
    df = pd.DataFrame(all_range, columns=['price'])

    df.drop_duplicates(inplace=True)
    df.sort_values('price', ascending=False, inplace=True)
    df.reset_index(inplace=True)
    df.drop(columns='index', inplace=True)

    df['diff'] = (df['price'] - starts) / starts
    return df


def rebal_plans(df, fix_values=1000, start_cash=1000, max_zone=0.5, min_zone=0.5, sub_zone=0.3):
    df['value'] = (df['diff'] * start_cash) + start_cash
    df['unit'] = 0.0
    df['adj_cash'] = 0.0
    df['free_cash'] = 0.0
    df['start_cash'] = start_cash
    df['asset_value'] = fix_values
    df['equity'] = 0.0


    for i in range(len(df)):

        diff = df['diff'][i]
        if (diff <= -sub_zone) & (diff >= -min_zone):

            df['asset_value'][i] = fix_values * (1 + 0.2)

            df['unit'][i] = float(df['asset_value'][i] / df['price'][i])
            df['adj_cash'][i] = df['value'][i] - df['asset_value'][i]  # if >min <max adj else  none adjust
            df['free_cash'][i] = df['adj_cash'][i] + df['start_cash'][i]
            df['equity'][i] = df['asset_value'][i] + df['free_cash'][i]

        elif (diff >= sub_zone) & (diff <= max_zone):

            df['asset_value'][i] = fix_values * (1 - 0.2)

            df['unit'][i] = float(df['asset_value'][i] / df['price'][i])
            df['adj_cash'][i] = df['value'][i] - df['asset_value'][i]  # if >min <max adj else  none adjust
            df['free_cash'][i] = df['adj_cash'][i] + df['start_cash'][i]
            df['equity'][i] = df['asset_value'][i] + df['free_cash'][i]

        elif (diff >= -(sub_zone)) & (diff <= sub_zone):

            df['asset_value'][i] = fix_values

            df['unit'][i] = float(df['asset_value'][i] / df['price'][i])
            df['adj_cash'][i] = df['value'][i] - df['asset_value'][i]  # if >min <max adj else  none adjust
            df['free_cash'][i] = df['adj_cash'][i] + df['start_cash'][i]
            df['equity'][i] = df['asset_value'][i] + df['free_cash'][i]

    #     ## Action 2  No adj if below min% ,above max%
    for i in range(len(df)):
        diff = df['diff'][i]

        if (diff < (-min_zone)):

            df['unit'][i] = df[df['diff'] >= -(min_zone)]['unit'].values[-1]
            df['asset_value'][i] = df['unit'][i] * df['price'][i]
            df['adj_cash'][i] = 0  # if >min <max adj else  none adjust
            df['free_cash'][i] = df[df['diff'] >= -(min_zone)]['free_cash'].values[-1]
            df['equity'][i] = df['asset_value'][i] + df['free_cash'][i]


        elif (diff > (max_zone)):

            df['adj_cash'][i] = 0  # if >min <max adj else  none adjust
            df['unit'][i] = df[df['diff'] <= (max_zone)]['unit'].values[0]
            df['free_cash'][i] = df[df['diff'] <= (max_zone)]['free_cash'].values[0]
            df['asset_value'][i] = (df['unit'][i] * df['price'][i])
            df['equity'][i] = df['asset_value'][i] + df['free_cash'][i]
        #     bh= fix_values+start_cash

    #     df['equity_bh'] =  bh+ (bh*df['diff'])

    df.drop(columns=['start_cash'], inplace=True)
    return df





def create_entry_setting(SETTING):
    dict_setting = {}
    dict_entry = {}
    exc = Exchange()
    timestamp = datetime.now().strftime('%Y/%m/%d %H:%M:%S')

    for i in SETTING[0]:
        name = i['symbol'].split('/')[0]
        name = name.lower()
        ### entry dict
        last = exc.get_price(i['symbol'])
        #             last = 3450.0 # Edit Manual
        unit_hold_first = round(float(i['fix'] / last), 5)
        value_first = round(unit_hold_first * last, 2)
        entry_d = {'date': timestamp, 'price': last, 'unit': unit_hold_first, 'value': value_first}
        ### Create data to save files
        dict_setting[i['symbol']] = i
        dict_entry[i['symbol']] = entry_d
        zone_bot = create_bot_zone(last, 0.1, last - (last * i['sl']) - 0.1, (last * i['tp']) + last + 0.1)
        # Adj 50 / 50 plans
        df = rebal_plans(zone_bot, fix_values=i['fix'], start_cash=i['fix'], max_zone=i['tp'], min_zone=i['sl'],
                         sub_zone=0.3)
        print(f'{name} CSV \n',df)
        print('#-#'*50)
        # print(dict_entry)
        # print(dict_setting)
        if os.path.exists(f'price_file/{name}.csv') != True:
            print(f'Create {name} Price  File')
            df.to_csv(f'price_file/{name}.csv')

    if os.path.exists(PERSISTANT_PRICE_FILE) != True:
        _save_json(PERSISTANT_PRICE_FILE, dict_entry)
        print('Create EntryPrice File')
    #
    if os.path.exists(SETTING_FILE) != True:
        print('Create SettingFile')
        _save_json(SETTING_FILE, dict_setting)

    if os.path.exists(STATUS_FILE) != True:
        print('Create Status File')
        save_txt(STATUS_FILE, 'on')


    else:
        print('File Already Exists')

    return dict_setting,dict_entry


#  # Step 1
import warnings
warnings.filterwarnings('ignore')
setting  , entry= create_entry_setting(list_setting)
print('ENTRY : ',entry)
print('#'*50)
print('SETTING :',setting)
