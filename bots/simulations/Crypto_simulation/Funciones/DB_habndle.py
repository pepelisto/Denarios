from django.conf import settings
import django
from Denarios.settings import DATABASES, INSTALLED_APPS
from datetime import timedelta
django.setup()
from app.models import *


def update_opportunities(op, type=None, stock_rsi=None, macd=None, rsi=None, var_1=None):
    if type is not None:
        op.type = type
    if stock_rsi is not None:
        op.stock_rsi = stock_rsi
    if macd is not None:
        op.macd = macd
    if rsi is not None:
        op.rsi = rsi
    if var_1 is not None:
        op.var_1 = var_1
    op.save()

def create_position(symbol_, type_, entry_price_, quantity_, open_date_, stoch_, rsi_, sl_price, sl_tp_ratio):
    sl_factor = (sl_price/entry_price_) - 1
    tp__ = entry_price_ + entry_price_ * sl_factor * (-1.05) * sl_tp_ratio
    sl__ = entry_price_ + entry_price_ * sl_factor * (1.05)
    factor_ajuste = (abs((1 - entry_price_ / sl_price)) + 0.001) * 1.5
    Open_position_sim.objects.create(
        symbol=symbol_,
        type=type_,
        entry_price=entry_price_,
        quantity=quantity_,
        open_date=open_date_,
        stoch=stoch_,
        rsi=rsi_,
        sl_price=sl__,
        tp_price=tp__,
        ratr=factor_ajuste,  #se usa como factor de ajuste inicial
        atr=0,
    )

def close_position(s, po, close_date_, sl_tp_ratio, sl_limit, sl_low_limit, factor_ajuste, sim_number, sim_info, close_method):
    if close_method == "TP":
        exit_price = po.tp_price
    else:
        exit_price = po.sl_price
    if po.type == "BUY":
        delta = exit_price/po.entry_price - 1
    else:
        delta = -((exit_price / po.entry_price) - 1)
    quantity_ = round(po.quantity * (1 + delta), 2)
    fee_entry = round(po.quantity * 0.00045, 5)
    fee_exit = round(quantity_ * 0.00045, 5)
    total_fee = round(fee_exit + fee_entry, 4)
    profit_ = round(po.quantity * delta - total_fee, 3)
    roe_ = round((profit_/po.quantity)*100, 1)
    Closed_position_sim.objects.create(
        symbol=s,
        type=po.type,
        entry_price=round(po.entry_price, 6),
        exit_price=round(exit_price, 6),
        roe=roe_,
        fee=total_fee,
        profit=profit_,
        quantity=quantity_,
        open_date=po.open_date,
        close_date=close_date_,
        stoch_open=round(abs(0.5 - po.stoch), 2),
        rsi_open=abs(50 - po.rsi),
        close_method=close_method,
        tp_price=po.tp_price,
        sl_price=po.sl_price,
        tp_sl_ratio=sl_tp_ratio,
        sl_limit=sl_limit,
        sl_low_limit=sl_low_limit,
        ratr=factor_ajuste,
        simulation=sim_number,
        sim_info=sim_info,
    )
    Open_position_sim.objects.get(symbol_id=s.pk).delete()
    op = Oportunities_sim.objects.get(symbol_id=s.pk)
    update_opportunities(op, type='NONE', stock_rsi=False, macd=False, rsi=False)

def update_position(po, alt_TP_SL=None, sl_price=None, tp_price=None):
    if tp_price is not None:
        po.tp_price = tp_price
    if alt_TP_SL is not None:
        po.atr = alt_TP_SL
    if sl_price is not None:
        po.sl_price = sl_price
    po.save()