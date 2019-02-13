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
    
    # 以下__開頭者為內部使用function
    def __generate_signal(self, condition_list):
        signal = pd.Series([True] * len(condition_list[0]))

        # 回傳所有條件的交集(這裡只處理"且")
        # 其實在外部輸入condition時就可以處理and(&), or(|)的條件
        # 但若在外部寫則會較繁瑣，因此仍保留此function
        for condition in condition_list:
            signal = condition & signal
        return signal
    
    def __generate_position(self, signal, buy_or_short='buy'):
        has_position = False
        positions = pd.Series(0, index=signal.index)
        if buy_or_short == 'buy':
            position = 1
        elif buy_or_short == 'short':
            position = -1
        
        # 若signal裡的condition_in出現進場訊號且沒有部位則進場
        # 若有部位且signal裡的condition_out出現出場訊號則平倉
        # 此種寫法尚未考量加減碼，透過buy_or_short決定建倉方向
        for i in range(len(positions)):
            if signal.condition_in.iloc[i] == True:
                if not has_position:
                    positions.iloc[i] = position
                    has_position = True
            elif signal.condition_out.iloc[i] == True:
                if has_position:
                    positions.iloc[i] = -1*position
                    has_position = False
        
        # 上述只標記進出場點位(未考量持倉狀況)且未考量買賣時機
        # 透過cumsum決定出部位狀況，例如：0,1,0,0,-1代表第二天出現進場訊號第五天出現出場訊號
        # cumsum後則變為0,1,1,1,0，意味在第二~四天時持有多頭部位
        # 接著透過shift決定出實際部位持有時間點，因為訊號出現後通常用下一資料點進出場(可由next_bar調整)
        # shift(1)後則變為na,0,1,1,1,0，則變為在第三~五天時持有多頭部位
        positions = positions.cumsum().shift(periods=self.next_bar)

        # 若最後一期有留倉則強制平倉
        if positions.iloc[-1] != 0:
            positions.iloc[-1] = 0
        return positions
    
    def __generate_trade_table(self, buy_or_short='buy'):

        # 持倉狀況(position)→進場後為1(多)或-1(空)，空手為0。
        # 上述例子：na,0,1,1,1,0，為第三~五天時持有多頭部位
        if buy_or_short == 'buy':
            position =  self.signal.stock_to_buy_position * 1000
            stock_price = self.stock_to_buy[self.trade_on]
        elif buy_or_short == 'short':
            position =  self.signal.stock_to_sellshort_position * 1000
            stock_price = self.stock_to_sellshort[self.trade_on]
        
        # 持有部位大小乘上股價與後即為持有部位價值(holdings)
        holdings = position * stock_price
        
        # 暫存日期(用stock_to_sellshort.date也一樣，因為已經preprocess後才送入class)
        date = self.stock_to_buy.date

        # 進出場點位(entry_exit_points)→多頭部位進場為1出場為-1，空頭部位進場為-1出場為1
        # 透過diff(差分)計算，以上述na,0,1,1,1,0例子而言，取diff()後為na,na,1,0,0,-1(第三天進場第六天平倉)
        entry_exit_points = position.diff()

        # 紀錄現金部位，概念相對複雜，解釋過程在help資料夾中
        cash = self.initial_capital - (entry_exit_points * stock_price).cumsum()

        # 紀錄部位總價值(浮動，因為有考量holdings)，現金+股票部位
        total_value = cash + holdings

        # 浮動權益不含初始資金
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
        
        # 建立訊號
        self.signal = pd.DataFrame()
        self.signal['condition_in'] = self.__generate_signal(condition_in)
        self.signal['condition_out'] = self.__generate_signal(condition_out)

        # 建立部位
        self.signal['stock_to_buy_position'] = self.__generate_position(self.signal, buy_or_short='buy')
        self.signal['stock_to_sellshort_position'] = self.__generate_position(self.signal, buy_or_short='short')

        # 儲存結果
        self.stock_to_buy_trade_table = self.__generate_trade_table(buy_or_short='buy')
        self.stock_to_sellshort_trade_table = self.__generate_trade_table(buy_or_short='short')