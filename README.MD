# 大商电器代理服务平台系统

## TODO

## NOTE
删除docker日志 `cat /dev/null > /var/lib/docker/container/<container_id>/<container_id>-json.log`

用qq邮箱发邮件需要修改flask-mail中的源代码
加上 `host.ehlo()` 在`host.login`之前

## 开发环境搭建
操作系统: Ubuntu  
编程语言: python3  

### 下载代码
`git clone https://github.com/KnaveM/elec`  下载源代码

### python设置
`pip3 install -r env/environment.txt`  安装需要的库  
`pip3 freeze > env/environment.txt`  保存需要的库

### shell环境变量
待定

### 数据库
待定

### 启动服务器
`sudo ./manager.py run

## 需求
- 用户模块
- 订单管理模块
- 邮件模块
- 任务管理模块
- 厂商和商品管理模块
- 数据库设计
- 系统设计

## 测试
### 环境搭建测试
环境搭建测试在test文件夹, tests/test1.py  
运行`sudo python3 test1.py`, 打开对应网址