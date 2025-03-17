'''
@author: 梁卓权 3122004397
@create: 2024-12-30
@last_update: 2025-01-04
@description: 模型文件，存储数据库与ORM的映射关系表结构
@version: 3.0
@process: 
    1.0: 创建文件，创建模型
    2.0: 弃用Double字段，使用Numeric代替
    3.0：发现表结构字段属性名称拼写错误，修复
'''

from flask_sqlalchemy import SQLAlchemy
# 初始化db映射关系
db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'Users'
    UserID = db.Column(db.String(255), primary_key=True, comment='用户id')
    Name = db.Column(db.String(255), nullable=False, comment='昵称')
    Passwd = db.Column(db.String(255), nullable=False, comment='密码')

class Admins(db.Model):
    __tablename__ = 'Admins'
    AdminID = db.Column(db.String(255), primary_key=True, comment='管理员id')
    Name = db.Column(db.String(255), nullable=False, comment='昵称')
    Passwd = db.Column(db.String(255), nullable=False, comment='密码')
    Role = db.Column(db.Enum('ToAdmins', 'ToFlights', 'ToPlanes', 'ToUsers'), nullable=False, comment='角色')


class Planes(db.Model):
    __tablename__ = 'Planes'
    PlaneID = db.Column(db.String(255), primary_key=True, comment='航班id')
    BCnum = db.Column(db.Integer, nullable=False, comment='商务舱座位数量')
    BCprice = db.Column(db.Numeric(precision=7, scale=2), nullable=False, comment='商务舱价格')
    ECnum = db.Column(db.Integer, nullable=False, comment='经济舱座位数量')
    ECprice = db.Column(db.Numeric(precision=7, scale=2), nullable=False, comment='经济舱价格')
    PStatus = db.Column(db.Enum('待命', '飞行中', '维护中'), nullable=False, comment='飞机状态')
    #flights = db.relationship('Flights', backref='plane', lazy=True)

class Flights(db.Model):
    __tablename__ = 'Flights'
    FlightID = db.Column(db.String(255), primary_key=True, comment='航班id')
    PlaneID = db.Column(db.String(255), db.ForeignKey('Planes.PlaneID'), nullable=False, comment='飞机id')
    Origin = db.Column(db.String(255), nullable=False, comment='出发地')
    Destin = db.Column(db.String(255), nullable=False, comment='目的地')
    STime = db.Column(db.String(255), nullable=False, comment='起飞时间')
    PEtime = db.Column(db.String(255), nullable=False, comment='预计到达时间')
    BCfree = db.Column(db.Integer, nullable=False, comment='商务舱座位剩余数')
    ECfree = db.Column(db.Integer, nullable=False, comment='经济舱座位剩余数')
    FStatus = db.Column(db.Enum('待起飞', '飞行中', '已取消', '已延误', '已完成'), nullable=False, comment='航班状态')

class Orders(db.Model):
    __tablename__ = 'Orders'
    OrderID = db.Column(db.String(255), primary_key=True, comment='订单id')
    UserID = db.Column(db.String(255), db.ForeignKey('Users.UserID'), nullable=False, comment='用户id')
    FlightID= db.Column(db.String(255), db.ForeignKey('Flights.FlightID'), nullable=False, comment='航班id')
    Accom = db.Column(db.Enum('经济舱', '商务舱'), nullable=False, comment='舱位品类')
    OrderNum = db.Column(db.Integer, nullable=False, comment='订单数量')
    OrderPrice = db.Column(db.Numeric(precision=7, scale=2), nullable=False, comment='订单总价')
    OStatus = db.Column(db.Enum('待支付', '已支付', '已取消'), nullable=False, comment='订单状态')