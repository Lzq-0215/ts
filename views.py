'''
@author: 梁卓权 3122004397
@create: 2025-01-01
@last_update: 2025-01-05
@description: 视图文件，实现网页跳转，实现功能
@version: 11.0
@process: 
    1.0: 创建文件，将原app中路由信息转移至本文件
    2.0: 实现航班管理
    3.0: 实现飞机管理
    4.0: 实现管理员管理
    5.0: 实现订单管理
    6.0: 修复路由混乱问题
    7.0: 按网页顺序，排列路由函数的顺序
    8.0: 修改一些已知bug
    9.0: 新增航班检索功能
    10.0: 新增订单检索功能
    11.0: 修改一些已知bug

'''
from flask import Blueprint, render_template, url_for, request, redirect, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError 
from sqlalchemy import desc
from models import db, Users, Admins, Flights, Planes, Orders
import uuid

views = Blueprint('views', __name__)


@views.route('/', methods=['POST', 'GET'])
def login():
    '''
    实现登录功能，将登录信息存储在session中
    '''
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        try:
            user = Users.query.filter(Users.UserID == user_id, Users.Passwd == password).first()
            admin = Admins.query.filter(Admins.AdminID == user_id, Admins.Passwd == password).first()
            if user:
                session['user_id'] = user.UserID
                return redirect(url_for('views.user_index'))
            elif admin:
                session['admin_id'] = admin.AdminID
                session['role'] = admin.Role
                return redirect(url_for('views.admin_index'))
            else:
                message = '账号不存在'
                return render_template('login.html', title="航空管理系统", **locals())
        except SQLAlchemyError as e:
            message = f'错误信息：{str(e)}', 'error'

    return render_template('login.html', title="航空管理系统")


@views.route('/register', methods=['GET', 'POST'])
def register():
    '''
    实现注册功能，将注册信息传递到数据库中
    '''
    if request.method == 'POST':
        register_id = request.form.get('register_id')
        password = request.form.get('password')
        try:
            user = Users.query.filter(Users.UserID == register_id).all()
            if user:
                message = "账号已被注册"
            else:
                new_user = Users(
                    UserID = register_id,
                    Name = register_id,
                    Passwd = password,
                )
                try:
                    db.session.add(new_user)
                    db.session.commit()
                    message = "注册成功，请返回登录界面登录"
                except SQLAlchemyError as e:
                    db.session.rollback()
                    message = f'Error：{str(e)}'
                
        except SQLAlchemyError as e:
            message = f'Error：{str(e)}'

    return render_template("register.html", title="用户注册", **locals())

###################################################################################################


@views.route('/user_index', methods=['GET'])
def user_index():
    '''
    实现用户主界面，实现航班检索功能
    用户一进入主界面，会显示所有待起飞的航班
    '''
    try:
        # 获取搜索参数
        origin = request.args.get('origin')
        destin = request.args.get('destin')
        
        # 构建查询
        query = Flights.query.filter(Flights.FStatus == '待起飞')
        
        if origin:
            query = query.filter(Flights.Origin.like(f'%{origin}%'))
        if destin:
            query = query.filter(Flights.Destin.like(f'%{destin}%'))
            
        # 获取航班列表并按起飞时间排序
        flights = query.order_by(Flights.STime).all()
        
    except SQLAlchemyError as e:
        message = f'错误信息：{str(e)}'

    return render_template('user_index.html', title="用户主界面", **locals())


