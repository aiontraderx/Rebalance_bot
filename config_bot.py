# ASSETS_TO_TRADE = ("ETH/USD", "SOL/USD",'XRP/USD')
import os

from dotenv import load_dotenv

load_dotenv()
secret_key = os.getenv("secret_key")
apikey = os.getenv("apikey")
sub_account_name = 'test_bot'
list_setting = []

ASSETS_TO_TRADE = ['ETH/USD', 'SOL/USD']
# new ways
symbol_1 = {'symbol': 'ETH/USD', 'fix': 500, 'buy_p': 0.03, 'sell_p': 0.02, 'tp': 0.5, 'sl': 0.5}
symbol_2 = {'symbol': 'SOL/USD', 'fix': 300, 'buy_p': 0.03, 'sell_p': 0.02, 'tp': 0.9, 'sl': 0.5}
# list_setting[0][0]['symbol']
list_setting.append([symbol_1, symbol_2])
print(list_setting)

LOGFILE = 'log_save/log.txt'
EX_LOGFILE = 'log_save/exchange_log.txt'
BOT_LOGFILE = 'log_save/bot_log.txt'
SETTING_FILE = 'setting/SETTING.json'
PERSISTANT_PRICE_FILE = 'setting/initial_price.json'
STATUS_FILE = 'status.txt'
PORT_LOG = r'log_save/Portfolio.csv'  # read

## os
