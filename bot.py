import asyncio

from utilis import read_config,load_json,_save_json,save_txt
from config_bot import PERSISTANT_PRICE_FILE,SETTING_FILE,STATUS_FILE
from threading import Thread,Lock
from exchange import *
# import os
import threading
import sys
from datetime import datetime,timedelta


class BOT(Thread):
    def __init__(self, ASSETS_TO_TRADE):

        Thread.__init__(self, daemon=True)  #
        self.pause_cond = threading.Condition(Lock())

        self.exc = Exchange()
        self.run_bot = True  # pause resume
        self.OPEN_BOT = True  # start close # control while loop
        self.recheck_sl = True
        #         self.last_order = {}
        #         self.previou_trade_info = {}
        self.market_type = 'limit'  #
        self.ordey_type = 'long'  # long ,'short'
        self.setting = load_json(SETTING_FILE)
        self.initial_price = load_json(PERSISTANT_PRICE_FILE)
        self.cd = 300
        self.live_trade = True
        self.ASSETS_TO_TRADE = ASSETS_TO_TRADE

    #         print(self.initial_price)

    def _max_min_zone(self, symbol):
        tp_p = self.setting[symbol]['tp']
        sl_p = self.setting[symbol]['sl']

        entry_p = self.initial_price[symbol]['price']
        sl_zone = entry_p - (entry_p * sl_p)
        tp_zone = entry_p + (entry_p * tp_p)
        #                 print(tp_zone,sl_zone)

        return (tp_zone, sl_zone, entry_p)

    def _check_reb(self, symbol):

        # try:
            self.exc.cancelby_symbol(symbol)  # Cancle all order on symbol
            min_size = self.exc._minimum_size(symbol)
            # step_price = self.exc.step_price(symbol)
            unit = self.exc.get_unit(symbol)  #
            last = self.exc.get_price(symbol)
            token_name = self.exc._check_token_name(symbol)
            hold_values = unit * last
            #fix_value = float(self.setting[symbol]['fix'])
            data_plan = pd.read_csv(f'price_file/{token_name}.csv')

            try:
                fix_value = data_plan[data_plan['price'] <= last]['asset_value'].values[0]

            except IndexError as e:
                fix_value = data_plan[data_plan['price'] >= last]['asset_value'].values[-1] ##


            buy_p = float(self.setting[symbol]['buy_p'])
            sell_p = float(self.setting[symbol]['sell_p'])
            if fix_value > 0:  ## if fix Value greater than 0
                hold_values = round(hold_values, 2)
                diff = hold_values - fix_value  #######  300 - 500 = diff $
                # print(fix_value,diff)
                diff_p = diff / fix_value  # diff $ %
                diff = round(self.exc.round_by_step(diff, 0.01), 3)  ## round usd dollar $
                diff_p = round(self.exc.round_by_step(diff_p, 0.001), 4)  # round diff %
                if symbol in ['ETH/USD','BTC/USD']:
                    spread_fix = 0.0025
                else :
                    spread_fix = 0.005


                mid_price_all = self.exc.get_mid_price(symbol, spread=spread_fix)

                mid_price = mid_price_all[0]

                mid_price_buy = mid_price_all[1]
                mid_price_sell = mid_price_all[2]
                adj_unit = diff / mid_price  # 60$ / price 2$ >> unit =30

                #         print(mid_price_all,min_size)
                #         print(adj_unit,min_size,mid_price)
                adj_unit = float(abs((self.exc.round_by_step(adj_unit, min_size))))  ## absolute
                # print(type(diff),diff,mid_price_all,adj_unit)

                if (diff_p <= -buy_p) & (adj_unit >= min_size):

                    adj_unit = diff / mid_price_buy  # change values
                    adj_unit = float(abs((self.exc.round_by_step(adj_unit, min_size))))  ## absolute
                    action_price = mid_price_buy
                    actionx = 'buy'
                    # msg = f'{token_name} : Fix {fix_value} $: Nows Values {hold_values}$ | Hold Unit {unit} {actionx} {adj_unit} @ {action_price:5f} '
                    # print(msg)
                    print('Buy ',symbol,' SPEARD ',spread_fix,f' {action_price:.5f}')
                    msg1 = f'{symbol} Rebalance :{actionx}'
                    log_bot(msg1)
                    action = {'action': actionx, 'unit': adj_unit, 'price': action_price, 'diff': diff, 'symbol': symbol}



                elif (diff_p >= sell_p) & (adj_unit >= min_size):

                    adj_unit = diff / mid_price_sell  # change values
                    adj_unit = abs(self.exc.round_by_step(adj_unit, min_size))  ## absolute
                    action_price = mid_price_sell
                    actionx = 'sell'

                    print('Sell ',symbol,' SPEARD ',spread_fix,f' {action_price:.5f}')

                    msg1 = f'{symbol} Rebalance :{actionx}'
                    log_bot(msg1)
                    action ={'action':actionx, 'unit':adj_unit, 'price':action_price, 'diff':diff, 'symbol':symbol}


                elif (diff_p > -buy_p) & (diff_p < sell_p) or (adj_unit < min_size):  # waiting process
                    print('Wait ',symbol,' SPEARD ',spread_fix)
                    action_price = mid_price
                    actionx = 'wait'
                    adj_unit = 0
                    action_price = 0
                    # msg = f'{token_name}  Fix {fix_value:.2f}  : Values {hold_values:.2f}:Hold Unit {unit:.5f} ,Diff {diff_p * 100:.2f}%\nTrigger:Buy {buy_p * 100}% : Sell {sell_p * 100}%'
                    # print(msg)
                    msg1 = f'{symbol} Rebalance :{actionx},Refresh time {self.cd} Seconds '
                    log_bot(msg1)
                    action = {'action': actionx, 'unit': adj_unit, 'price': action_price, 'diff': diff, 'symbol': symbol}


            else:
                actionx = 'Error'
                adj_unit = 0
                action_price = 0
                diff = 0
                print(actionx, f': {symbol} Not in Asset TRADES')
                # return {'action':'None', 'unit':0, 'price':0, 'diff':0, 'symbol':symbol}
                action ={'action':actionx, 'unit':adj_unit, 'price':action_price, 'diff':diff, 'symbol':symbol}

        # except ZeroDivisionError as e:
        #     print(str(e) + ': Please Recheck Setting Fix Values')
        #     return None
        #
        # except KeyError as e:
        #     print(str(e) + ': Symbols Not in Asset TRADES')
        #     return None
        #
        # except Exception as e:
        #     print(str(e))
        #     log_bot(e)
        #     sys.exit()
        # return action  ## action unit action_price
            return action

    async def _create_trades(self, action):
        #     cd_bot =60
        # cd_bot -20 secondes
        await asyncio.sleep(0.5)
        sidex = action['action']
        pricex = action['price']
        order = self.exc.create_custom_order(symbols=action['symbol'], side=sidex, unit=action['unit']
                                         , price=pricex, typex='limit')
        # first buy price by action['price']

        order_id = order['id']
        loop_count = 0
        check_loop = 6

        symbols = action['symbol']

        if (order_id != 0):
            while True:
                await asyncio.sleep(30)  # minus 10 seconds
                status = self.exc.exchange.fetch_order_status(order_id)
                print(f'Order Status {status}  : {order_id}')
                if status in ['closed', 'cancled', 'pending_cancel', 'expired']:
                    print(f'[{self.exc._get_time()}] {symbols} :Trades Complete [cancle/fill] ::')
                    cond = True

                    break
                    return cond

                    ### Order was fill


                elif status in ['open']:
                    ### Rebuy

                    action = self._check_reb(symbols)
                    sidex = action['action']
                    pricex = action['price']
                    if sidex == 'buy':
                        if loop_count >= check_loop/2 :
                            n_price = self.exc.get_mid_price(symbols, spread=0.0015)[1]
                        else :
                            n_price = self.exc.get_mid_price(symbols, spread=0.0025)[1]


                        if n_price >= pricex:
                            self.exc.cancelby_symbol(symbols)  # Cancle all order on symbol
                            order = self.exc.create_custom_order(symbols=action['symbol'], side=action['action'],
                                                             unit=action['unit'], price=n_price, typex='limit')

                            n_order_id = order['id']
                            if (n_order_id != 0):
                                # n_price = action['price']
                                price = action['price']
                                n_status = self.exc.exchange.fetch_order_status(n_order_id)
                                diff = (n_price / price - 1) * 100
                                print(
                                    f'[{self.exc._get_time()}]:{symbols} Retry Trades  OLD_Entry:{price} : Now_Entry {n_price}  Chg {diff:.2f}%')
                                print(f'New order {n_order_id}: {n_status} Replace -  {order_id} ')
                                print('#' * 50)
                                order_id = n_order_id
                                status = n_status

                            else:
                                print('No Order ID')
                                print('#' * 50)
                        else:
                            print('No Refresh order')
                            cond = False

                    elif sidex =='sell':  # Sell action

                        if loop_count >= check_loop/2 :
                            n_price = self.exc.get_mid_price(symbols, spread=0.002)[2]
                        else :
                            n_price = self.exc.get_mid_price(symbols, spread=0.0025)[2]

                        if n_price <= pricex:
                            self.exc.cancelby_symbol(symbols)  # Cancle all order on symbol
                            order = self.exc.create_custom_order(symbols=action['symbol'], side=action['action'],
                                                             unit=action['unit'], price=n_price, typex='limit')

                            n_order_id = order['id']
                            if (n_order_id != 0):
                                # n_price = action['price']
                                price = action['price']
                                n_status = self.exc.exchange.fetch_order_status(n_order_id)
                                diff = (n_price / price - 1) * 100
                                print(
                                    f'[{self.exc._get_time()}]:{symbols} Retry Trades  OLD_Entry:{price} : Now_Entry {n_price}  Chg {diff:.2f}%')
                                print(f'New order {n_order_id}: {n_status} Replace -  {order_id} ')
                                print('#' * 50)
                                order_id = n_order_id
                                status = n_status
                            else:
                                print('No Order ID')
                                print('#' * 50)
                        else:
                            print('No Refresh order')
                            cond = False
                    else :
                        print(f'{symbols} No Rebalance Value = Fix Values')
                # cd_bot / 10 - 2  # 10sec firstloop 10sec last loop each loop 10 sec (10#,10,10,10,10,#10)
                #             check_loop = ((cd_bot/ wait_by_loop )) ## 30 sec and wait 10 sec
                # (300/30) = 10 loops and wait be
                loop_count += 1
                print(f'Count Loop {symbols} :', loop_count, check_loop)
                if loop_count >= check_loop:  # 5sec upto 50seconds up to main cd bot
                    ## limit loop and not fill wait 20 sec
                    print(f'[{self.exc._get_time()}] Finished {check_loop} Loops  Done ')
                    print('#' * 50)
                    cond = False
                    # await asyncio.sleep(20)
                    break
        return cond

    async def _taksleep(self, timesleep):

        print(f'[{self.exc._get_time()}] :Time Sleep  Bot ')
        await asyncio.sleep(timesleep)
        print(f'[{self.exc._get_time()}] :Closed  Time Sleep Bot ')