@views.route('/user_index/book_flight', methods=['POST'])
def book_flight():
    '''
    拿到用户预订信息，将预订信息传递到数据库中
    实现预订功能
    '''
    try:
        data = request.get_json()
        print("收到的预订数据:", data)  # 调试信息
        
        '''
        登录检测：弃用
        if not session.get('user_id'):
            return jsonify({'success': False, 'message': '请先登录'})
        '''
            
        flight = Flights.query.get(data['flight_id'])
        if not flight:
            return jsonify({'success': False, 'message': '航班不存在'})
        
        # 检查航班状态
        if flight.FStatus != '待起飞':
            return jsonify({'success': False, 'message': '该航班不可预订'})
        
        # 检查余票，检测输入合法性
        try:
            book_num = int(data['num'])
            if book_num <= 0:
                return jsonify({'success': False, 'message': '订票数量必须大于0'})
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': '无效的订票数量'})
            
        if data['class_type'] == '商务舱':
            if book_num > flight.BCfree:
                return jsonify({'success': False, 'message': f'商务舱余票不足，当前余票: {flight.BCfree}'})
            flight.BCfree -= book_num
            try:
                plane = Planes.query.get(flight.PlaneID)
                if not plane:
                    return jsonify({'success': False, 'message': '航班信息不完整'})
                price = float(plane.BCprice)
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': '票价信息错误'})
        else:  # 经济舱
            if book_num > flight.ECfree:
                return jsonify({'success': False, 'message': f'经济舱余票不足，当前余票: {flight.ECfree}'})
            flight.ECfree -= book_num
            try:
                plane = Planes.query.get(flight.PlaneID)
                if not plane:
                    return jsonify({'success': False, 'message': '航班信息不完整'})
                price = float(plane.ECprice)
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': '票价信息错误'})
        
        # 创建订单
        order = Orders(
            OrderID = str(uuid.uuid4())[:8],  # 生成8位随机订单号
            UserID = session.get('user_id'),
            FlightID = flight.FlightID,
            Accom = data['class_type'],
            OrderNum = book_num,
            OrderPrice = price * book_num,
            OStatus = '待支付'
        )
        # 提交至数据库
        db.session.add(order)
        db.session.commit()
        return jsonify({'success': True, 'message': '预订成功'})
    except SQLAlchemyError as e:
        db.session.rollback()
        print("数据库错误:", str(e))  # 调试信息
        return jsonify({'success': False, 'message': f'数据库错误: {str(e)}'})
    except Exception as e:
        db.session.rollback()
        print("未知错误:", str(e))  # 调试信息
        return jsonify({'success': False, 'message': f'系统错误: {str(e)}'})


@views.route('/user_index/pay_order', methods=['POST'])
def pay_order():
    '''
    个人订单界面可以看到自己的历史订单信息
    并且如果是未支付的可以进行支付确认订单
    确认后就不可以修改
    '''
    try:
        data = request.get_json()
        order = Orders.query.get(data['order_id'])
        if not order:
            return jsonify({'success': False, 'message': '订单不存在'})
        
        if order.OStatus != '待支付':
            return jsonify({'success': False, 'message': '订单状态不正确'})
        
        order.OStatus = '已支付'
        db.session.commit()
        return jsonify({'success': True})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@views.route('/user_index/cancel_order', methods=['POST'])
def cancel_order():
    '''
    个人订单界面可以看到自己的历史订单信息
    并且如果是未支付的可以进行取消订单
    取消后不可以修改
    '''
    try:
        data = request.get_json()
        order = Orders.query.get(data['order_id'])
        if not order:
            return jsonify({'success': False, 'message': '订单不存在'})
        
        if order.OStatus == '已支付':
            return jsonify({'success': False, 'message': '已支付的订单不能取消'})
        
        # 恢复航班余票
        flight = Flights.query.get(order.FlightID)
        if flight:
            if order.Accom == '商务舱':
                flight.BCfree += order.OrderNum
            else:
                flight.ECfree += order.OrderNum
        
        order.OStatus = '已取消'
        db.session.commit()
        return jsonify({'success': True})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@views.route('/user_index/private_order', methods=['GET'])
def private_order():
    '''
    个人订单界面可以看到自己的历史订单信息
    '''
    try:
        orders = Orders.query.filter(Orders.UserID == session.get('user_id')).all()
    except SQLAlchemyError as e:
        message = f'错误信息：{str(e)}'

    return render_template('private_order.html', title="订单管理", **locals())



##############################################################################################

@views.route('/admin_index', methods=['GET'])
def admin_index():
    '''
    管理员主界面，可以查看所有用户信息
    '''
    try:
        users = Users.query.all()
    except SQLAlchemyError as e:
        message = f'错误信息：{str(e)}'

    return render_template('admin_index.html', title="管理员主界面", **locals())


@views.route('/admin_index/edit_user', methods=['POST'])
def edit_user():
    '''
    修改用户信息
    '''
    try:
        data = request.get_json()
        user = Users.query.get(data['user_id'])
        if user:
            user.Name = data['name']
            user.Passwd = data['passwd']
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '用户不存在'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@views.route('/admin_index/delete_user', methods=['POST'])
def delete_user():
    '''
    删除用户信息
    '''
    try:
        data = request.get_json()
        user = Users.query.get(data['user_id'])
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '用户不存在'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
    



