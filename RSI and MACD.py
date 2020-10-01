'''
Buy Signal:
Wait for RSI 7 to move above 50
When RSI 7 is above 50, wait for MACD histogram to cross the 0-line from below
Buy on the candle close with stops at the candle’s low
Continue to hold the position until you get a reversal signal
Sell Signal:
Wait for RSI 7 to move below 50
When the RSI 7 is below 50, wait for MACD histogram to cross the 0-line from above
Sell on the candle close with stops at the candle’s high
Continue to hold the position until you get a reversal signal
'''
import backtrader as bt

#class to create the RSI indicator
class RSI(bt.Indicator):
    lines = ('rsi',)
    params = dict(rsi = 7)

    def __init__(self):
        rsi = bt.ind.RSI(self.data, period=self.params.rsi)

class MACD(bt.indicator):
    pass

class Dual_strategy(bt.Strategy):
    params = (('printlog',False))

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        
        self.dataclose = self.datas[0].close #reference to the close line
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        pass



#