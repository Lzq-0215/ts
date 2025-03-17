'''
@author: 梁卓权 3122004397
@create: 2024-12-30
@last_update: 2025-01-03
@description: 主文件，创建app并绑定静态目录读取静态信息
@version: 6.0
@process: 
    1.0: 创建文件，创建app
    2.0: 绑定数据库，实现基本交互
    3.0：修改数据库连接，修改成类并且独立成env文件
    4.0：创建路由，链接本地静态资源，实现网页跳转
    5.0：完善路由信息
    6.0：将路由信息独立成views文件，注册蓝图，绑定app
'''
from flask import Flask
from env import Config
from models import db
from views import views

# 创建app并绑定静态目录读取静态信息
app = Flask(__name__, template_folder="./templates")
# 配置app连接数据库
app.config.from_object(Config)
# 配置app映射ORM表结构
db.init_app(app)
# 注册蓝图
app.register_blueprint(views)


if __name__ == '__main__':
    app.run(port=5000)