########################################################################################################
    def _close(self, exit_only=False):
        # cancle all order
        #         for symbol in ASSETS_TO_TRADE:
        #             cancle = self.exc.cancel_id(self.last_order[symbol])  # Return status True False
        cancle = self.exc.exchange.cancel_all_orders()
        self.run_bot = False
        self.OPEN_BOT = False
        msg = 'Exit_Programes : User Close BOT'
        log_bot(msg)
        if exit_only == False:
            save_txt(STATUS_FILE, 'kill')
            sys.exit()
        else:
            sys.exit()

    def _pause(self):
#       cancle order
        self.exc.exchange.cancel_all_orders()
        self.run_bot = False
        msg = ' User Pause Bot'
        log_bot(msg)
        save_txt(STATUS_FILE, 'off')
        self.pause_cond.acquire()

    def _resume(self):
        self.run_bot = True
        self.OPEN_BOT = True
        msg = 'User Resume Bot '
        log_bot(msg)
        save_txt(STATUS_FILE, 'on')
        self.pause_cond.notify()

        self.pause_cond.release()

    def _check_status(self):
        status = read_config(STATUS_FILE)  ## config all files
        #         status = StatusBot.ON

        if status == 'on':
            self.run_bot = True
            self.OPEN_BOT = True
        elif status == 'kill':
            #             self.OPEN_BOT = False
            self._close()
        elif status == 'off':
            self.run_bot = False
        return status


    def _run_bot(self):
        import time
        all_task = []

        for symbol in self.ASSETS_TO_TRADE:
            max_min = self._max_min_zone(symbol)
            max_zone = max_min[0]
            min_zone = max_min[1]
            last = self.exc.get_price(symbol)
            time.sleep(0.5)
            action = self._check_reb(symbol) # first canalce
            print(action)

            if (  action['action'] != 'wait') & ( action['action'] != 'Error') :
                if (last < max_zone) & (last > min_zone):
                    if self.live_trade:
                        # print(action)
                        # a=  self.exc._create_trades(action)
                        job=  self._create_trades(action)

                        all_task.append(job)
                    else:
                        print(action)

                else:
                    msg = 'STOP BOT BY TP/SL Waiting to Maunal Close'
                    log_bot(msg)
            # elif action[0] == 'None':

            elif action['action'] =='wait':
                self.exc.cancelby_symbol(symbol)  # Cancle all order on symbol
                msg = ' Wait To action '
                print(msg)
                print('#' * 50)
                a= self._taksleep(60)
                all_task.append(a)
            #                 log(msg)

            elif action['action'] =='Error':
            # elif action[0] == 'Error':
                self.exc.cancelby_symbol(symbol)  # Cancle all order on symbol
                msg = ' Symbols not allow to trades check Fix value and ASSET to Trade'
                print(msg)
                print('#' * 50)
                a = self._taksleep(60)
                all_task.append(a)
        # await asyncio.gather(*all_task) ## task = 60 sec
        return all_task

    def run(self):
        from PortDB import PortDatabase

        msg = 'USER Start Bot'
        log_bot(msg)

        while self.OPEN_BOT:  # self.OPEN_BOT
            with self.pause_cond:
                status = self._check_status() # db
                print(f'Control Status {status}')
                self.setting = load_json(SETTING_FILE) # db
                self.initial_price = load_json(PERSISTANT_PRICE_FILE)# db

                if self.run_bot:  ### Check Rebalance
                    print('ASSET TRADES: ', self.ASSETS_TO_TRADE)
                    # task = self._run_bot()  # loop check rebalance and trade all symbols list
                    task = self._run_bot()
                    # print(task)
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    all_groups  = asyncio.gather(*task)
                    # loop.create_task()
                    results = loop.run_until_complete(all_groups)
                    print('Loop Closed ')
                    loop.close()
                    DB = PortDatabase()
                    DB.save_CSV()
                    # next rebalance time
                    a = self.exc._get_time()
                    date_time_obj = datetime.strptime(a, '%d/%m/%Y %H:%M:%S')
                    b = date_time_obj + timedelta(0, 3)
                    b.strftime('%d/%m/%Y %H:%M:%S')
                    print('CD TIMES :', self.cd, a)
                    print('Next Time Run  : ',b)
                    print('#' * 50)
                    self.pause_cond.wait(timeout=self.cd)
                    #time.sleep(self.cd)
                    # self.pause_cond.wait(timeout=self.cd)


                else:  # self.run_bot ==False
                    for symbol in self.ASSETS_TO_TRADE:
                        dt_str = self.exc._get_time()
                        price = self.exc.get_price(symbol)

                        if self.recheck_sl:  ## recheck to sell all on stoploss by equity report !!!
                            print(f'[{dt_str}]---- Stop Bot by User ----: {symbol} : {price}')
                            zone = self._max_min_zone(symbol)
                            tp_zone = zone[0]
                            sl_zone = zone[1]
                            if price < sl_zone:
                                print('SELL All !!!!!!!!!!!!')
                                print('STOP LOSS')
                                print('KILL PROGRAMS')

                        else:
                            print(f'[{dt_str}]---- Stop Bot by User ----: {symbol} : {price}')
                    DB = PortDatabase()
                    save_db = DB.save_CSV()
                    print('CD TIMES :', self.cd, self.exc._get_time())
                    self.pause_cond.wait(timeout=self.cd)
#                         time.sleep(cd_time)




# symbols ='ETH/USD'
# B = BOT([symbols])
# asyncio.gather(B.run())
# B.run()
# action = (B._check_reb(symbols))
# print(action)
# print(type(action))
# task = B._run_bot()
# all_groups = asyncio.gather(*task)
