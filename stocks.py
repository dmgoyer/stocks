import datetime as dt
from datetime import date, timedelta
from datetime import datetime
import pandas as pd
import yfinance as yf
import pandas_datareader as pdr
from bokeh.io import curdoc, show
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, PreText, TextInput, Button, DatePicker, LinearAxis, Range1d
from bokeh.plotting import figure

start_data = dt.datetime(2010,1,1)
end_data = dt.datetime.now()

def stocks_data(ticker, start, end):
    adj_close = []
    data = yf.Ticker(ticker)
    df = data.history(period='1d', start=start_data, end=end_data)
    df['MA_50'] = df['Close'].rolling(window=50).mean()
    df['MA_200'] = df['Close'].rolling(window=200).mean()
    df['MACD'] = (df['Close'].ewm(span=12, adjust=False).mean()) - (df['Close'].ewm(span=26, adjust=False).mean())
    df['Roll 9'] = df['MACD'].ewm(span=9, adjust=False).mean()
    s_ = df.index.searchsorted(datetime.strptime(start, '%Y-%m-%d'))
    e_ = df.index.searchsorted(datetime.strptime(end, '%Y-%m-%d'))
    df = df.iloc[s_:e_]
    source = ColumnDataSource(df)
    return source

def update_data():
    t = ticker_input.value
    s = start.value
    e = end.value
    src = stocks_data(t, s, e)
    source.data.update(src.data)
    price.y_range.start = min(src.data['Close'].min(), src.data['MA_50'].min(), src.data['MA_200'].min())
    price.y_range.end = max(src.data['Close'].max(), src.data['MA_50'].max(), src.data['MA_200'].max())
    price.extra_y_ranges['Volume'].start = src.data['Volume'].min()
    price.extra_y_ranges['Volume'].end = src.data['Volume'].max()

ticker_input = TextInput(value='GE', title='Company Symbol: ')
button = Button(label='Show', button_type='success')

start = DatePicker(title='Start Date: ', value=date.today()-timedelta(weeks=13), min_date=date(2010, 1, 1), max_date=date.today(), width=375)
end = DatePicker(title='End Date: ', value=date.today(), min_date=date(2010, 1, 1), max_date=date.today(), width=375)
source = stocks_data(ticker_input.value, start.value, end.value)

tool_bar = 'crosshair, reset, save'
minimum = min(source.data['Close'].min(), source.data['MA_50'].min(), source.data['MA_200'].min())
maximum = max(source.data['Close'].max(), source.data['MA_50'].max(), source.data['MA_200'].max())

price = figure(plot_height=400, plot_width=750, title="Stock Price", tools=tool_bar, x_axis_type='datetime', x_axis_label = 'Date', y_axis_label = 'Adjusted Close Price ($)')
# First Axis for Close price
price.line('Date', 'Close', source=source, legend_label='Close', color='black') # Close
price.line('Date', 'MA_50', source=source, legend_label='MA(50)', color='blue') # MA_50
price.line('Date', 'MA_200', source=source, legend_label='MA(200)', color='pink') # MA_200
price.y_range = Range1d(minimum, maximum)
# second Axis for Volume
price.extra_y_ranges = {'Volume': Range1d(source.data['Volume'].min(), source.data['Volume'].max())}
price.add_layout(LinearAxis(y_range_name='Volume'), "right")
price.line('Date', 'Volume', source=source, legend_label='Volume', y_range_name='Volume', color='green') #Volume
price.legend.location = 'top_left'
price.legend.click_policy='hide'

macd = figure(plot_height=400, plot_width=750, title="MACD", tools=tool_bar, x_axis_type='datetime', x_axis_label = 'Date', y_axis_label = 'MACD (12/26)')
macd.line('Date', 'MACD', source=source, color='orange', legend_label='MACD') # MACD
macd.line('Date', 'Roll 9', source=source, color='blue', legend_label='EMA') # 9 Day EMA of MACD
macd.line('Date', y=0, source=source, color='green', legend_label='Centerline')
macd.legend.location = 'top_left'

button.on_click(update_data)

#Create layouts
start_end = row(start, end)
graphs = column(price, macd)
curdoc().add_root(column(ticker_input, start_end, button, graphs))
