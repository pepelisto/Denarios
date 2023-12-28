from django.db import models


class Symbol(models.Model):
    symbol = models.CharField(max_length=12, unique=True)
    find_in_api = models.BooleanField(default=False)
    def __str__(self):
        return self.symbol + ' - ' + str(self.find_in_api)

class Oportunities(models.Model):
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    types = (('SELL', 'SELL'),('BUY', 'BUY'),('NONE','NONE'),('OPEN','OPEN'))
    type = models.CharField(max_length=4, choices=types, default='NONE')
    stock_rsi = models.BooleanField(default=False)
    macd = models.BooleanField(default=False)
    rsi = models.BooleanField(default=False)
    timeframe = models.FloatField(null=True, default=None)
    class Meta:
        unique_together = ['symbol', 'timeframe']
    def __str__(self):
        return str(self.symbol) + ' - ' + self.type + ' - ' + str(self.stock_rsi) + ' - ' + str(self.macd) + ' - ' + str(self.rsi) + ' - ' + str(self.timeframe)


class Open_position(models.Model):
    symbol = models.OneToOneField(Symbol, on_delete=models.CASCADE)
    types = (('SELL', 'SELL'),('BUY', 'BUY'))
    type = models.CharField(max_length=4, choices=types, default='NONE')
    entry_price = models.FloatField()
    quantity = models.FloatField()
    leverage = models.PositiveIntegerField()
    margin = models.FloatField()
    id_position = models.PositiveIntegerField()
    open_date = models.DateTimeField()
    tp_price = models.FloatField(null=True, default=None)
    sl_price = models.FloatField(null=True, default=None)
    tp_s = models.BooleanField(default=False)
    sp_s = models.BooleanField(default=False)
    alt_TP_SL = models.IntegerField(null=True, default=0)
    stoch = models.FloatField(null=True, default=None)
    rsi = models.FloatField(null=True, default=None)
    stopPrice_precision = models.IntegerField(null=True, default=0)
    timeframe = models.IntegerField(null=True, default=0)
    sl_order_id = models.CharField(max_length=50, null=True, default=None)
    tp_order_id = models.CharField(max_length=50, null=True, default=None)
    def __str__(self):
        return str(self.symbol) + ' - ' + self.type + ' - ' + str(self.alt_TP_SL) + ' - ' + str(self.timeframe) \
            + ' -tp price ' + str(self.tp_price) + ' -sl price ' + str(self.sl_price) + ' -sl price ' + str(self.alt_TP_SL)


class Closed_position(models.Model):
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    types = (('SELL', 'SELL'), ('BUY', 'BUY'))
    type = models.CharField(max_length=4, choices=types)
    entry_price = models.FloatField()
    exit_price = models.FloatField()
    roe = models.FloatField()
    fee = models.FloatField()
    profit = models.FloatField()
    quantity = models.FloatField()
    open_date = models.DateTimeField()
    close_date = models.DateTimeField()
    stoch_open = models.FloatField()
    rsi_open = models.FloatField()
    tp_price = models.FloatField(null=True, default=None)
    sl_price = models.FloatField(null=True, default=None)
    close_method = models.CharField(null=True, default=None, max_length=10)
    tp_sl_ratio = models.FloatField(null=True)
    sl_limit = models.FloatField(null=True, default=None)
    sl_low_limit = models.FloatField(null=True, default=None)
    alt_TP_SL = models.IntegerField(null=True, default=0)
    timeframe = models.IntegerField(null=True, default=0)
    def __str__(self):
        return str(self.symbol) + ' - ' + self.type + ' - ' + str(self.alt_TP_SL) + ' - ' + str(self.timeframe)   \
            + ' - ' + str(self.profit)


#------------------------------for simulations that calculate the optimum variables---------------------------------

class Oportunities_sim(models.Model):
    symbol = models.OneToOneField(Symbol, on_delete=models.CASCADE)
    types = (('SELL', 'SELL'),('BUY', 'BUY'),('NONE','NONE'),('OPEN','OPEN'))
    type = models.CharField(max_length=4, choices=types, default='NONE')
    stock_rsi = models.BooleanField(default=False)
    macd = models.BooleanField(default=False)
    rsi = models.BooleanField(default=False)
    def __str__(self):
        return str(self.symbol) + ' - ' + self.type + ' - ' + str(self.stock_rsi) + ' - ' + str(self.macd) + ' - ' + str(self.rsi)


class Open_position_sim(models.Model):
    symbol = models.OneToOneField(Symbol, on_delete=models.CASCADE)
    types = (('SELL', 'SELL'),('BUY', 'BUY'))
    type = models.CharField(max_length=4, choices=types, default='NONE')
    entry_price = models.FloatField()
    quantity = models.FloatField()
    open_date = models.DateTimeField()
    stoch = models.FloatField()
    rsi = models.FloatField()
    tp_price = models.FloatField(null=True, default=None)
    sl_price = models.FloatField(null=True, default=None)
    atr = models.FloatField(null=True, default=None)
    ratr = models.FloatField(null=True, default=None)


