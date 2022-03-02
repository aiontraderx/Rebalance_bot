# Rebalance_bot
pip install -r requirements.txt


     1.Create env files add apikey ,secret_key
     2.Edit and Run Config_bot.py  
      ADD Subaccount name 
      Add ASSET NAME TO TRADES 
                    Example : 
                          sub_account_name = 'test_bot'
                        : symbol_1={'symbol':'ETH/USD','fix':500,'buy_p': 0.02, 'sell_p': 0.02 ,'tp':0.5,'sl':0.5} 
                          symbol_2= {'symbol':'SOL/USD','fix':300,'buy_p': 0.02, 'sell_p': 0.02 ,'tp':0.5,'sl':0.5}
                          list_setting.append([symbol_1,symbol_2])
      
     3.Run command_bot.py

Command Bot
            
            !help
