'''
@author: 梁卓权 3122004397
@create: 2024-12-30
@last_update: 2025-01-2
@description: 环境变量，配置数据库连接
@version: 2.0
@process: 
    1.0: 创建文件，创建配置
    2.0: 修改配置信息，为使用session添加SECRET_KEY
'''
class Config(object):
    # 数据库登录的配置信息
    USERNAME = "root"
    PASSWORD = "****"
    HOST = "localhost"
    PORT = "3306"
    DB = "ManageDB"
    #DB_URI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}"
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}"
    DEBUG=True
    SECRET_KEY= 'my_secret_key'