@views.route('/admin_index/admin_manage', methods=['GET'])
def admin_manage():
    '''
    管理员管理界面，可以查看所有管理员信息
    '''
    try:
        admins = Admins.query.all()
    except SQLAlchemyError as e:
        message = f'错误信息：{str(e)}'

    return render_template('admin_manage.html', title="管理员管理", **locals())


@views.route('/admin_index/add_flight', methods=['POST'])
def add_flight():
    '''
    添加航班信息
    飞机必须要待命状态，且座位设置要合理
    '''
    try:
        data = request.get_json()
        # 检查航班是否已存在
        flight = Flights.query.get(data['flight_id'])
        if flight:
            return jsonify({'success': False, 'message': '航班号已存在'})
        
        # 检查飞机是否存在且可用
        plane = Planes.query.get(data['plane_id'])
        if not plane:
            return jsonify({'success': False, 'message': '指定的飞机不存在'})
        if plane.PStatus != '待命':
            return jsonify({'success': False, 'message': '指定的飞机不可用'})
            
        # 检查座位数是否合理
        if int(data['bc_free']) > plane.BCnum:
            return jsonify({'success': False, 'message': '商务舱座位数超过飞机容量'})
        if int(data['ec_free']) > plane.ECnum:
            return jsonify({'success': False, 'message': '经济舱座位数超过飞机容量'})
        
        # 创建新航班
        new_flight = Flights(
            FlightID = data['flight_id'],
            PlaneID = data['plane_id'],
            Origin = data['origin'],
            Destin = data['destin'],
            STime = data['s_time'],
            PEtime = data['pe_time'],
            BCfree = data['bc_free'],
            ECfree = data['ec_free'],
            FStatus = data['f_status']
        )
        # 提交至数据库
        db.session.add(new_flight)
        db.session.commit()
        return jsonify({'success': True})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
    
@views.route('/admin_index/delete_flight', methods=['POST'])
def delete_flight():
    '''
    删除航班信息
    先查询下来，然后再删除
    '''
    try:
        data = request.get_json()
        flight = Flights.query.get(data['flight_id'])
        if flight:
            # 检查是否有关联的订单
            orders = Orders.query.filter_by(FlightID=flight.FlightID).all()
            if orders:
                return jsonify({'success': False, 'message': '该航班存在关联订单，无法删除'})
            db.session.delete(flight)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '航班不存在'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
    
@views.route('/admin_index/edit_flight', methods=['POST'])
def edit_flight():
    '''
    修改航班信息
    先查询下来，然后再修改
    '''
    try:
        data = request.get_json()
        flight = Flights.query.get(data['flight_id'])
        if flight:
            flight.PlaneID = data['plane_id']
            flight.Origin = data['origin']
            flight.Destin = data['destin']
            flight.STime = data['s_time']
            flight.PEtime = data['pe_time']
            flight.BCfree = data['bc_free']
            flight.ECfree = data['ec_free']
            flight.FStatus = data['f_status']
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '航班不存在'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
    

@views.route('/admin_index/flight_manage', methods=['GET'])
def flight_manage():
    '''
    航班管理界面，可以查看所有航班信息
    '''
    try:
        # 获取搜索参数
        origin = request.args.get('origin')
        destin = request.args.get('destin')
        
        # 构建查询
        query = Flights.query
        
        if origin:
            query = query.filter(Flights.Origin.like(f'%{origin}%'))
        if destin:
            query = query.filter(Flights.Destin.like(f'%{destin}%'))
            
        # 获取航班列表
        flights = query.all()
        
    except SQLAlchemyError as e:
        message = f'错误信息：{str(e)}'

    return render_template('flight_manage.html', title="航班管理", **locals())

##################################################################################


@views.route('/admin_index/add_plane', methods=['POST'])
def add_plane():
    '''
    添加飞机信息
    飞机必须有飞机号，且飞机号不能重复
    '''
    try:
        data = request.get_json()
        # 检查飞机是否已存在
        plane = Planes.query.get(data['plane_id'])
        if plane:
            return jsonify({'success': False, 'message': '飞机号已存在'})
        
        # 创建新飞机
        new_plane = Planes(
            PlaneID = data['plane_id'],
            BCnum = data['bc_num'],
            BCprice = data['bc_price'],
            ECnum = data['ec_num'],
            ECprice = data['ec_price'],
            PStatus = data['p_status']
        )
        
        db.session.add(new_plane)
        db.session.commit()
        return jsonify({'success': True})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@views.route('/admin_index/delete_plane', methods=['POST'])
