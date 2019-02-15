# strategy.py中__generate_trade_table function說明

執行__generate_trade_table後會出現類似以下表格(此內部function在strategy.py中會被執行兩次，以下以stock_to_buy_position為例)：

![trade_table](https://i.imgur.com/dNFb6rh.png)

**欄位說明**：
* *close_price*：
  進出場時使用的價格(隨指定參數(trade_on)改變，可能是high或其他價格)

* *stock_to_buy_position*：
  部位持有狀況

* *entry_exit_point*：
  部位進出場點

* *holdings*：
  部位持有價值，stock_to_buy_position乘上*close_price* 欄位

* *entry_exit_point * close*：
  買賣股票產生的現金流

* *cumsum(entry_exit_point * close)*：
  因交易產生的現金流狀況(累積)，可用成本角度思考

* *cash*:
  現金部位，初始資金(例子中為100)減去*cumsum(entry_exit_point * close)* 欄位

  (可透過成本角度思考*cumsum(entry_exit_point * close)* 欄位)

* total：
  *cash* 欄位加上*holdings* 欄位

* total - cpaital：
  累積獲利(權益)
  
*cumsum(entry_exit_point * close)* 欄位僅記錄了進出過程的現金流狀況，因此cash也僅反應每筆交易所產生的現金流入流出(只反映已實現獲利/損失，未能反映潛在獲利/損益)，透過加上*holdings* 欄位(隨價格變動)得到*total* 欄位，便能得知整體帳戶價值概況(包含潛在獲利/損失)。

執行__generate_trade_table()後產生的表格將存於stock_to_xxx_trade_table，而上述*total - cpaital* 欄位將存於*cumulative_profit* 欄位中，此欄位反映整體帳戶價值概況，但送進Analysis.py中計算淨利曲線時只會考量已實現獲利/損失，但仍可以呼叫此欄位以繪圖方式檢視整體帳戶價值(尚未寫此功能2019/2/15)。

**備註：**
* help資料夾中有excel範例檔

* 上述表格中的*stock_to_buy_position* 欄位已於__generate_position()中考量next_bar參數