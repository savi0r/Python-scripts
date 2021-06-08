import datetime
import redis
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import psutil

#connect to redis container
r = redis.StrictRedis('redis', 6379, charset="utf-8", decode_responses=True)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H4('Resource usage'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ])
)

#have a snapshot of metrics right now
@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def update_metrics(n):
    # drop miliseconds and then convert to iso format to make the date comprehensible for redis
    dt=datetime.datetime.now().replace(microsecond=0).isoformat() 
	#Sorted sets are used here
    r.zadd(dt,{"cpu":psutil.cpu_percent()})
    r.zadd(dt,{"mem":psutil.virtual_memory().percent})
    r.zadd(dt,{"disk":psutil.disk_usage('/').percent})
    
    # delete data after 1800 seconds 
    r.expire(dt,1800) 
    
	#show this moment values on top of the page
    cpu=r.zscore(dt,"cpu")
    mem=r.zscore(dt,"mem")
    disk=r.zscore(dt,"disk")
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span('CPU: {0:.2f}'.format(cpu), style=style),
        html.Span('RAM: {0:.2f}'.format(mem), style=style),
        html.Span('Disk Usage: {0:0.2f}'.format(disk), style=style)
    ]


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    
    data = {
        'time': [],
        'mem': [],
        'cpu': [],
        'disk': []
    }

    # Collect some data
    for i in range(50):
        time = datetime.datetime.now() - datetime.timedelta(seconds=i*1)
       
        time=time.replace(microsecond=0).isoformat()
        if r.zscore(time,"cpu") is not None:
            cpu=r.zscore(time,"cpu")
            mem=r.zscore(time,"mem")
            disk=r.zscore(time,"disk")
            data['cpu'].append(cpu)
            data['mem'].append(mem)
            data['disk'].append(disk)
            data['time'].append(time)

    # Create the graph with subplots
    # fig = plotly.tools.make_subplots(rows=1, cols=1, vertical_spacing=0.2)
    # fig['layout']['margin'] = {
    #     'l': 30, 'r': 10, 'b': 30, 't': 10
    # }
    # fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}
    # fig['layout']['yaxis'] ={
    #     'range':[0,100]
    #     # showgrid=True,
    #     # zeroline=True,
    #     # showline=True,
    #     # gridcolor='#bdbdbd',
    #     # gridwidth=2,
    #     # zerolinecolor='#969696',
    #     # zerolinewidth=4,
    #     # linecolor='#636363',
    #     # linewidth=6
    # }
    
    # fig.append_trace({
    #     'x': data['time'],
    #     'y': data['disk'],
    #     'name': data['cpu'],
    #     'name': 'disk',
    #     'mode': 'lines+markers',
    #     'type': 'scatter'
    # }, 1, 1)
    # # fig.append_trace({
    # #     'x': data['time'],
    # #     'y': data['cpu'],
    # #     'text': data['time'],
    # #     'name': 'cpu',
    # #     'mode': 'lines+markers',
    # #     'type': 'scatter'
    # # }, 2, 1)
    # # fig.append_trace({
    # #     'x': data['time'],
    # #     'y': data['mem'],
    # #     'text': data['time'],
    # #     'name': 'mem',
    # #     'mode': 'lines+markers',
    # #     'type': 'scatter'
    # # }, 3, 1)
    fig = go.Figure()
    #define a fix scale
    fig.layout.yaxis ={
        'range':[0,100]
        # more fancier?
        # 'showgrid':True,
        # 'zeroline':True,
        # 'showline':True,
        # 'gridcolor':'#bdbdbd',
        # 'gridwidth':2,
        # 'zerolinecolor':'#969696',
        # 'zerolinewidth':4,
        # 'linecolor':'#636363',
        # 'linewidth':6
        }
    fig.layout.yaxis2 ={
        'range':[0,100]
        }
    fig.layout.yaxis3 ={
        'range':[0,100]
        }
    # add plots on different Y axis
    fig.add_trace(go.Scatter(
    x=data['time'],
    y=data['cpu'],
    name="CPU"
    ))


    fig.add_trace(go.Scatter(
        x=data['time'],
        y=data['mem'],
        name="RAM",
        yaxis="y2"
    ))

    fig.add_trace(go.Scatter(
        x=data['time'],
        y=data['disk'],
        name="Disk",
        yaxis="y3"
    ))
    # Create axis objects
    fig.update_layout(
        xaxis=dict(
            domain=[0.3, 0.7]
        ),
        yaxis=dict(
            title="CPU",
            titlefont=dict(
                color="#1f77b4"
            ),
            tickfont=dict(
                color="#1f77b4"
            )
        ),
        yaxis2=dict(
            title="RAM",
            titlefont=dict(
                color="#ef553b"
            ),
            tickfont=dict(
                color="#ef553b"
            ),
            anchor="free",
            overlaying="y",
            side="left",
            position=0.15
        ),
        yaxis3=dict(
            title="Disk",
            titlefont=dict(
                color="#00cc96"
            ),
            tickfont=dict(
                color="#00cc96"
            ),
            anchor="x",
            overlaying="y",
            side="right"
        ),
       
    )
    return fig


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
