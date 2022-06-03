from flask import Flask
import pymysql
from flask_sqlalchemy import SQLAlchemy
import config
from flask import render_template, request, redirect, flash, url_for, session
import random
import traceback
import datetime
from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField, PasswordField
# from wtforms.validators import DataRequired, Length, Email
app = Flask(__name__)
app.config['SECRET_KEY'] = 'very hard to guess string'
#app.config.from_object(config)
#db = SQLAlchemy(app)
db = pymysql.connect(host='localhost',
                     user='root',
                     password='123456',
                     database='database3_test')
cur = db.cursor()


#? http://oatthegoat.co.nz/intl.html
# !// 登录注册界面还未修改  还有主页面设计 over
#todo 登录界面 已加入身份判断
@app.route('/', methods=['GET', 'POST'])
def Sign_in():
    if request.method == 'POST':
        # post="post1"
        Cno = request.form.get("Cno")
        Cpsword = request.form.get("Cpsword")
        sqlQuery = " select Cpsword from Customer where Cno = %s"
        #values=(Aname,Apsword).
        Cpsword2 = ''
        if Cpsword == 'admin' and Cno == '111111':
            flash("管理员登录成功")
            session['xq'] = Cno  #*全局变量  用于判断是否是管理员登录
            return redirect(url_for('Admin_Interface'))
        try:
            cur.execute(sqlQuery, Cno)
            #*判断登录条件
            Cpsword2 = cur.fetchone()
            db.commit()
        except pymysql.Error as e:
            db.rollback()
        #?// 如果该客户输入的编号不存在怎么办？ 已解决
        if Cpsword2 == None:
            flash("客户编号有误（该客户不存在）")
            return render_template('index.html')
        if str(Cpsword2[0]) == Cpsword:
            session["xq"] = Cno  #*用于判断客户编号
            flash("登录成功")
            return redirect(url_for('Main_Interface'))
        else:
            flash("登陆失败")
            return render_template('index.html')
    else:
        return render_template('index.html')


#todo 注册界面
#*也做了条件判定 符合条件才能注册
@app.route('/register', methods=['GET', 'POST'])
def Register():
    if request.method == 'POST':
        # post="post1"
        Cname = request.form.get("Cname")
        Csex = request.form.get("Csex")
        Cphone = request.form.get("Cphone")
        Cid = request.form.get("Cid")
        Cpsword = request.form.get("Cpsword")
        sqlinsert = " INSERT INTO Customer (Cname,Csex,Cphone,Cid,Cpsword) VALUE (%s,%s,%s,%s,%s) "
        values = (Cname, Csex, Cphone, Cid, Cpsword)
        try:
            cur.execute(sqlinsert, values)
            db.commit()
            sqlquery = "select Cno from Customer where Cid=%s"
            try:
                cur.execute(sqlquery, values[3])
                Cno = cur.fetchone()
                db.commit()
                flash("成功获取客户编号(账号)")
                return render_template("CustomerCno.html", Cno=str(Cno[0]))
            except pymysql.Error as e:
                # print("数据查询失败："+e )
                flash("获取失败")
                db.rollback()
                # return render_template('index.html')
                return redirect('/')
        except pymysql.Error as e:
            db.rollback()
            flash("注册失败")  #todo 增加一堆提示信息使得软件更加的人性化
            if Csex != '男' and Csex != '女':
                flash("性别填写错误(请填写正确的性别)")
            if len(Cphone) != 11:
                flash("电话号码不为11位(请输入正确电话号码)")
            if len(Cid) != 18:
                flash("身份证号码不为18位(请输入正确的电话号码)")
            # return render_template('index.html')
            return redirect("/")
        # return render_template('index.html')
        return redirect("/")
    else:
        # return render_template('index.html')
        return redirect("/")


#todo 查询房源plus
@app.route('/house', methods=['GET', 'POST'])
def lookhouse():
    #?//怎么才能算访问空值 已解决
    cno = session['xq']
    sqlquery = 'select * from House where Cno is %s or Cno = %s' % (
        'NULL', cno)  ### ?访问空值代码
    adminsql = 'select * from House'
    try:
        if cno == '111111':  #*判断当前操作的用户
            cur.execute(adminsql)
        else:
            cur.execute(sqlquery)
        houses = cur.fetchall()
        flash("查看成功")
    except pymysql.Error as e:
        flash("访问失败")
        db.rollback()
    return render_template('house.html', houses=houses, qcno=cno)


#todo 主界面
@app.route('/main', methods=['GET', 'POST'])
def Main_Interface():
    return render_template('Main_interface.html')


