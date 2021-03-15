#!/root/anaconda3/envs/elec/bin/python
import sys
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db #, socketio
# from app.models import Role, User, Game, Player, Match, AI, MatchPlayer


app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db)


# TODO: 启动socketio
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

manager.add_command('run', Server(host='0.0.0.0', port=80))
# manager.add_command('runserver', SocketioServer(host='0.0.0.0', port=80))
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)  # 转移数据库用

if __name__ == '__main__':
    manager.run()
