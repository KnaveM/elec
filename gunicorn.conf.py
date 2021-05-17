from os import access


workers = 1 # socketio限制只能用一个?    # 定义同时开启的处理请求的进程数量，根据网站流量适当调整
# worker_class = "gevent"   # 采用gevent库，支持异步处理请求，提高吞吐量
# for socketio
worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"
bind = "0.0.0.0:80"
# capture_output = True
import datetime
# accesslog = './log/access' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") +'.log'
errorlog = './log/error' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") +'.log'
# errorlog中的信息比较重要 主要是显示debug信息
# accesslog中的信息太多了, 每次请求的信息都会被记录