#todo 管理员界面
@app.route('/admin', methods=['GET', 'POST'])
def Admin_Interface():
    return render_template('Admin_interface.html')


#todo 查询当前客户订单或者是管理员查看所有用户订单
@app.route('/order', methods=['GET', 'POST'])
def Query_order():
    sqlquery = 'select * from Porder where Cno=%s'
    sqlqueryadmin = 'select * from Porder'
    qcno = session["xq"]
    try:
        if qcno == '111111':
            cur.execute(sqlqueryadmin)
        else:
            cur.execute(sqlquery, qcno)
        orders = cur.fetchall()
        print("数据查询成功")
    except pymysql.Error as e:
        print("数据查询失败：" + e)
        db.rollback()
    return render_template('order.html', orders=orders,
                           qcno=qcno)  #*多传入的这个qcno参数是用来判断是否是管理员账号的返回主页是需要用


#todo 买房子
#?可能会优化一下button 和背景?
@app.route("/purchase/<Hno>", methods=['GET', 'POST'])
def Buy_house(Hno):
    sqlinsert = "insert into Porder (Hno,Cno,Time) values (%s,%s,%s)"
    d = datetime.datetime.now()  ###?获取当前时间
    d = d.date()
    try:
        values = (Hno, session['xq'], str(d))
        cur.execute(sqlinsert, values)
        db.commit()
        print("数据插入成功")
    except pymysql.Error as e:
        print("数据查询失败：" + e)
        db.rollback()
    return render_template('buy_success.html')


#todo 查看当前客户预约或者管理员查看全部预约信息
@app.route("/reservation", methods=['GET', 'POST'])
def Reservation():
    sqlquery = 'select * from Browse where Cno=%s'
    sqlqueryadmin = 'select * from Browse'
    qcno = session['xq']
    try:
        if session['xq'] == '111111':
            cur.execute(sqlqueryadmin)
        else:
            cur.execute(sqlquery, session['xq'])
        books = cur.fetchall()
    except pymysql.Error as e:
        print("数据查询失败：" + e)
        db.rollback()
    return render_template('Reservation.html', Books=books, qcno=qcno)  #同上


#todo 预约看房
#*可能会优化一下
@app.route("/appointment/<Hno>", methods=['GET', 'POST'])
def Appointment(Hno):
    sqlinsert = "insert into Browse (Cno,Hno,Viewtime) values (%s,%s,%s)"
    d = datetime.datetime.now()
    d = d.date()
    try:
        values = (session['xq'], Hno, str(d))
        cur.execute(sqlinsert, values)
        db.commit()
        print("数据插入成功")
    except pymysql.Error as e:
        print("数据查询失败：" + e)
        db.rollback()
    return render_template('appointment_success.html')


#todo 管理员添加房子
#*可能会优化一下
@app.route("/admin/addhouse", methods=['GET', 'POST'])
def admin_add_house():
    if request.method == 'POST':
        Hunit = request.form.get("Hunit")
        Hfloor = request.form.get("Hfloor")
        #Hfloor=int(Hfloor)
        Htype = request.form.get("Htype")
        HUprice = request.form.get("HUprice")
        #HUprice=float(HUprice)
        HTprice = request.form.get("HTprice")
        #HTpirce=float(HTprice)
        Harea = request.form.get("Harea")
        #Harea=float(Harea)
        Hadress = request.form.get("Hadress")
        sqlinsert = " INSERT INTO House (Hunit,Hfloor,Htype,HUprice,HTprice,Harea,Hadress) values(%s,%s,%s,%s,%s,%s,%s) "
        values = (Hunit, Hfloor, Htype, HUprice, HTprice, Harea, Hadress)
        try:
            cur.execute(sqlinsert, values)
            db.commit()
            flash("添加成功")
            return redirect(url_for('Admin_Interface'))
        except pymysql.Error as e:
            print("数据插入失败：" + e)
            db.rollback()
        return render_template('add_house.html')
    else:
        return render_template('add_house.html')


@app.route("/customer", methods=['GET', 'POST'])
#todo 查看用户信息或个人信息
def View_customer():
    sqlquery = 'select * from Customer where Cno=%s'
    sqlqueryadmin = 'select * from Customer'
    qcno = session["xq"]
    try:
        if qcno == '111111':
            cur.execute(sqlqueryadmin)
        else:
            cur.execute(sqlquery, qcno)
        customers = cur.fetchall()
        print("数据查询成功")
    except pymysql.Error as e:
        print("数据查询失败：" + e)
        db.rollback()
    return render_template('customer.html', customers=customers, qcno=qcno)


if __name__ == '__main__':
    app.run(debug=True)
