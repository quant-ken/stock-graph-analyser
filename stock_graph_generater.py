import pandas as
import plotly.offline as offline
import plotly.subplots                      # make_subplots
import plotly.graph_objs as graph_obj


class StockGraphGenerater:

    

    @classmethod
    def generate_graph(cls, summary, data_frame):

        # Get empty date
        date_all = pd.date_range(start=data_frame['date'].iloc[0], end=data_frame['date'].iloc[-1])
        date_obs = [d.strftime('%Y-%m-%d') for d in data_frame['date']]
        dt_breaks = [d for d in date_all.strftime('%Y-%m-%d').tolist() if not d in date_obs]

        moving_avg = ['sma5', 'sma20', 'sma100',
                      'sma200', 'ema5', 'ema20', 'ema100', 'ema200']

        # GRAPH PART
        # jupyter notebook 에서 출력
        offline.init_notebook_mode(connected=True)

        fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            specs=[[{"rowspan": 2}],
                   [None],
                   [{}]])

        fig.add_trace(graph_obj.Candlestick(
            x=data_frame.date,
            open=data_frame.open,
            high=data_frame.high,
            low=data_frame.low,
            close=data_frame.close,

            increasing_line_color='red',
            decreasing_line_color='blue',
            # y=data_frame.close,
            name='일봉'),
            row=1, col=1)

        for avg in moving_avg:
            fig.add_trace(graph_obj.Scatter(
                x=data_frame.date,
                y=data_frame[avg]),
                row=1, col=1)

        fig.add_trace(graph_obj.Bar(x=data_frame.date,
                                    y=data_frame.volume,
                                    name='거래량'),
                      row=3, col=1)


        fig.update_layout(title='{} - 일봉 그래프'.format(summary.name))
        fig.update_xaxes(rangeslider_visible=False)

        fig.update_xaxes(
            rangebreaks=[dict(values=dt_breaks)]  # hide dates with no values
        )

        fig.show()

        print("Get - Show :", time.time() - start)

    @classmethod
    def save_graph(cls):

        # Save plotly to html
        pass