class Closed_position_sim(models.Model):
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    types = (('SELL', 'SELL'), ('BUY', 'BUY'))
    type = models.CharField(max_length=4, choices=types)
    entry_price = models.FloatField()
    exit_price = models.FloatField()
    roe = models.FloatField()
    fee = models.FloatField()
    profit = models.FloatField()
    quantity = models.FloatField()
    open_date = models.DateTimeField()
    close_date = models.DateTimeField()
    stoch_open = models.FloatField()
    rsi_open = models.FloatField()
    tp_price = models.FloatField(null=True, default=None)
    sl_price = models.FloatField(null=True, default=None)
    close_method = models.CharField(null=True, default=None, max_length=10)
    tp_s = models.BooleanField(default=False)
    sp_s = models.BooleanField(default=False)
    predetermined_tp_sl = models.BooleanField(default=False)
    tp_sl_ratio = models.FloatField(null=True)
    sl_limit = models.FloatField(null=True, default=None)
    simulation = models.IntegerField(null=True, default=1)
    sl_low_limit = models.FloatField(null=True, default=None)
    ratr = models.FloatField(null=True, default=None)
    sim_info = models.CharField(null=True, default=None, max_length=100)

    def __str__(self):
        return self.type + ' - ' + str(self.profit)


class Optimum_parameter(models.Model):
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    types = (('SELL', 'SELL'), ('BUY', 'BUY'))
    type = models.CharField(max_length=4, choices=types, null=True, default=None)
    timeframe = models.FloatField(null=True, default=None)
    tp_sl_ratio = models.FloatField(null=True, default=None)
    sl_limit = models.FloatField(null=True, default=None)
    open_rsi = models.FloatField(null=True, default=None)
    positions = models.IntegerField(null=True, default=None, blank=True)
    avg_positions_day = models.FloatField(null=True, default=None, blank=True)
    duration = models.FloatField(null=True, default=None, blank=True)
    profit_loss_rate = models.FloatField(null=True, default=None, blank=True)
    pnl = models.FloatField(null=True, default=None)
    fee_total = models.FloatField(null=True, default=None, blank=True)
    q = models.FloatField(null=True, default=None)
    winning_rate_month = models.FloatField(null=True, default=None, blank=True)
    criteria = models.CharField(max_length=20, null=True, default=None, blank=True)
    sl_low_limit = models.FloatField(null=True, default=None)
    open_stoch = models.FloatField(null=True, default=None, blank=True)
    max_pnl = models.FloatField(null=True, default=None, blank=True)
    min_pnl = models.FloatField(null=True, default=None, blank=True)
    max_accumulated_loss = models.FloatField(null=True, default=None, blank=True)
    max_accumulated_profit = models.FloatField(null=True, default=None, blank=True)
    simulation = models.IntegerField(null=True, default=None)
    pnl_av = models.FloatField(null=True, default=None)
    factor_ajuste = models.FloatField(null=True, default=None)
    class Meta:
        unique_together = ['symbol', 'type', 'criteria', 'timeframe']
    def __str__(self):
        return str(self.symbol) + ' - ' + str(self.timeframe) + ' - ' + str(self.q)


class Simulations(models.Model):
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    types = (('SELL', 'SELL'), ('BUY', 'BUY'))
    type = models.CharField(max_length=4, choices=types)
    timeframe = models.FloatField(null=True, default=None)
    tp_sl_ratio = models.FloatField(null=True, default=None)
    sl_limit = models.FloatField(null=True, default=None)
    open_rsi = models.FloatField(null=True, default=None)
    positions = models.IntegerField(null=True, default=None)
    avg_positions_day = models.FloatField(null=True, default=None)
    duration = models.FloatField(null=True, default=None)
    profit_loss_rate = models.FloatField(null=True, default=None)
    pnl = models.FloatField(null=True, default=None)
    fee_total = models.FloatField(null=True, default=None)
    winning_rate_week = models.FloatField(null=True, default=None)
    roe = models.FloatField(null=True, default=None)
    sl_low_limit = models.FloatField(null=True, default=None)
    open_stoch = models.FloatField(null=True, default=None)
    max_pnl = models.FloatField(null=True, default=None)
    min_pnl = models.FloatField(null=True, default=None)
    max_accumulated_loss = models.FloatField(null=True, default=None)
    max_accumulated_profit = models.FloatField(null=True, default=None)
    wins_in_a_row = models.IntegerField(null=True, default=None)
    losses_in_a_row = models.IntegerField(null=True, default=None)
