workers = 1 # socketio限制只能用一个?    # 定义同时开启的处理请求的进程数量，根据网站流量适当调整
# worker_class = "gevent"   # 采用gevent库，支持异步处理请求，提高吞吐量
# for socketio
worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"
bind = "0.0.0.0:80"