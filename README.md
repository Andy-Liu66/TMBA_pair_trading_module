# TMBA_pair_trading_module
## 簡介：

## 要求：
* 使用套件：
  * pandas
  * numpy
  * matplotlib
  * datetime

* 欲使用的股價資料：
  * 日期須為datetime object(需依據日期遞增排序)
  * 使用數值須為float
  * column名字皆為小寫

## 限制與改善方法：
* 尚未考量加減碼：

  須從signal表更改。

* 尚未考量停損停利：

  需要考量到交易表(stock_to_xxx_trade_table)，可能須透過for loop去看損益狀況並決定是否提前平倉。

* 更彈性的價格進出場：

  目前進出場只能用一樣的，需透過更改__generate_trade_table()裡計算損益的部分；若更改則計算浮動損益的方式也將需要更改。

* 更彈性的進出場時間點：

  若要改何時進場則須改__generate_position()裡的for loop標記的時候改.iloc[i+x]即可(須注意載資料最後出現訊號則可能有error，但通常會用next bar進場因此目前沒寫)，若改了則positions.cumsum().shift()也須改掉。

* 目前只能針對商品做單邊買賣，例如：條件符合時買台積電並空另一支股票，就不能賣台積電然後多另一支股票

## 參考資料：
* 進出場寫法：
  * [victorgau's GitHub](https://github.com/victorgau/PyConTW2018Tutorial/blob/master/06.%20strategies/%E9%80%B2%E5%87%BA%E5%A0%B4%E7%AD%96%E7%95%A5.ipynb)

  * [Backtesting a Moving Average Crossover in Python with pandas](https://www.quantstart.com/articles/Backtesting-a-Moving-Average-Crossover-in-Python-with-pandas)

* 計算max drowdown寫法：
  * [Start, End and Duration of Maximum Drawdown in Python](https://stackoverflow.com/questions/22607324/start-end-and-duration-of-maximum-drawdown-in-python)

* 其他現有交易套件：
  * [https://www.quantstart.com/articles/backtesting-systematic-trading-strategies-in-python-considerations-and-open-source-frameworks](https://www.quantstart.com/articles/backtesting-systematic-trading-strategies-in-python-considerations-and-open-source-frameworks)
