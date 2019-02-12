import pandas as pd

class Strategy:
    
    def __init__(
        self, next_bar=1, trade_on='close',
        initial_capital = 1000000, tax_rate=0.003, cost=0.001425
    ):
        self.next_bar = next_bar
        self.trade_on = trade_on
        self.initial_capital = initial_capital
        self.tax_rate = tax_rate
        self.cost = cost
    
    def __generate_signal(self, condition_list):
        signal = pd.Series([True] * len(condition_list[0]))
        for condition in condition_list:
            signal = condition & signal
        return signal
    
    def __generate_position(self, signal, trade_type='buy'):
        has_position = False
        position = pd.Series(0, index=signal.index)
        if trade_type == 'buy':
            buy_or_sell = 1
        elif trade_type == 'sellshort':
            buy_or_sell = -1

        for i in range(len(position)):
            if signal.condition_in.iloc[i] == True:
                if not has_position:
                    position.iloc[i] = buy_or_sell
                    has_position = True
            elif signal.condition_out.iloc[i] == True:
                if has_position:
                    position.iloc[i] = -1*buy_or_sell
                    has_position = False
        position = position.cumsum().shift(periods=self.next_bar)
        # 若最後一期有留倉則強制平倉
        if position.iloc[-1] != 0:
            position.iloc[-1] = 0
        return position
    
    def __generate_trade_table(self, buy_or_short='buy'):
        # 持有訊號(position)→進場後為1(多)或-1(空)，空手為0。
        # 例如：01110，則代表第二天開始持有部位第五天平倉，乘上股價與股數後即為持有部位價值
        if buy_or_short == 'buy':
            position =  self.signal.stock_to_buy_position * 1000
            stock_price = self.stock_to_buy[self.trade_on]
            date = self.stock_to_buy.date
        elif buy_or_short == 'short':
            position =  self.signal.stock_to_sellshort_position * 1000
            stock_price = self.stock_to_sellshort[self.trade_on]
            date = self.stock_to_buy.date
        
        holdings =  position * stock_price
        # 進出場點位(entry_exit_points)→多頭部位進場為1出場為-1，空頭部位進場為-1出場為1
        # 透過diff(差分)計算，以上述01110例子而言，取diff()後為na,1,0,0,-1(第二天進場第五天平倉)
        entry_exit_points = position.diff()
        # 紀錄現金部位，概念相對複雜，解釋過程在help資料夾中
        cash = self.initial_capital - (entry_exit_points * stock_price).cumsum()
        # 紀錄部位總價值→現金+股票部位
        total_value = cash + holdings
        # 累積報酬
        cumulative_profit = total_value - self.initial_capital

        trade_table = pd.DataFrame([])
        trade_table['date'] = date
        trade_table[self.trade_on + '_price'] = stock_price
        trade_table['holdings'] = holdings
        trade_table['entry_exit_points'] = entry_exit_points
        trade_table['cash'] = cash
        trade_table['total_value'] = total_value
        trade_table['cumulative_profit'] = cumulative_profit
        return trade_table

    def run(self, stock_to_buy, stock_to_sellshort ,condition_in, condition_out):
        self.stock_to_buy = stock_to_buy
        self.stock_to_sellshort = stock_to_sellshort
        self.condition_in = condition_in
        self.condition_out = condition_out
        
        
        signal = pd.DataFrame()
        signal['condition_in'] = self.__generate_signal(condition_in)
        signal['condition_out'] = self.__generate_signal(condition_out)
        signal['stock_to_buy_position'] = self.__generate_position(signal, trade_type='buy')
        signal['stock_to_sellshort_position'] = self.__generate_position(signal, trade_type='sellshort')
        self.signal = signal
        self.buy_stock_result = self.__generate_trade_table(buy_or_short='buy')
        self.sellshort_stock_result = self.__generate_trade_table(buy_or_short='short')