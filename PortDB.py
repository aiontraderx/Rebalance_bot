from exchange import Exchange
import pandas as  pd
from config_bot import PORT_LOG
from utilis import log

class PortDatabase:
    def __init__(self):
        self.port_log = PORT_LOG
        self.exc = Exchange()  # Client ccxt.ftx()

    ######## CSV CHANGE TO SQL ###########
    def checkCSV(self):
        try:
            port_log = pd.read_csv(self.port_log)
            print('DataBase Exist Loading DataBase....')
        except:
            port_log = pd.DataFrame(columns=['date'])
            port_log.to_csv(self.port_log, index=False)
            print("Database Created")
        return port_log

    def save_CSV(self):
        #     log_trade = f"portfolio_record.csv"

        port_hist = self.checkCSV()
        equity_re = self.exc.equity_report()
        hold_equity = equity_re['equity'].values[0]
        free_usd = equity_re['usd'].values[0]

        port_hist = port_hist.append(equity_re)
        port_hist = port_hist.set_index('date')
        port_hist.to_csv(self.port_log)
        msg= f'Record Portfolio Values =  {hold_equity:.2f} : Free Cash {free_usd:.2f} ON CSV'
        # print(equity_re)
        log(msg)


        return port_hist # DataFrame


def log_job(LOGFILE):
    from datetime import datetime as dt
    timestamp = dt.now().strftime('%Y/%m/%d %H:%M:%S')
    msg = '-----------Test Auto Save------------'
    s = "[%s] %s" % (timestamp, msg)
    print(s)
    print('#' * 50)
    try:
        f = open(LOGFILE, "a")
        f.write(s + "\n")
        f.close()
    except:
        pass

DB= PortDatabase()
DB.save_CSV()