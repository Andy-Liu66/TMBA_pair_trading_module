import pandas as pd


class Analysis:
    
    def __init__(self, strategy):
        self.strategy = strategy
        self.stock_to_buy_trade_table = self.strategy.stock_to_buy_trade_table
        self.stock_to_sellshort_trade_table = self.strategy.stock_to_sellshort_trade_table
    
    def __parse_trade_result(self, buy_or_short='buy'):
        # 找出進出場的index
        if buy_or_short == 'buy':
            direction = 1
            trade_table = self.stock_to_buy_trade_table.reset_index(drop=True)
        elif buy_or_short == 'short':
            direction = -1
            trade_table = self.stock_to_sellshort_trade_table.reset_index(drop=True)
        entry_exit_index = pd.DataFrame({
            'entry': trade_table[trade_table.entry_exit_points*direction > 0].index,
            'exit': trade_table[trade_table.entry_exit_points*direction < 0].index
        }) 

        # 紀錄交易結果相關資訊
        trade_result = pd.DataFrame([])
        for i in range(len(entry_exit_index)):
            current_index = entry_exit_index.iloc[i]
            temp_entry_index, temp_exit_index = current_index.entry, current_index.exit
            temp_table = trade_table.iloc[temp_entry_index: temp_exit_index+1]
            temp_table = temp_table.copy()

            # 紀錄進出場日期與持有時間
            entry_date = temp_table.date.iloc[0]
            exit_date = temp_table.date.iloc[-1]
            holding_date = (exit_date - entry_date).days

            # 記錄進出場價格
            # 第2個column為價格資料，因為可能是用其他價格進行交易例如：open, high等，因此用index的方式呼叫
            entry_price = temp_table.iloc[0, 1]
            exit_price = temp_table.iloc[-1, 1]

            # 找出MFE, MAE
            # 扣掉累加的報酬才能找出發生在當筆交易的損益狀況
            temp_table['potential_profit'] = temp_table.cumulative_profit - temp_table.cumulative_profit.iloc[0]
            maximum_favorable_excursion = temp_table['potential_profit'].max()
            maximum_adverse_excursion = temp_table['potential_profit'].min()

            # 紀錄報酬
            actual_payoff = temp_table['potential_profit'].iloc[-1]
            actual_return = actual_payoff/abs(temp_table.holdings.iloc[0])

            # 將資料整理成dataframe
            temp_result = pd.DataFrame({
                'entry_date': entry_date,
                'exit_date': exit_date,
                'holding_date': holding_date,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'actual_payoff': actual_payoff,
                'actual_return': actual_return,
                'maximum_favorable_excursion': maximum_favorable_excursion,
                'maximum_adverse_excursion': maximum_adverse_excursion
            }, columns=[
                # 需指定columns否則順序會跑掉
                'entry_date',
                'exit_date',
                'holding_date',
                'entry_price',
                'exit_price',
                'actual_payoff',
                'actual_return',
                'maximum_favorable_excursion',
                'maximum_adverse_excursion'
            ], index=[i])

            # 合併dataframe
            trade_result = pd.concat([trade_result, temp_result])
        return trade_result
    
    def run(self):
        self.stock_to_buy_trade_result = self.__parse_trade_result(buy_or_short='buy')
        self.stock_to_sellshort_trade_result = self.__parse_trade_result(buy_or_short='short')