def delete_plane(): 
    '''
    删除飞机信息
    先查询下来，然后再删除
    '''
    try:
        data = request.get_json()
        plane = Planes.query.get(data['plane_id'])
        if plane:
            # 检查是否有关联的航班
            flights = Flights.query.filter_by(PlaneID=plane.PlaneID).all()
            if flights:
                return jsonify({'success': False, 'message': '该飞机存在关联航班，无法删除'})
            db.session.delete(plane)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '飞机不存在'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@views.route('/admin_index/edit_plane', methods=['POST'])
def edit_plane():
    '''
    修改飞机信息
    先查询下来，然后再修改，修改后提交
    '''
    try:
        data = request.get_json()
        plane = Planes.query.get(data['plane_id'])
        if plane:
            plane.BCnum = data['bc_num']
            plane.BCprice = data['bc_price']
            plane.ECnum = data['ec_num']
            plane.ECprice = data['ec_price']
            plane.PStatus = data['p_status']
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '飞机不存在'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})
    

@views.route('/admin_index/plane_manage', methods=['GET'])
def plane_manage():
    '''
    飞机管理界面，可以查看所有飞机信息
    '''
    try:
        planes = Planes.query.all()
    except SQLAlchemyError as e:
        message = f'错误信息：{str(e)}'

    return render_template('plane_manage.html', title="飞机管理", **locals())

##################################################################################

@views.route('/admin_index/add_admin', methods=['POST'])
def add_admin():
    '''
    添加管理员信息
    管理员必须有管理员号，且管理员号不能重复
    '''
    try:
        data = request.get_json()
        # 检查管理员是否已存在
        admin = Admins.query.get(data['admin_id'])
        if admin:
            return jsonify({'success': False, 'message': '管理员ID已存在'})
        
        # 创建新管理员
        new_admin = Admins(
            AdminID = data['admin_id'],
            Name = data['name'],
            Passwd = data['passwd'],
            Role = data['role']
        )
        
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({'success': True})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})



@views.route('/admin_index/edit_admin', methods=['POST'])
def edit_admin():
    '''
    修改管理员信息
    先查询下来，然后再修改
    '''
    try:
        data = request.get_json()
        admin = Admins.query.get(data['admin_id'])
        if admin:
            admin.Name = data['name']
            admin.Passwd = data['passwd']
            admin.Role = data['role']
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '管理员不存在'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@views.route('/admin_index/delete_admin', methods=['POST'])
def delete_admin():
    '''
    删除管理员信息
    先查询下来，然后再删除
    '''
    try:
        data = request.get_json()
        admin = Admins.query.get(data['admin_id'])
        if admin:
            # 检查是否是最后一个管理员
            admin_count = Admins.query.count()
            if admin_count <= 1:
                return jsonify({'success': False, 'message': '系统至少需要保留一个管理员'})
            db.session.delete(admin)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '管理员不存在'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@views.route('/admin_index/order_manage', methods=['GET'])
def order_manage():
    '''
    订单管理界面，可以查看所有订单信息
    可以通过用户ID和航班ID进行检索
    '''
    # 获取搜索参数
    user_id = request.args.get('user_id')
    flight_id = request.args.get('flight_id')
    
    # 构建查询
    query = Orders.query
    
    if user_id:
        query = query.filter(Orders.UserID == user_id)
    if flight_id:
        query = query.filter(Orders.FlightID == flight_id)
        
    # 获取订单列表
    orders = query.all()
    
    return render_template('order_manage.html', orders=orders)

@views.route('/admin_index/update_order_status', methods=['POST'])
def update_order_status():
    '''
    修改订单状态
    先查询下来，然后再修改
    '''
    data = request.get_json()
    order_id = data.get('order_id')
    status = data.get('status')
    
    try:
        order = Orders.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': '订单不存在'})
            
        # 更新订单状态
        order.OStatus = status
        
        # 如果取消订单,恢复航班座位
        if status == '已取消':
            flight = Flights.query.get(order.FlightID)
            if flight:
                if order.Accom == '商务舱':
                    flight.BCnum += order.OrderNum
                else:
                    flight.ECnum += order.OrderNum
        
        db.session.commit()
        return jsonify({'success': True, 'message': '状态更新成功'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})




