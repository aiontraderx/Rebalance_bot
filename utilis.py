import pandas as pd
from config_bot import LOGFILE,SETTING_FILE,EX_LOGFILE,BOT_LOGFILE
import json






def log(msg):
    from datetime import datetime as dt
    timestamp = dt.now().strftime('%Y/%m/%d %H:%M:%S')
    s = "[%s] %s" % (timestamp, msg)
    print(s)
    print('#' * 50)
    try:
        f = open(LOGFILE, "a")
        f.write(s + "\n")
        f.close()
    except:
        pass


def log_bot(msg):
    from datetime import datetime as dt
    timestamp = dt.now().strftime('%Y/%m/%d %H:%M:%S')
    s = "[%s] %s" % (timestamp, msg)
    print(s)
    print('#' * 50)
    try:
        f = open(BOT_LOGFILE, "a")
        f.write(s + "\n")
        f.close()
    except:
        pass

def log_ex(msg):
    from datetime import datetime as dt
    timestamp = dt.now().strftime('%Y/%m/%d %H:%M:%S')
    s = "[%s] %s" % (timestamp, msg)
    print(s)
    print('#' * 50)
    try:
        f = open(EX_LOGFILE, "a")
        f.write(s + "\n")
        f.close()
    except:
        pass




def load_json(filen):
    try:
        with open(filen, "r", encoding="utf8") as a_file:
            load_file = json.load(a_file)
            a_file.close()
        return load_file
    except :
        with open(filen, "r", encoding="utf-8-sig") as a_file:
            load_file = json.load(a_file)
            a_file.close()
        return load_file

def _save_json(filen,out):
    with open(filen, "w", encoding="utf8") as a_file:
            file= json.dump(out, a_file)
            a_file.close()
    return file

def save_txt(file, out):
    with open(file, "w", encoding="utf8") as prices_file:
        prices_file.write(out)
        prices_file.close()
    msg = f'Save json file {file}'
    log(msg)
    return file


def read_config(filename):
    with open(filename, encoding='utf-8') as status:
        status_line = status.read()
        return status_line




def _load_json(filen):
    file = pd.read_json(filen)
    msg = f'Load json file {filen}'
    print(msg)
    return file

def update_entry_to_setting(setting,update_price_entry):
    setting_load = _load_json(SETTING_FILE).T
    setting_load['entry_price'] = 0
    previou_setting = setting_load.index.values
    setting_now = setting.index.values

    for symbol in setting_now:
        if symbol not in previou_setting:
            update_row = update_price_entry[update_price_entry['symbols'] == symbol]
            setting_load = setting_load.append(update_row)
        entry_price = (update_price_entry[update_price_entry['symbols'] == symbol]['price'].values[0])
        print(entry_price)
        setting_load.loc[setting_load.index == symbol, 'entry_price'] = entry_price

    print('Update Entry On setting file')
    return setting_load



