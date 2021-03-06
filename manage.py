import sys
import os
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db, mail #, socketio
from app.models import *

app = create_app(os.getenv("FLASK_CONFIG") or "default")
manager = Manager(app)
migrate = Migrate(app, db)

def initdb():
    "初始化数据库"
    with app.app_context():
        db.drop_all()
        db.create_all()
        u = User(username="test", password="testtest", email="testa@test.com", name='张伟', phone='+86-18866667777', address="北京市朝阳区人民公园")
        db.session.commit()
        

        si = StoreInfo(u, name='我的小店1', address='北京市朝阳区人民公园',
                        contact="张伟", phone="+86-18866667777")
        db.session.add(si)
        db.session.commit()
        # fi = FactoryInfo(u, name=u.username, address='testaddress', contact='lisi', phone='19711112222', complaint_department='department', complaint_method='method')
        # db.session.add(fi)
        # db.session.commit()
        fi = u.factory
        p1 = Product(fi, name="容声（Ronshen）592升对开门冰箱双开门大容量 变频风冷无霜 一级能效 智能节能BCD-592WD16HPA", price=3299, subtitle="【8日0-1点仅3199，0点限型号前30送500卡仅2699】长效除菌净味！一级能效全时双驱变频 AIF+离子净味 时尚墨韵灰面板 WIFI智控  说换就换赢钜惠，戳链接看店铺内更多好物！", specification_json=[['包装清单', '电冰箱x1、冷冻室搁架x4、冷冻室上抽屉x1、冷冻室下抽屉x1、冷冻室层架x4、冷藏室搁架x4、冷藏室上抽屉x1、冷藏室下抽屉x1、冷藏室层架x4、使用说明书x1'], ['主体参数'], ['品牌', '容声(Ronshen)']])
        p2 = Product(fi, name="格力（GREE）1.5匹新能效变频挂机空调KFR-35GW/NhAe1BG 一级能效冷暖家用云恬省电", price=3199, subtitle="【格力4月开门红！4.2日券后价2999！立即抢购！】新一级能效，节能省电挚选，双导风板，运动送风体感更舒适，56℃净菌自洁搭配出风口可拆洗  新一级能效挂机低至2799！立即抢购!", specification_json=[["包装清单", "室内机x1、说明书x2、保温管x1、7号电池x2、密封胶泥x1、螺钉附件x1、膨胀管附件x1、室外机x1、排水接头x1、连接管部件x1、包扎带x1"]])
        p3 = Product(fi, name="海尔(Haier) 65英寸 4K超高清 人工智能语音 2+16G高配内存 LU65C51智能液晶平板电视", price=2699, subtitle="【开门红钜惠！今日仅2899元！购机就送大礼包！】2G+16G、语音遥控、4K HDR  海尔电视爆款钜惠 惊喜不断 立即抢购超值大礼包", specification_json=[["包装清单", "液晶电视机x1、遥控器x1、底座x2、使用说明书x1、螺钉x4"]])
        p4 = Product(fi, name="苏宁极物小Biu智能扫地机 扫地机器人家用静音大吸力全自动吸尘器V6", price=1024, subtitle="视觉导航陀螺仪双导航 断点续扫 1800Pa大吸力 彩屏监控 自动回充 支持安卓系统", specification_json=[["包装清单", "主机x1、说明书x1、保修卡x1"]])

        # MARK: test2 user
        u2 = User(username="test2", password="testtest", email="test2@test.com", name='李磊', phone='+86-18822223333', address="辽宁省沈阳市浑南转运中心")
        db.session.commit()
        s2 = StoreInfo(u2, name='小米扫地机器人旗舰店', address='辽宁省沈阳市万达广场4号铺',
                        contact="李磊", phone="18766665555")
        db.session.add(s2)
        f2 = u2.factory
        p5 = Product(f2, name="小米米家扫地机器人G1智能家用全自动扫拖一体机2200PA大吸力 电控水箱 悬浮吸口 MJSTG1 白", subtitle="【限时到手价仅899元！抢完即止！】三重过滤系统 智能线路规划 智能联动+AI语音操控 红外碰撞减速  领券立减5元", price=899, specification_json=[["包装清单", "主机x1、充电座x1、适配器x1、拖布托班x1、拖布x1、清洁刷x1、说明书x1	"], ["主体"], ["品牌", "	小米(mi)"], ['生活小家电类型', "扫拖一体机器人"], ['功能'], ['清扫模式', "扫吸式"], ['控制方式', '微电脑式']])
        p6 = Product(f2, name="小米米家扫地机器人智能家用全自动扫拖一体机激光导航 2100Pa大吸力 米家APP互联 白色", subtitle="【限时到手价仅1599元！抢完即止！】三种扫地模式 模拟人工拖地 米家APP远程操控 智能电控水箱 LDS激光导航 专业拖地路径  领券立减5元", price=1599, specification_json=[["包装清单", "米家扫拖机器人白色款x1"], ["主体"], ["品牌", "小米(mi)"], ["生活小家电类型", "扫拖一体机器人"]])
        p7 = Product(f2, name="米家 小米扫地机器人扫拖一体 拖地机 吸尘器家用 激光导航 2100Pa大吸力 米家APP互联 黑色", subtitle="【限时到手价仅1599元！抢完即止！】三种扫地模式 模拟人工拖地 米家APP远程操控 智能电控水箱 LDS激光导航 专业拖地路径  领券立减5元", price=1599, specification_json=[["包装清单", "米家扫拖机器人白色款x1"], ["主体"], ["品牌", "小米(mi)"], ["生活小家电类型", "扫拖一体机器人"], ['型号', 'STYTJ02YM']])
        p8 = Product(f2, name='小米米家扫地机器人1S家用全自动无线智能吸尘器视觉激光导航吸尘 毛发防缠绕 米家APP互联', subtitle='【限时到手价仅1599元！抢完即止！】2000Pa大吸力 AI图像区分 智能路径规划 自动回充 断点续扫  领券立减5元', price=1599, specification_json=[["包装清单", "	扫地机x1"], ["主体"], ["品牌", "小米(mi)"], ["生活小家电类型", "扫拖一体机器人"], ['型号', '1S']])

        # test code
        u = User.query.first()
        ps = Product.query.all()
        [u.add_to_cart(p) for p in ps]
        db.session.add(u)
        db.session.commit()

def test_mail():
    from flask_mail import Message
    message = Message(subject = 'title', recipients=['1105711978@qq.com'], body="message")
    mail.send(message)

def make_shell_context():
    return dict(app=app, db=db, User=User, initdb=initdb, mail=mail, test_mail=test_mail)


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

if __name__ != '__main__':
    # 如果不是直接运行，则将日志输出到 gunicorn 中
    from logging.config import dictConfig, fileConfig
    import logging
    import os
    
    # 现在的情况是 gunicorn有一个logger app也有一个logger
    # gunicorn的log输出到error.log中 app的log输出到终端+access.log
    # dictConfig(LOGGING)
    fileConfig('./log/logging.conf', disable_existing_loggers=False)
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    manager.run()
