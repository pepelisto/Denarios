from bots.notUsed.A_A.functions.Take_position import BinanceTrader

position_side = 'BOTH'  # Replace with your position side (e.g., 'LONG' or 'SHORT')





sl_order_id = '855052269'
side = 'SELL'

sl_new_price = '0.615'
# response_sl = BinanceTrader().modify_order('PHBUSDT', sl_order_id, sl_new_price, side)
response_sl = BinanceTrader().place_order_tp_sl('PHBUSDT', 'BUY', sl_new_price, 'STOP_MARKET', sl_order_id)
# print("Modified SL Order:", response_sl)

# order_status = BinanceTrader().get_order_status('PHBUSDT', sl_order_id)
# print("Order Status:", order_status)