## Command Bot
#
from config_bot import SETTING_FILE,ASSETS_TO_TRADE,list_setting
from create_json import create_entry_setting
from bot import BOT

from PortDB import PortDatabase
import time
import threading
import sys
from utilis import _load_json,_save_json,log
import os
import ccxt
import pandas as pd



def cd_save(PortDatabase, cd=300):
    PortDatabase.save_CSV()
    time.sleep(cd)
    # countdown(cd)


## get calculate mid_price _postiosize #

def show_setting():
    data = B.setting
    df = pd.DataFrame(data).T
    return df


def _cancel_all():
    cancle = B.exc.exchange.cancel_all_orders()
    print('Cancle order all symbols')

    return cancle


def show_active_orders():
    orders = B.exc.exchange.fetch_open_orders()
    if orders != []:
        df = pd.DataFrame(orders)
        df.drop(columns='info', inplace=True)
        return df
    else:
        return []


def show_port():
    data = B.exc._hold_values('all')[0]
    df = pd.DataFrame(data).T.drop(columns=['symbol'])
    return df


def sell_all_asset():
    try:
        orders = []
        port_all = show_port()
        for i in range(len(port_all)):
            name = (port_all['name'][i])
            if name != 'usd':  # check symbols not usd
                symbols = port_all.index[i]
                B.setting[symbols]['fix'] = 0

                unit = port_all['unit'][i]
                last = B.exc.get_price(symbols)
                cancle = B.exc.exchange.cancel_all_orders()
                order = B.exc.exchange.create_order(symbols, 'market', 'sell', unit)
                orders.append(order)
                print(symbols, unit, last)
            _save_json(SETTING_FILE, B.setting)

    #                 change_settingfix_values
    except ccxt.InvalidOrder as e:
        print(f'{name} No Asset To Trade: Size To Small ')
        _save_json(SETTING_FILE, B.setting)

    return orders


def edit_setting(setting_dict=None):
    try:
        # setting_dict = {'SOL/USD':{'fix':'20','buy','sell','tp','sl'}}
        if setting_dict == None:
            print(B.setting)
            symbol_edit = input("Enter symbol to edit \n")  # add validation?
            fix_edit = input("Input Amount to Fix Values \n")
            buy_p = input("Input Buy Target  to Allocation \n")
            sell_p = input("Input Sell Target  to Allocation \n")
            tp_p = input("Input Take Profit Target % to stop bot \n")
            sl_p = input("Input Stop loss Target % to stop bot \n")

            B.setting[symbol_edit]['fix'] = float(fix_edit)
            B.setting[symbol_edit]['buy'] = float(buy_p)
            B.setting[symbol_edit]['sell'] = float(sell_p)
            B.setting[symbol_edit]['tp'] = float(tp_p)
            B.setting[symbol_edit]['sl'] = float(sl_p)

            _save_json(SETTING_FILE, B.setting)
        else:
            _save_json(SETTING_FILE, setting_dict)
    except KeyError as e:
        print(symbol_edit, 'Not IN SETTING FILE')


# symbol_x ='ETH/USD'
# side_x ='buy'

def _create_trade(symbols, side, unit, price, typex='limit'):
    B.exc.create_custom_order(symbols=symbols, side=side, unit=unit, price=price, typex=typex)


def _create_manual_trade():
    symbol_add = input("Enter symbol to Trades \n")  # add validation?
    symbol_add = (symbol_add).upper()
    quotes  = input("Enter quotes  to Trades # [USD,USDT,PERP] \n")  # add validation?

    if quotes in ['USD','USDT','usd','usdt']:
        quotes= quotes.upper()
        symbols = symbol_add +'/'+quotes
        con1= True

    elif quotes in ['perp','PERP']:
        quotes=quotes.upper()
        symbols = symbol_add +'-'+quotes
        con1= True

    else :
        print('Error Input Quotes Only Support [USD,USDT,PERP]')
        con1 =False
    print('Asset Trade :',symbols)

    if con1==True  :
        side = input("Input Side to Trades [buy-sell] \n")
        if side in ['sell','buy']:
            print('Input Side :',side)
            con2= True
        else :
            print('Error Input Side')
            side= None
            con2=False

    if (con2 == True)& (con1== True):
            unit = float(input("Input to Unit Trades  \n"))
            min_size = B.exc._minimum_size(symbols)
            if unit >= min_size :
                print(f'Allow to traades {unit} minimum {min_size}')
                con3= True
            else:
                print('Erorr')
                con3 =False
                unit = None


    if (con3 ==True)  & (con2 == True)& (con1== True):
            typex = input("Input Type to Trades [limit-market] \n")
            if typex in ['limit','market']:
                print(f'Input Type :{typex}' )
                con4= True
            else :
                print('Error typex')
                con4 =False

    if (con4 ==True)  & (con3 == True)& (con2== True) & (con1== True):
            print('Now Price: ',B.exc.get_price(symbols))
            price = float(input("Input Price : \n"))
            if unit >= min_size :
                print(f'Allow to traades {unit} minimum {min_size}')
            else:
                print('Erorr')
                price = None
    print(symbols,side,unit,price,typex)
    confirm =input(' Y or N To confirm Save')

    if confirm in ['y','Y']:
        if typex == 'limit':
            print('Limit Trades')
            B.exc.create_custom_order(symbols=symbols, side=side, unit=unit, price=price)
            msg= f'User Maunal trades {symbols}-{typex} @{price} -{side} {unit}   '
            log(msg)
        elif typex == 'market':
            print('Market trades')
            B.exc.create_custom_order(symbols=symbols, side=side, unit=unit,price=price,typex=typex)
            msg= f'User Maunal Trades {symbols}-{typex} {side}@ {unit}   '
            log(msg)

    else:
            print('Not Confirm')


