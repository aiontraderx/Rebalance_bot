import asyncio

from config_bot import secret_key,apikey,sub_account_name
import ccxt
from datetime import datetime
from decimal import Decimal
import pandas as pd
from utilis import log,log_bot,log_ex

ex = ccxt.ftx({'api_key':apikey,'secret':secret_key ,'enableRateLimit': True,'headers': {
                    'FTX-SUBACCOUNT': sub_account_name,
                }})
class Exchange:
    def __init__(self):
        self.exchange = self.ccxt.ftx({'api_key':apikey,'secret':secret_key ,'enableRateLimit': True,'headers': {
                    'FTX-SUBACCOUNT': sub_account_name,}})
        # self.exchange =ex
    def get_wallet(self):
        try:
            wallet = self.exchange.privateGetWalletBalances()['result']
            return wallet
        except:
            return None

    def _get_time(self):
        """Get current date and time in human readable format
        :rtype: str
        :returns: Current date and time information
        """

        now = datetime.now()
        formatted_date = now.strftime("%d/%m/%Y %H:%M:%S")

        return formatted_date

    def get_cash(self):
        try:
            wallet = self.get_wallet()
            for t in wallet:
                if t['coin'] == 'USD':
                    #                     wallet[0]['coin'] in ['USD','USDT'] !!!
                    #                 if ('USD' not in token_name[i]) and ('USDT' not in token_name[i]):

                    cash = float(t['availableWithoutBorrow'])
            return cash
        except:
            return None

    def get_token_value(self, symbols):
        try:
            wallet = self.get_wallet()
            usd_value = 0
            for token in wallet:
                if token['coin'] == symbols:
                    usd_value = (token['usdValue'])

            return float(usd_value)
        except Exception as e:
            print(str(e))
            print('No Asset In Wallet')
            usd_value = 0
            return float(usd_value)

    def get_unit(self, symbols):
        try:
            wallet = self.get_wallet()
            token_name = symbols.split('/')[0]
            unit = 0
            for token in wallet:
                if token['coin'] == token_name:
                    valuex = float(token['availableWithoutBorrow'])
                    unit += (valuex)

            return float(unit)
        except Exception as e:
            print(str(e))
            print('No Asset In Wallet')
            unit = 0
            return float(unit)

    def get_price(self, symbols):
        try:
            price = self.exchange.fetch_ticker(symbols)['last']
            return float(price)
        except Exception as e :
                print(f'Error {symbols}')
                print( str(e ))
                log_ex(str(e))

    def get_bid(self, symbol):
        try:
            return float(self.exchange.fetch_ticker(symbol)['info']['bid'])
        except :
            print('Bid Erorr')
            return None

    def get_ask(self, symbol):
        try:
            return float(self.exchange.fetch_ticker(symbol)['info']['ask'])
        except :
            print('Ask Erorr')
            return None


    def get_mid_price(self, symbol, spread=0.00):
        ### Spread range 0.001- 0.005 or off
        mid_price = (self.get_bid(symbol) + self.get_ask(symbol)) / 2
        mid_buy = mid_price - (mid_price * spread)
        mid_sell = mid_price + (mid_price * spread)

        step_price = self.step_price(symbol)
        mid_price = self.round_by_step(mid_price, step_price)
        mid_buy = self.round_by_step(mid_buy, step_price)
        mid_sell = self.round_by_step(mid_sell, step_price)

        return (mid_price, mid_buy, mid_sell)

    def _adj_unit(self,diff, mid_price, min_size):
        adj_unit = diff / mid_price  # 60$ / price 2$ >> unit =30
        adj_unit = float(abs((self.round_by_step(adj_unit, min_size))))  ## absolute
        return adj_unit

    def _check_token_name(self,symbol):
        if len(symbol.split('/')) == 2:
            token_name = symbol.split('/')[0]
        if len(symbol.split('-')) == 2:
            token_name = symbol.split('/')[0]
        token_name = token_name.lower()
        return token_name

    def cancel_id(self, order_id):
        try:
            self.exchange.cancel_order(order_id)
            status = True
            print("Order ID : {} Successfully Canceled".format(order_id))
        except Exception as e:
            status = False
            print(str(e))
        return status

    def _minimum_size(self, symbol):
        try:
            return float(self.exchange.fetch_ticker(symbol)['info']['minProvideSize'])
        except Exception as e :
            print(str(e)+': Miniumsize Error')
            log_ex(str(e))

    def step_price(self, symbol):
        try:
            return self.exchange.fetch_ticker(symbol)['info']['priceIncrement']
        except Exception as e:
            print(str(e) + ': Step Price Error')
            log_ex(str(e))

    def _hold_values(self, symbol):  ## [date,usd,unit,now_price]
        dt_now = self._get_time()
        asset_dict = {}
        asset_dicts = []
        sum_value = 0

        if symbol != 'all':
            # token_name = symbol.split('/')[0]
            unit_hold = self.get_unit(symbol)
            last = self.get_price(symbol)
            name = self._get_token_name(symbol)
            usd_value = (unit_hold * last)
            #         usd_value = self.round_by_step(usd_value,0.01)
            asset_dict[symbol] = {'date': dt_now, f'unit': unit_hold,
                                  f'usd_values': usd_value, 'symbol': symbol, 'name': name}
            cash = self.get_cash()
            asset_dict['USD'] = {'date': dt_now, f'unit': cash,
                                 f'usd_values': cash, 'symbol': 'USD', 'name': 'usd'}
            sum_value += usd_value
            total_all_value = sum_value + cash
            msg = f'Check Value {name} + Cash {cash} = {total_all_value}'
            # log(msg)
            print(msg)

        elif symbol == 'all':
            res = self.exchange.privateGetWalletBalances()['result']
            for i in res:  ###
                valuex = float(i['usdValue'])
                if valuex > 0:
                    # print(i)
                    symbol  = i['coin'] + '/USD'
                    name = self._get_token_name(symbol)
                    if i['coin'] != 'USD':
                        last = self.get_price(symbol)
                        unit_hold = self.get_unit(symbol)

                        usd_value = (unit_hold * last)
                        asset_dict[symbol] = {'date': dt_now, 'unit': unit_hold,
                                         f'usd_values': usd_value, 'symbol': symbol, 'name': name}
                        sum_value += usd_value
                        # print(symbol,usd_value,last,unit_hold)

                cash = self.get_cash()
                asset_dict['USD'] = {'date': dt_now, f'unit': cash,
                                         f'usd_values': cash, 'symbol': 'USD', 'name': 'usd'}


            total_all_value = sum_value + cash
            # msg = f'Check All Asset Value   + Cash = {sum_value} + {cash} = {total_all_value}'
            # log(msg)
            # print(msg)

        return (asset_dict,total_all_value)

    def _get_token_name(self, symbol):

        if len(symbol.split('/')) == 2:
            token_name = symbol.split('/')[0]
            token_namex = token_name.lower()

        if len(symbol.split('-')) == 2:
            token_name = symbol.split('/')[0]
            token_namex = token_name.lower()

        else :
            token_name = symbol
            token_namex = token_name.lower()
        return token_namex

    def round_by_step(self, a_number: Decimal, step_size: Decimal):

        a_number = float(a_number)
        step_size = float(step_size)
        """
        Rounds the number down by the step size, e.g. round_by_step(1.8, 0.25) = 1.75
        :param a_number: A number to round
        :param step_size: The step size.
        :returns rounded number.
        """
        return float((Decimal(a_number) // Decimal(step_size)) * Decimal(step_size))

    def create_custom_order(self, symbols, side, unit, price,typex='limit'):  ### Custom param
        try:
            if typex =='limit':
                orderInfo = self.exchange.create_order(symbols, typex, side, unit, price)["info"]
                orderID = orderInfo["id"]
                usdValue = round(price * unit, 3)
                msg = f'Open-{orderID} {side} ,{symbols} Price: {price:.5f} Unit :{unit} Usd {usdValue}$'
                # print(msg)
                log_ex(msg)
            elif typex =='market':
                orderInfo = self.exchange.create_order(symbols, typex, side, unit)["info"]
                orderID = orderInfo["id"]
                usdValue = round(price * unit, 3)
                msg = f'Open-{orderID} {side} ,{symbols} Price: {price:.5f} Unit :{unit} Usd {usdValue}$'
                # print(msg)
                log_ex(msg)
        # self.sendtext(msg)

        except ccxt.InvalidOrder as e:
            #             dollar_round = float(round(1 / price, 2))
            orderInfo = {'id': 0}
            msg = "InvalidOrder " + str(e)
            log_ex(msg)
            return orderInfo

        except ccxt.NetworkError as e:
            orderInfo = {'id': 0}
            log_ex("NetworkError , " + str(e))


        except ccxt.ExchangeError as e:
            orderInfo = {'id': 0}
            log_ex(str(e))

        except ccxt.InsufficientFunds as e:
            orderInfo = {'id': 0}
            log_ex(":Not Enough Balances / Asset To Trades ")
        return orderInfo



    def check_order(self, symbols):
        try:
            list_id = []
            orders = self.exchange.fetch_open_orders(symbols)
            for i in orders:
                idx = i['id']
                status = i['status']
                list_id.append(idx)
        except Exception as e:
            log_ex(str(e))
        return list_id



    def cancel_order(self,order_id):
        try :
            self.exchange.cancel_order(order_id)
            print("Order ID : {} Successfully Canceled".format(order_id))
        except Exception as e:
            print(str(e))



    def cancelby_symbol(self, symbol):
        try:
            order_list = self.check_order(symbol)
            if order_list != []:  # IF have Open trade on symbols cancel all
                for order in order_list:
                    self.cancel_id(order)
            else:
              print(f'{symbol} -- Order  Not Found')
        except  Exception as e:
            print(str(e))

    def equity_report(self):
        hold_all = self._hold_values('all')
        port_dict = hold_all[0]
        total_equity = hold_all[1]
        equity = pd.DataFrame()
        equity['date'] = pd.Series(self._get_time())
        # token_name =[]

        for i in port_dict:
            if ('/USD' not in port_dict[i]['name']):
                name = port_dict[i]['name'].split('/')[0] ## Test and append

                # name = port_dict[i]['name'] # old ways
                valuex = port_dict[i]['usd_values']
                valuex = float(valuex)
                if valuex >= 10:
                    unitx = port_dict[i]['unit']
                    exposure = valuex / total_equity
                    equity[f'{name}_value'] = valuex
                    equity[f'{name}_unit'] = unitx
                    equity[f'{name}_exposure'] = exposure

        #         token_name.append(name)
        equity['usd'] = port_dict['USD']['usd_values']
        equity['equity'] = total_equity

        return equity



