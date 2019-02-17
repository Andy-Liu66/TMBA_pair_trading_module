# TMBA_pair_trading_module
## 簡介：
此為一個策略回測模組，輸入股價資料及進出場條件後便能進行回測，且提供策略基本績效資訊，共有四個資料夾：
  * **pair_trading**：

    存放主要程式碼。
  * **data**：

    存放Demo使用之股價資料(0050成分股，日頻率)。
  * **help**：

    存放程式碼較複雜處的解釋。
  * **example**：

    存放模組使用例子。

pair_trading資料夾中又各自含有3個主要程式：
  * [**basic_tool.py**](https://github.com/Andy-Liu66/TMBA_pair_trading_module/blob/master/pair_trading/basic_tool.py)：

    存放撰寫策略會使用的基本function，及資料前處理所需function。
     
  * [**strategy.py**](https://github.com/Andy-Liu66/TMBA_pair_trading_module/blob/master/pair_trading/strategy.py)：

    策略物件，輸入股價資料、進出場條件，及其他交易相關參數。
    
  * [**analysis.py**](https://github.com/Andy-Liu66/TMBA_pair_trading_module/blob/master/pair_trading/analysis.py)：
  
    分析策略績效物件，輸入策略。

## 要求：
* **使用套件**：
  * pandas
  * numpy
  * matplotlib
  * datetime

* **欲使用的股價資料**：
  * 日期須為datetime object(需依據日期遞增排序)
  * 使用數值須為float
  * column名稱皆為小寫

## Demo：
例子存放於example中，以下簡要介紹使用方法：

假設目前有stock_2330(台積電)、stock_1101(台泥)兩支股票要進行配對交易，且其所需之技術指標皆以計算完畢。

#### 檢視資料：
```python
stock_2330.head()
```
<table border="1" class="dataframe">  <thead>    <tr style="text-align: right;">      <th></th>      <th>id</th>      <th>name</th>      <th>date</th>      <th>open</th>      <th>high</th>      <th>low</th>      <th>close</th>      <th>volume</th>      <th>ma20</th>      <th>ma5</th>    </tr>  </thead>  <tbody>    <tr>      <th>0</th>      <td>2330</td>      <td>台積電</td>      <td>2001-01-09</td>      <td>22.59</td>      <td>23.22</td>      <td>22.59</td>      <td>23.22</td>      <td>44746</td>      <td>20.9190</td>      <td>21.894</td>    </tr>    <tr>      <th>1</th>      <td>2330</td>      <td>台積電</td>      <td>2001-01-10</td>      <td>23.47</td>      <td>23.71</td>      <td>23.09</td>      <td>23.47</td>      <td>33171</td>      <td>20.9440</td>      <td>22.568</td>    </tr>    <tr>      <th>2</th>      <td>2330</td>      <td>台積電</td>      <td>2001-01-11</td>      <td>23.71</td>      <td>23.84</td>      <td>22.97</td>      <td>23.09</td>      <td>36399</td>      <td>20.9690</td>      <td>22.942</td>    </tr>    <tr>      <th>3</th>      <td>2330</td>      <td>台積電</td>      <td>2001-01-12</td>      <td>23.22</td>      <td>23.47</td>      <td>23.09</td>      <td>23.47</td>      <td>27240</td>      <td>21.0440</td>      <td>23.118</td>    </tr>    <tr>      <th>4</th>      <td>2330</td>      <td>台積電</td>      <td>2001-01-15</td>      <td>23.47</td>      <td>23.59</td>      <td>23.09</td>      <td>23.59</td>      <td>25695</td>      <td>21.1315</td>      <td>23.368</td>    </tr>  </tbody></table>

#### 撰寫進出場策略(Strategy)：
```python
from pair_trading.basic_tool import lag, maximum, crossunder, preprocess
# pair_trading.basic_tool中仍有minimum, crossover可使用
from pair_trading.strategy import Strategy

# 股價前處理(主要依據日期取交集)
stock_2330, stock_1101 = preprocess(stock_2330, stock_1101)

# 撰寫進出場條件
# (條件為list，若依序填入則為條件皆符合才觸發("且"))
# 進場訊號
condition_in = [
    # 此為"且"的寫法
    # 台積電今日收盤價高過於前十日最高價
    stock_2330.close > lag(maximum(stock_2330.high, 10)),
    # "且"今日收紅k
    stock_2330.close > stock_2330.open
]

# 出場訊號
condition_out = [
    # 此為"或"的寫法
    (
        # 台積電20日平均死亡交叉5日平均
        (crossunder(stock_2330.ma20, stock_2330.ma5)) |
        # "或"今日收小於3%的黑k
        ((stock_2330.close - stock_2330.open)/stock_2330.open < -0.03)
    )
]

# 建立Strategy物件
example_strategy = Strategy(
    # 訊號出現後何時進出場，0為出現後馬上執行交易，1為下一個價格執行交易，2...以此類推
    next_bar=1,
    # 以甚麼價格進行交易
    trade_on='close',
    # 初始資金(後續分析中沒有使用到)
    initial_capital=1000000,
    # 交易稅
    tax_rate=0.003,
    # 交易成本(率)
    cost=0.001425
)

# 開始回測
example_strategy.run(
    # condition_in成立時欲做多的股票
    stock_2330,
    # condition_in成立時欲放空的股票
    stock_1101,
    # 進場訊號
    condition_in,
    # 出場訊號
    condition_out,
    # 對沖比率，預設為auto，亦即將兩兩欲交易的價格(trade_on)進行比較，
    # 將價格較高者部位設為1，價格較低者部位則由高價除以低價並四捨五入
    # 也可以輸入list如：[2, 1]，將會以2:1的部位進行交易(stock_to_buy : stock_to_sellshort)
    hedge_ratio='auto'
)
```

#### 分析策略結果(Analysis)
```python
# 建立分析物件
example_strategy_analysis = Analysis(
    # 欲分析的策略
    example_strategy
)

# 進行分析
example_strategy_analysis.run()

# 策略績效基本資訊
example_strategy_analysis.summary(
    # 檢視策略績效總結果，另有'buy'(做多交易), 'sellshort'(放空交易)
    select_result='total'
)
```

<table border="1" class="dataframe">  <thead>    <tr style="text-align: right;">      <th></th>      <th>total_profit</th>      <th>average_return</th>      <th>winning_rate</th>      <th>max_drowdown</th>      <th>average_holding_days</th>      <th>total_trade_number</th>    </tr>  </thead>  <tbody>    <tr>      <th>0</th>      <td>-13446.7115</td>      <td>-0.0156</td>      <td>0.451</td>      <td>91340.9822</td>      <td>39.5784</td>      <td>102</td>    </tr>  </tbody></table>

```python
# 策略權益曲線
example_strategy_analysis.plot_equity_curve(
    # 另有'total'(總交易), 'sellshort'(放空交易)
    select_result='buy'
)
```

![equity_curve](https://i.imgur.com/PF9yvnx.png)

```python
# 策略獲利與虧損(每筆)
example_strategy_analysis.plot_profit_and_loss_per_trade(
    # 另有'total'(總交易), 'buy'(做多交易)
    select_result='sellshort'
)
```
![profit_and_loss](https://i.imgur.com/IMZRh6J.png)

(詳細舉例內容見example資料夾)

**備註：**
* 目前只能針對股票做單邊買賣，strategy.run()中第一個輸入的參數*stock_to_buy*為進場條件達成便做多的股票，第二個參數*stock_to_sellshort*則為相對於*stock_to_buy*而放空的股票，因此兩者部位放向完全相反，在一個策略中*stock_to_buy*的股票只會一直做多，而*stock_to_sellshort*則只會做空，例如：一個策略中，條件符合時做多台積電並放空另一支股票，在同個策略下就不會放空台積電然後做多另一支股票。
  
  若策略邏輯是想要condition_out出現時就放空原先*stock_to_buy*的股票(因此做多原先*stock_to_sellshort*的股票)，則只需要更改建立*strategy*物件的順序。延續Demo的例子，若想要放空台積電並做多台泥則更改程式碼如下(在condition_in, condition_out不變下)：

  ```python
  # 開始回測
  example_strategy.run(
      # condition_in成立時欲做多的股票
      stock_1101,
      # condition_out成立時欲放空的股票
      stock_2330,
      # 進場訊號
      condition_out,
      # 出場訊號
      condition_in,
  )
  ```

  也就是將原先的出場策略變成台泥的進場做多策略，此時台積電則變成放空，而原先的進場策略則變為台泥多單出場訊號，對台積電而言則是空單出場訊號。如此，便能達成單一股票多單、空單皆能執行，但如此一來便會產生兩個*strategy*，績效衡量上則得分開看，解決方案為另外寫一個class把上述兩*strategy*包起來(尚未新增此功能，2019/2/16)變成單一策略，以進行後續分析。

  **(但實際正確性仍需檢查)**

* 此模組不只用適用配對交易，也可檢視基本做多策略，因為寫法如上述只會對同一股票做同樣方向的單(配對的股票空頭部位完全相反於做多股票的部位)，因此在績效分析中只需將*select_result*設定為*buy*，即可檢視只考量做多情況下的策略績效。

## 限制與改善方法：
* **尚未考量加減碼**：

  須從signal表更改。

* **尚未考量停損停利**：

  需要考量到交易表(stock_to_xxx_trade_table)，可能須透過for loop去看損益狀況並決定是否提前平倉。

* **更彈性的價格進出場**：

  目前進出場只能用一樣的，需透過更改*strategy.py*中__generate_trade_table()裡計算損益的部分；若更改則計算浮動損益(*cumulative_profit*)的方式也將需要更改。

* **更彈性的進出場時間點**：

  若要改何時進場則須改*strategy.py*中__generate_position()裡的for loop，在標記的時候改.iloc[i+x]即可(須注意在資料最後出現訊號則可能有error)，但通常會用next bar進場(因此目前沒寫，2019/2/16)，若改了則positions.cumsum().shift()也須改掉。

## 疑慮與可新增功能：
* **疑慮**：

  * 在分析對沖組合每筆交易報酬率時，使用相加(做多的報酬率加放空的報酬率)的方式似乎有些奇怪，做多與放空各自報酬率皆以進場價為基準(分母)
* **可新增功能**：

  * 可以畫持倉過程的總權益(cash + holdings)概況

  * 可以分析*cash*的狀況，例如：在買股票時是否會出現現金水位不夠的狀況(目前未考量放空的保證金問題，否則也可看是否會被斷頭的問題)

## 參考資料：
* **進出場寫法**：
  * [victorgau's GitHub](https://github.com/victorgau/PyConTW2018Tutorial/blob/master/06.%20strategies/%E9%80%B2%E5%87%BA%E5%A0%B4%E7%AD%96%E7%95%A5.ipynb)

  * [Backtesting a Moving Average Crossover in Python with pandas](https://www.quantstart.com/articles/Backtesting-a-Moving-Average-Crossover-in-Python-with-pandas)

* **計算max drowdown寫法**：
  * [Start, End and Duration of Maximum Drawdown in Python](https://stackoverflow.com/questions/22607324/start-end-and-duration-of-maximum-drawdown-in-python)

* **其他現有類似交易套件**：
  * [https://www.quantstart.com/articles/backtesting-systematic-trading-strategies-in-python-considerations-and-open-source-frameworks](https://www.quantstart.com/articles/backtesting-systematic-trading-strategies-in-python-considerations-and-open-source-frameworks)
