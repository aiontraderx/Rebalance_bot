# Rebalance_bot
only ftx


1.Create apiKey ,Secretkey env file
2.Edit and Run Config_bot.py 
  Setting Subaccount name
  Add ASSET NAME TO TRADES
    : Create Setting Symbol : symbol_1={'symbol':'ETH/USD','fix':500,'buy_p': 0.02, 'sell_p': 0.02 ,'tp':0.5,'sl':0.5}
                            : symbol_2= {'symbol':'SOL/USD','fix':300,'buy_p': 0.02, 'sell_p': 0.02 ,'tp':0.5,'sl':0.5}
                            list_setting.append([symbol_1,symbol_2])
      
3.Run command_bot.py
