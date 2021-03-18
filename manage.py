import sys
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db #, socketio
from app.models import *

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)

def initdb():
	"初始化数据库"
	db.drop_all()
	db.create_all()
	a = User(username='aa')
	db.session.add(a)
	db.session.commit()
	ai = UserInfo(email="testa@test.com", name='zhang', phone='+86-18866667777', address="daheishan", user_id=a.id)
	db.session.add(ai)
	db.session.commit()
	si = StoreInfo(name='teststore', address='daheishanjiao', contact="zhangsan", phone="+86-18766665555", user_id=a.id)
	db.session.add(si)
	db.session.commit()
	fi = FactoryInfo(name='良心工厂', address='大黑山顶', contact='李四', phone='+86-18711112222', complaint_department="12319", complaint_method="请拨打12319", user_id=a.id)
	db.session.add(fi)
	db.session.commit()

	pa = Product(name='卫龙辣条', version="?", description="好吃", comment="备注", factory_id=fi.id)
	pb = Product(name="波士顿红茶", version='1.0', description="好喝", comment="暂无", factory_id=fi.id)
	db.session.add(pa)
	db.session.add(pb)
	db.session.commit()
	
	import datetime
	o = Order(money=998, deadline=datetime.datetime.utcnow())
	db.session.add(o)
	db.session.commit()


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

manager.add_command('run', Server(host='0.0.0.0', port=88, threaded=True))
# manager.add_command('runserver', SocketioServer(host='0.0.0.0', port=80))
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)  # 转移数据库用

if __name__ == '__main__':
    manager.run()
