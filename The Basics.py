from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
# Import the backtrader platform
import backtrader as bt
# Create a Stratey
import backtrader as bt
from datetime import datetime
import backtrader.indicator as btind

class MyStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataopen = self.datas[0].open
        self.dataclose = self.datas[0].close #reference to the close line
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

    #checks whether broker accepted order, adds result to log
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

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        # Write down: no pending order
        self.order = None

    #THIS function does not work
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
 
if __name__ == '__main__':

    # Create a cerebro entity
    cerebro = bt.Cerebro()
    startcash = 10000000   #50mil
    cerebro.broker.setcash(startcash)
    cerebro.broker.setcommission(commission=0.001)
    # Add a strategy
    cerebro.addstrategy(MyStrategy)
    cerebro.addanalyzer(bt.analyzers.PyFolio)
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))  #current folder
    datapath = os.path.join(modpath, '^GSPC.csv')             #add data to path

    data = bt.feeds.GenericCSVData(dataname=datapath, fromdate=datetime(2014, 1, 1), todate=datetime(2020, 12, 31), nullvalue=0.0, dtformat=('%Y-%m-%d'), datetime=0, high=2, low=3, open=1,close=4,volume=5)

    cerebro.adddata(data)
    # Run over everything
    cerebro.run()
    #Get final portfolio Value
    portvalue = cerebro.broker.getvalue()
    pnl = portvalue - startcash

    #Print out the final result
    print('Final Portfolio Value: ${}'.format(portvalue))
    print('P/L: ${}'.format(pnl))
    print('Total Return: {}'.format((pnl/portvalue)*100))

    #Finally plot the end results
    cerebro.plot(style='candlestick')
    