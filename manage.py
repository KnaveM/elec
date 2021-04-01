import sys
import os
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db #, socketio
from app.models import *

app = create_app(os.getenv("FLASK_CONFIG") or "default")
manager = Manager(app)
migrate = Migrate(app, db)

def initdb():
    "初始化数据库"
    with app.app_context():
        db.drop_all()
        db.create_all()
        u = User(username="test", password="testtest")
        db.session.add(u)
        db.session.commit()
        ui = UserInfo(u, email="testa@test.com", name='zhang',
                        phone='+86-18866667777', address="daheishan", user_id=u.id)
        db.session.add(ui)
        db.session.commit()

        si = StoreInfo(u, name='teststore', address='daheishanjiao',
                        contact="zhangsan", phone="18766665555")
        db.session.add(si)
        db.session.commit()
        fi = FactoryInfo(u, name='testfactory', address='testaddress', contact='lisi', phone='19711112222', complaint_department='department', complaint_method='method')
        db.session.add(fi)
        db.session.commit()
        p1 = Product(fi, name="testp1")
        db.session.add(p1)
        p2 = Product(fi, name="testp2")
        db.session.add(p2)
        p3 = Product(fi, name="testp3")
        db.session.add(p3)
        p4 = Product(fi, name="testp4")
        db.session.add(p4)
        p5 = Product(fi, name="testp5")
        db.session.add(p5)
        db.session.commit()


        # test code
        u = User.query.first()
        ps = Product.query.all()
        [u.add_to_cart(p) for p in ps]
        db.session.add(u)
        db.session.commit()

        # fi = FactoryInfo()
        
        # import datetime
        # o = Order(money=998, deadline=datetime.datetime.utcnow())
        # db.session.add(o)
        # db.session.commit()


def make_shell_context():
    return dict(app=app, db=db, User=User, initdb=initdb)


# TODO: socketio
class SocketioServer(Server):
    def __call__(self, app, host, port, use_debugger, use_reloader,
                 threaded, processes, passthrough_errors, ssl_crt, ssl_key):
        # we don't need to run the server in request context
        # so just run it directly

        if use_debugger is None:
            use_debugger = app.debug
            if use_debugger is None:
                use_debugger = True
                if sys.stderr.isatty():
                    print(
                        "Debugging is on. DANGER: Do not allow random users to connect to this server.", file=sys.stderr)
        if use_reloader is None:
            use_reloader = use_debugger

        if None in [ssl_crt, ssl_key]:
            ssl_context = None
        else:
            ssl_context = (ssl_crt, ssl_key)

        # socketio.run(app, host=host, port=port, **self.server_options)

manager.add_command('run', Server(host='0.0.0.0', port=80, threaded=True))
# manager.add_command('runserver', SocketioServer(host='0.0.0.0', port=80))
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)  # 转移数据库用

if __name__ != '__main__':
    # 如果不是直接运行，则将日志输出到 gunicorn 中
    import logging
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


if __name__ == '__main__':
    manager.run()
