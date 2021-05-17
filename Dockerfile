FROM python:3.6
WORKDIR /Project/demo

COPY env/requirements.txt ./
RUN pip install -r requirements.txt

# 已改为volume 省的每次修改文件都需要重新构建镜像
# COPY . .

# EXPOSE 80 # EXPOSE 只有在启动时使用-P参数时有用

# 设置flask环境变量 好像不需要了 只能在生成镜像时设置
# ENV FLASK_APP manage.py

# gunicorn.conf.py中进行配置
CMD ["gunicorn", "manage:app", "--log-level=debug", "-c", "./gunicorn.conf.py"]

# gunicorn -b 0.0.0.0:88 --log-level=debug -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 manage:app

# 构建镜像 只在最后测试的时候重新构建 其他情况直接bash添加
# docker build -t 'testflask' .
# 创建容器
# docker run -d -p 80:80 -p 3306:3306 -v $(pwd)/:/Project/demo --name=flask -e MAIL_USERNAME=1105711978@qq.com -e MAIL_PASSWORD=shomufxjhbtpjbeg  testflask
# 需要手动设置一下邮箱的环境变量

# 创建数据库容器 每次重构flask都需要重构mysql
# docker pull mysql
# docker run --net container:flask --name mysql -e MYSQL_ROOT_PASSWORD=123456 -d --restart=always mysql

# 创建数据库 配置数据库
# docker exec -it mysql mysql -uroot -p
# ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY '123456';
# flush privileges;
# create database elec;

# 初始化数据库
# docker exec -it flask python -c "import manage; manage.initdb()"

# 使用volume映射
# 启动容器时可设置环境变量 -e DATABASE_URL=""

# 命令行控制应用
# docker exec -it flask python manage.py shell

# 清除docker logs
# cat /dev/null > /var/lib/docker/containers/