def get_resposnse(cond=None):
    #     try:

    if cond == 'on' or 'off':  ### if bot status on/ off  return control by cmd or  0 1 # not 2
        command = input("Enter Condition \n")  # add validation?
    else:
        print('Bot Status KILL')

    if command in ['res', 'resume']:
        # no save cond
        cond = 'on'
        try:
            B._resume()
        except:
            print('Nows Threads Active Pasue and Resume')

    elif command in ['!help']:

        help_list = ['res', 'kill', 'pause', 'save_db', 'show_port', 'show_setting', 'exit', 'rebalance','check_rebal',
                     'edit_set', 'check_status']
        print('Prefix ! : ',help_list)

    elif command in ['!kill']:
        # save cond
        cond = 'kill'
        B._close()

    elif command in ['!pause']:
        cond = 'off'  # save
        # no save cond  or save for manual
        B._pause()

    elif command in ['!save_db', '!savedb']:
        DB = PortDatabase()
        threading.Thread(target=cd_save, args=(DB, 3600), daemon=True).start()

    elif command in ['!show_port']:
        print(show_port())

    elif command in ['!show_setting']:
        res= B.setting
        df=pd.DataFrame(res).T
        print(df)

    elif command in ['!exit']:
        B._close()
        sys.exit()


    elif command in ['!rebalance']:
        B._run_bot()


    elif command in ['!check_rebal']:
        print(ASSETS_TO_TRADE)
        for symbol in B.ASSETS_TO_TRADE:
            print(f'CHECK REB {symbol}')
            B._check_reb(symbol)
######## Addition & Test ####
    elif command in ['!manual_trade']: #!!!!!!!!!!!
        _cancel_all()
        _create_manual_trade()
        # print('Cancle order all symbols')

    elif command in ['!cancle_all']:
        # cancle = B.exc.exchange.cancel_all_orders()
        _cancel_all()



    elif command in ['!cancle_symbol']:
        symbol = input('Symbols to Cancle')
        B.exc.cancelby_symbol(symbol)  # Cancle all order on symbol

    elif command in ['!edit_asset_trade']:
        print(B.ASSETS_TO_TRADE)


    elif command in ['!check_status']:
        statusx = B.OPEN_BOT
        status_run_bot = B.run_bot
        print(f'Open Bot {statusx}, Auto Rebalance{status_run_bot}')

    elif command in ['!edit_setting', 'edit_set']:

        print(B.setting)
        edit_setting(setting_dict=None)

    elif command in ['!active_order']:
        print(show_active_orders())

    else:
        print('Error Command')


# ASSETS_TO_TRADE = ['ETH/USD','SOL/USD']
# df = create_entry_setting(ASSETS_TO_TRADE)
print(f'Price Range BOT ')

setting  , entry= create_entry_setting(list_setting)
print('ENTRY : ',entry)
print('#'*50)
print('SETTING :',setting)

print('#'*50)
# print(df)
# DB = PortDatabase()
# threading.Thread(target=cd_save, args=(DB, 3600), daemon=True).start()
processe = []
B = BOT(ASSETS_TO_TRADE) # Bot 1
# status =B._check_status()
B.start()

if __name__ == '__main__':

    while True:

        try:
            COMMAND = threading.Thread(target=get_resposnse, args=('on',), daemon=True).run()
            # print('Threadding Active', len(threading.enumerate()), [i for i in threading.enumerate()])
            time.sleep(1)
        except KeyboardInterrupt:
            print('Interrupted')
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)


