"""
@Author : wangxiaopeng
@Date   : 2020-1-13
@Github : github.com/xiaopeng-whu
"""

from tkinter import *
from tkinter.messagebox import *
import pymysql  # 导入 pymysql
from tkinter import ttk


# 每次显示信息时先执行该函数将表已显示内容清空
def delButton(tree):
    x = tree.get_children()
    for item in x:
        tree.delete(item)


def showAllInfo(tree, table):
    delButton(tree)
    db = pymysql.connect(host="localhost", user="root",
                         password="123456", db="school_teacher_information", port=3306)
    cur = db.cursor()
    cur.execute("select * from %s" % table)  # 执行sql语句
    results = cur.fetchall()  # 获取查询的所有记录
    for item in results:
        tree.insert('', "end", values=item)
    cur.close()
    db.close()  # 关闭连接


# 还要考虑只有信息表存在的教职工才能在另外两个表中添加相关的新数据
# 还要在添加基本信息表的信息时对sex项进行检查
def appendInfo(tree, table, list):
    delButton(tree)
    list2 = []  # 存储输入框信息
    for i in range(len(list)):  # 这里我直接规定一条信息的全部数据项均为not null，实际情况可能不是这样，但为了简洁（以及方便），暂时这样规定⑧
        if list[i].get() == '':
            showerror(title='提示', message='输入不能为空')
            return
        else:
            list2.append(list[i].get())
            # list[i].delete(0, END)  # 每次获取到输入框的值后就清空输入框，但执行完这条就无法在findinfo获取输入框信息了，为了findInfo的一致性，暂时无法统一形式，索性先不删去输入

    x = tree.get_children()
    for item in x:
        tree.delete(item)

    db = pymysql.connect(host="localhost", user="root", password="123456", db="school_teacher_information", port=3306)
    cur = db.cursor()

    if table == 'teacher_basic':
        if list2[2] == '男' or list2[2] == '女':
            # 注意values中的%s要加单引号！！！（之前试的时候没有加也成功了，就很奇怪）
            cur.execute("insert into %s values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (table, list2[0], list2[1], list2[2], list2[3], list2[4], list2[5], list2[6], list2[7], list2[8], list2[9]))
        else:
            showinfo(title='提示', message='sex项必须为“男”or“女”！')
            showAllInfo(tree, table)
            return
    elif table == 'teaching':  # 先判断新添加的数据的教职工号是否属于基本信息表中，再选择是否执行插入新数据操作
        if findInfo(0, tree, 'teacher_basic', list):  # 因为我们没有使用到tree，所以这里不一定必须指定为Tree1
            cur.execute("insert into %s values('%s','%s','%s','%s','%s','%s','%s')" % (table, list2[0], list2[1], list2[2], list2[3], list2[4], list2[5], list2[6]))
        else:
            showinfo(title='提示', message='添加信息不在教职工基本信息表中，添加失败！')
            showAllInfo(tree, table)
            return
    else:  # 同样要先进行判断
        if findInfo(0, tree, 'teacher_basic', list):
            cur.execute("insert into %s values('%s','%s','%s','%s','%s','%s')" % (table, list2[0], list2[1], list2[2], list2[3], list2[4], list2[5]))
        else:
            showinfo(title='提示', message='添加信息不在教职工基本信息表中，添加失败！')
            showAllInfo(tree, table)
            return
    db.commit()
    cur.execute("select * from %s" % table)
    results = cur.fetchall()
    for item in results:
        tree.insert('', "end", values=item)

    cur.close()
    db.close()
    showinfo(title='提示', message='插入/更新成功！')



# 在删除第一个表（教职工信息表）数据的时候，也要将其他两个表的数据删除（以tea_no为索引）
# 而删除其他两个表数据时，则不需要删除其他两个表的数据
def deleteInfo(tree, table):
    if not tree.selection():
        showerror(title='提示', message='Sorry ,please choose an item.')
        return
    for item in tree.selection():
        selectedItem = tree.selection()[0]
        no1 = tree.item(selectedItem, 'values')[0]
        cno1 = tree.item(selectedItem, 'values')[2]
        dir1 = tree.item(selectedItem, 'values')[1]
        tree.delete(item)

        db = pymysql.connect(host="localhost", user="root",
                             password="123456", db="school_teacher_information", port=3306)
        cur = db.cursor()
        if table == 'teacher_basic':
            cur.execute("delete from teacher_basic where tea_no = '%s'" % no1)  # 通过输入框的教工号进行查找删除的，而不是选中行
            cur.execute("delete from teaching where tea_no = '%s'" % no1)
            cur.execute("delete from research where tea_no = '%s'" % no1)
        elif table == 'teaching':
            # 这里还有一个bug，删除一个老师的一条信息会把该老师的其他信息都删除，因为是根据tea_no进行delete的！
            cur.execute("delete from teaching where tea_no = '%s' AND cour_no = '%s'" % (no1, cno1))  # 如果不是信息表，则只删除该表信息即可
        else:
            cur.execute("delete from research where tea_no = '%s' AND research_dir = '%s'" % (no1, dir1))

        db.commit()
        cur.close()
        db.close()
        showinfo(title='提示', message='删除成功！')


# 更新也要考虑一个表对其他表的影响
# 这里先进行的delete再进行的append，导致判断发生在append中，使得更新失败仍会删除原数据
def checkexist(table, list):   # 判断输入信息代表教职工是否在基本信息表中
    list2 = []  # 存储输入框信息
    flag = 0  # 作为返回值
    for i in range(len(list)):  # 这里我直接规定一条信息的全部数据项均为not null，实际情况可能不是这样，但为了简洁（以及方便），暂时这样规定⑧
        if list[i].get() == '':
            showerror(title='提示', message='输入不能为空')
            return 0
        else:
            list2.append(list[i].get())

    db = pymysql.connect(host="localhost", user="root", password="123456", db="school_teacher_information", port=3306)
    cur = db.cursor()

    db.commit()
    cur.execute("select * from %s" % table)
    results = cur.fetchall()
    cur.close()
    db.close()

    for item in results:
        if item[0] == list[0].get():
            flag = 1
    if not flag:
        showinfo(title='提示', message='更新信息不在教职工基本信息表中，更新失败！')

    return flag


def updateInfo(tree, table, list):
    if not tree.selection():
        showerror(title='提示', message='Sorry ,please choose an item.')
        return
    elif checkexist('teacher_basic', list):
        for item in tree.selection():
            selectedItem = tree.selection()[0]
            no1 = tree.item(selectedItem, 'values')[0]
            tree.delete(item)

            db = pymysql.connect(host="localhost", user="root",
                                 password="123456", db="school_teacher_information", port=3306)
            cur = db.cursor()
            if table == 'teacher_basic':
                cur.execute("delete from teacher_basic where tea_no = '%s'" % no1)  # 通过输入框的教工号进行查找删除的，而不是选中行
                cur.execute("delete from teaching where tea_no = '%s'" % no1)
                cur.execute("delete from research where tea_no = '%s'" % no1)
            else:
                cur.execute("delete from %s where tea_no = '%s'" % (table, no1))  # 通过输入框的学号进行查找删除的，而不是选中行

            db.commit()
            cur.close()
            db.close()
        appendInfo(tree, table, list)
    else:
        return


# 暂时只按照tea_no查询，后续三个表可以使用if语句进行分支执行不同查询
# 要求实现多种关联查询，因此还要作修改！！！***（/fad）
def findInfo(check, tree, table, list):
    if check:  # check=1表示是要在当前界面查询并显示，check=0表示只是调用一下查询结果
        delButton(tree)  # 在appendInfo中调用时不能执行该语句，需修改
    db = pymysql.connect(host="localhost", user="root",
                         password="123456", db="school_teacher_information", port=3306)
    cur = db.cursor()

    if table == 'multi_table':  # 多表查询
        for i in range(len(list)):
            if list[i].get() == '':
                showerror(title='提示', message='输入不能为空')
                return
        cur.execute("select teacher_basic.tea_no,teacher_basic.tea_name,teacher_basic.sex,teaching.cour_name,research.patent "
                    "from teacher_basic,teaching,research where dept = '%s' AND cour_no = '%s' AND research_dir = '%s'"
                    % (entry_t1.get(), entry_t2.get(), entry_t3.get()))
        entry_t1.delete(0, END)
        entry_t2.delete(0, END)
        entry_t3.delete(0, END)
    else:  # 单表查询（按照tea_no查询）
        cur.execute("select * from %s where tea_no = '%s'" % (table, list[0].get()))  # 执行sql语句
        for i in range(len(list)):
            list[i].delete(0, END)
        # entry_tea_no.delete(0, END)  # 按下查询按钮后输入框清空
    results = cur.fetchall()  # 获取查询的所有记录

    if not len(results):
        if check:
            showinfo(title='提示', message='查询结果为空！')
        flag1 = 0  # 返回查询结果是否为空的标志
    else:
        if check:
            for item in results:
                tree.insert('', "end", values=item)
        flag1 = 1

    db.commit()
    cur.close()
    db.close()  # 关闭连接
    return flag1


def table1():  # 教职工基本信息表（teacher_basic）
    root1 = Tk()
    root1.geometry('950x1000')
    root1.title('教职工基本信息表')
    Label(root1, text='教职工基本信息表', bg='white', fg='red', font=('宋体', 15)).pack(side=TOP, fill='x')

    Label(root1, text="tea_no：").place(relx=0, rely=0.05, relwidth=0.1)
    Label(root1, text="tea_name：").place(relx=0.5, rely=0.05, relwidth=0.1)
    Label(root1, text="sex：").place(relx=0, rely=0.1, relwidth=0.1)
    Label(root1, text="degree：").place(relx=0.5, rely=0.1, relwidth=0.1)
    Label(root1, text="dept：").place(relx=0, rely=0.15, relwidth=0.1)
    Label(root1, text="graduate_sch：").place(relx=0.5, rely=0.15, relwidth=0.1)
    Label(root1, text="health：").place(relx=0, rely=0.2, relwidth=0.1)
    Label(root1, text="title：").place(relx=0.5, rely=0.2, relwidth=0.1)
    Label(root1, text="duty：").place(relx=0, rely=0.25, relwidth=0.1)
    Label(root1, text="award_or_punish：").place(relx=0.5, rely=0.25, relwidth=0.1)

    tea_no = StringVar()
    tea_name = StringVar()
    sex = StringVar()
    degree = StringVar()
    dept = StringVar()
    graduate_sch = StringVar()
    health = StringVar()
    title = StringVar()
    duty = StringVar()
    award_or_punish = StringVar()

    global entry_tea_no
    global entry_tea_name
    global entry_sex
    global entry_degree
    global entry_dept
    global entry_graduate_sch
    global entry_health
    global entry_title
    global entry_duty
    global entry_award_or_punish
    entry_tea_no = Entry(root1, textvariable=tea_no)
    entry_tea_no.place(relx=0.1, rely=0.05, relwidth=0.3, height=25)
    entry_tea_name = Entry(root1, textvariable=tea_name)
    entry_tea_name.place(relx=0.6, rely=0.05, relwidth=0.3, height=25)
    entry_sex = Entry(root1, textvariable=sex)
    entry_sex.place(relx=0.1, rely=0.1, relwidth=0.3, height=25)
    entry_degree = Entry(root1, textvariable=degree)
    entry_degree.place(relx=0.6, rely=0.1, relwidth=0.3, height=25)
    entry_dept = Entry(root1, textvariable=dept)
    entry_dept.place(relx=0.1, rely=0.15, relwidth=0.3, height=25)
    entry_graduate_sch = Entry(root1, textvariable=graduate_sch)
    entry_graduate_sch.place(relx=0.6, rely=0.15, relwidth=0.3, height=25)
    entry_health = Entry(root1, textvariable=health)
    entry_health.place(relx=0.1, rely=0.2, relwidth=0.3, height=25)
    entry_title = Entry(root1, textvariable=title)
    entry_title.place(relx=0.6, rely=0.2, relwidth=0.3, height=25)
    entry_duty = Entry(root1, textvariable=duty)
    entry_duty.place(relx=0.1, rely=0.25, relwidth=0.3, height=25)
    entry_award_or_punish = Entry(root1, textvariable=award_or_punish)
    entry_award_or_punish.place(relx=0.6, rely=0.25, relwidth=0.3, height=25)

    # 将输入框Entry放在一个列表中传入相关操作的函数中，利用get()获得输入值
    list1 = [entry_tea_no, entry_tea_name, entry_sex, entry_degree, entry_dept, entry_graduate_sch, entry_health, entry_title, entry_duty, entry_award_or_punish]

    # global Tree1  # 声明global貌似也不能在其他函数中使用，还是直接当做参数传入函数⑧，但不同table又在不同函数中，也没有相互调用，怎么传Tree1？每次关闭第一个表后Tree1就消失了
    Tree1 = ttk.Treeview(root1, show='headings',
                         column=('tea_no', 'tea_name', 'sex', 'degree', 'dept', 'graduate_sch', 'health', 'title', 'duty', 'award_or_punish'))
    Tree1.column('tea_no', width=100, anchor="center")
    Tree1.column('tea_name', width=100, anchor="center")
    Tree1.column('sex', width=100, anchor="center")
    Tree1.column('degree', width=100, anchor="center")
    Tree1.column('dept', width=100, anchor="center")
    Tree1.column('graduate_sch', width=100, anchor="center")
    Tree1.column('health', width=100, anchor="center")
    Tree1.column('title', width=100, anchor="center")
    Tree1.column('duty', width=100, anchor="center")
    Tree1.column('award_or_punish', width=100, anchor="center")
    # 表格标题设置
    Tree1.heading('tea_no', text='tea_no')
    Tree1.heading('tea_name', text='tea_name')
    Tree1.heading('sex', text='sex')
    Tree1.heading('degree', text='degree')
    Tree1.heading('dept', text='dept')
    Tree1.heading('graduate_sch', text='graduate_sch')
    Tree1.heading('health', text='health')
    Tree1.heading('title', text='title')
    Tree1.heading('duty', text='duty')
    Tree1.heading('award_or_punish', text='award_or_punish')

    Tree1.place(rely=0.4, relwidth=0.99)

    # 使用lambda匿名函数传参
    Button(root1, text="显示所有信息", command=lambda: showAllInfo(tree=Tree1, table='teacher_basic')).place(relx=0.05, rely=0.3, width=100)
    Button(root1, text="追加信息", command=lambda: appendInfo(tree=Tree1, table='teacher_basic', list=list1)).place(relx=0.25, rely=0.3, width=100)
    Button(root1, text="删除信息", command=lambda: deleteInfo(tree=Tree1, table='teacher_basic')).place(relx=0.45, rely=0.3, width=100)
    Button(root1, text="更改信息", command=lambda: updateInfo(tree=Tree1, table='teacher_basic', list=list1)).place(relx=0.65, rely=0.3, width=100)
    Button(root1, text="查找信息（tea_no）", command=lambda: findInfo(check=1, tree=Tree1, table='teacher_basic', list=list1)).place(relx=0.85, rely=0.3, width=120)


def table2():  # 教职工教学信息表（teaching）
    root2 = Tk()
    root2.geometry('950x1000')
    root2.title('教职工教学信息表')
    Label(root2, text='教职工教学信息表', bg='white', fg='red', font=('宋体', 15)).pack(side=TOP, fill='x')

    Label(root2, text="tea_no：").place(relx=0, rely=0.05, relwidth=0.1)
    Label(root2, text="tea_name：").place(relx=0.5, rely=0.05, relwidth=0.1)
    Label(root2, text="cour_no：").place(relx=0, rely=0.1, relwidth=0.1)
    Label(root2, text="cour_name：").place(relx=0.5, rely=0.1, relwidth=0.1)
    Label(root2, text="cour_hour：").place(relx=0, rely=0.15, relwidth=0.1)
    Label(root2, text="credit：").place(relx=0.5, rely=0.15, relwidth=0.1)
    Label(root2, text="cour_type：").place(relx=0, rely=0.2, relwidth=0.1)

    tea_no = StringVar()
    tea_name = StringVar()
    cour_no = StringVar()
    cour_name = StringVar()
    cour_hour = StringVar()
    credit = StringVar()
    cour_type = StringVar()

    global entry_tea_no
    global entry_tea_name
    global entry_cour_no
    global entry_cour_name
    global entry_cour_hour
    global entry_credit
    global entry_cour_type
    entry_tea_no = Entry(root2, textvariable=tea_no)
    entry_tea_no.place(relx=0.1, rely=0.05, relwidth=0.37, height=25)  # 把place单独拿出来就可以？？爷笑了！
    entry_tea_name = Entry(root2, textvariable=tea_name)
    entry_tea_name.place(relx=0.6, rely=0.05, relwidth=0.37, height=25)
    entry_cour_no = Entry(root2, textvariable=cour_no)
    entry_cour_no.place(relx=0.1, rely=0.1, relwidth=0.37, height=25)
    entry_cour_name = Entry(root2, textvariable=cour_name)
    entry_cour_name.place(relx=0.6, rely=0.1, relwidth=0.37, height=25)
    entry_cour_hour = Entry(root2, textvariable=cour_hour)
    entry_cour_hour.place(relx=0.1, rely=0.15, relwidth=0.37, height=25)
    entry_credit = Entry(root2, textvariable=credit)
    entry_credit.place(relx=0.6, rely=0.15, relwidth=0.37, height=25)
    entry_cour_type = Entry(root2, textvariable=cour_type)
    entry_cour_type.place(relx=0.1, rely=0.2, relwidth=0.37, height=25)

    # 将输入框Entry放在一个列表中传入相关操作的函数中，利用get()获得输入值
    list2 = [entry_tea_no, entry_tea_name, entry_cour_no, entry_cour_name, entry_cour_hour, entry_credit, entry_cour_type]

    Tree2 = ttk.Treeview(root2, show='headings',
                         column=('tea_no', 'tea_name', 'cour_no', 'cour_name', 'cour_hour', 'credit', 'cour_type'))
    Tree2.column('tea_no', width=150, anchor="center")
    Tree2.column('tea_name', width=150, anchor="center")
    Tree2.column('cour_no', width=150, anchor="center")
    Tree2.column('cour_name', width=150, anchor="center")
    Tree2.column('cour_hour', width=150, anchor="center")
    Tree2.column('credit', width=150, anchor="center")
    Tree2.column('cour_type', width=150, anchor="center")
    # 表格标题设置
    Tree2.heading('tea_no', text='tea_no')
    Tree2.heading('tea_name', text='tea_name')
    Tree2.heading('cour_no', text='cour_no')
    Tree2.heading('cour_name', text='cour_name')
    Tree2.heading('cour_hour', text='cour_hour')
    Tree2.heading('credit', text='credit')
    Tree2.heading('cour_type', text='cour_type')

    Tree2.place(rely=0.35, relwidth=0.99)

    # 使用lambda匿名函数传参
    Button(root2, text="显示所有信息", command=lambda: showAllInfo(tree=Tree2, table='teaching')).place(relx=0.05, rely=0.25, width=100)
    Button(root2, text="追加信息", command=lambda: appendInfo(tree=Tree2, table='teaching', list=list2)).place(relx=0.25, rely=0.25, width=100)
    Button(root2, text="删除信息", command=lambda: deleteInfo(tree=Tree2, table='teaching')).place(relx=0.45, rely=0.25, width=100)
    Button(root2, text="更改信息", command=lambda: updateInfo(tree=Tree2, table='teaching', list=list2)).place(relx=0.65, rely=0.25, width=100)
    Button(root2, text="查找信息（tea_no）", command=lambda: findInfo(check=1, tree=Tree2, table='teaching', list=list2)).place(relx=0.85, rely=0.25, width=120)


def table3():  # 教职工科研信息表（research）
    root3 = Tk()
    root3.geometry('950x1000')
    root3.title('教职工科研信息表')
    Label(root3, text='教职工科研信息表', bg='white', fg='red', font=('宋体', 15)).pack(side=TOP, fill='x')

    Label(root3, text="tea_no：").place(relx=0, rely=0.05, relwidth=0.1)
    Label(root3, text="research_dir：").place(relx=0.5, rely=0.05, relwidth=0.1)
    Label(root3, text="research_sit：").place(relx=0, rely=0.1, relwidth=0.1)
    Label(root3, text="patent：").place(relx=0.5, rely=0.1, relwidth=0.1)
    Label(root3, text="paper_name：").place(relx=0, rely=0.15, relwidth=0.1)
    Label(root3, text="paper_level：").place(relx=0.5, rely=0.15, relwidth=0.1)

    tea_no = StringVar()
    research_dir = StringVar()
    research_sit = StringVar()
    patent = StringVar()
    paper_name = StringVar()
    paper_level = StringVar()

    global entry_tea_no
    global entry_research_dir
    global entry_research_sit
    global entry_patent
    global entry_paper_name
    global entry_paper_level
    entry_tea_no = Entry(root3, textvariable=tea_no)
    entry_tea_no.place(relx=0.1, rely=0.05, relwidth=0.37, height=25)  # 把place单独拿出来就可以？？爷笑了！
    entry_research_dir = Entry(root3, textvariable=research_dir)
    entry_research_dir.place(relx=0.6, rely=0.05, relwidth=0.37, height=25)
    entry_research_sit = Entry(root3, textvariable=research_sit)
    entry_research_sit.place(relx=0.1, rely=0.1, relwidth=0.37, height=25)
    entry_patent = Entry(root3, textvariable=patent)
    entry_patent.place(relx=0.6, rely=0.1, relwidth=0.37, height=25)
    entry_paper_name = Entry(root3, textvariable=paper_name)
    entry_paper_name.place(relx=0.1, rely=0.15, relwidth=0.37, height=25)
    entry_paper_level = Entry(root3, textvariable=paper_level)
    entry_paper_level.place(relx=0.6, rely=0.15, relwidth=0.37, height=25)

    # 将输入框Entry放在一个列表中传入相关操作的函数中，利用get()获得输入值
    list3 = [entry_tea_no, entry_research_dir, entry_research_sit, entry_patent, entry_paper_name, entry_paper_level]

    Tree3 = ttk.Treeview(root3, show='headings',
                         column=('tea_no', 'research_dir', 'research_sit', 'patent', 'paper_name', 'paper_level'))
    Tree3.column('tea_no', width=150, anchor="center")
    Tree3.column('research_dir', width=150, anchor="center")
    Tree3.column('research_sit', width=150, anchor="center")
    Tree3.column('patent', width=150, anchor="center")
    Tree3.column('paper_name', width=150, anchor="center")
    Tree3.column('paper_level', width=150, anchor="center")
    # 表格标题设置
    Tree3.heading('tea_no', text='tea_no')
    Tree3.heading('research_dir', text='research_dir')
    Tree3.heading('research_sit', text='research_sit')
    Tree3.heading('patent', text='patent')
    Tree3.heading('paper_name', text='paper_name')
    Tree3.heading('paper_level', text='paper_level')

    Tree3.place(rely=0.3, relwidth=0.99)

    # 使用lambda匿名函数传参
    Button(root3, text="显示所有信息", command=lambda: showAllInfo(tree=Tree3, table='research')).place(relx=0.05, rely=0.2, width=100)
    Button(root3, text="追加信息", command=lambda: appendInfo(tree=Tree3, table='research', list=list3)).place(relx=0.25, rely=0.2, width=100)
    Button(root3, text="删除信息", command=lambda: deleteInfo(tree=Tree3, table='research')).place(relx=0.45, rely=0.2, width=100)
    Button(root3, text="更改信息", command=lambda: updateInfo(tree=Tree3, table='research', list=list3)).place(relx=0.65, rely=0.2, width=100)
    Button(root3, text="查找信息（tea_no）", command=lambda: findInfo(check=1, tree=Tree3, table='research', list=list3)).place(relx=0.85, rely=0.2, width=120)


def table4():
    root4 = Tk()
    root4.geometry('950x1000')
    root4.title('多表查询')
    Label(root4, text='多表查询（以所属部门、课程号、研究方向为条件）', bg='white', fg='red', font=('宋体', 15)).pack(side=TOP, fill='x')

    # 举例：查找网安学院、课程号为001、研究方向为数据库的教职工相关信息（性别、课程名等）
    Label(root4, text="dept：").place(relx=0.2, rely=0.05, relwidth=0.1)
    Label(root4, text="cour_no：").place(relx=0.2, rely=0.1, relwidth=0.1)
    Label(root4, text="research_dir：").place(relx=0.2, rely=0.15, relwidth=0.1)

    t1 = StringVar()
    t2 = StringVar()
    t3 = StringVar()

    global entry_t1
    global entry_t2
    global entry_t3

    entry_t1 = Entry(root4, textvariable=t1)
    entry_t1.place(relx=0.3, rely=0.05, relwidth=0.37, height=25)
    entry_t2 = Entry(root4, textvariable=t2)
    entry_t2.place(relx=0.3, rely=0.1, relwidth=0.37, height=25)
    entry_t3 = Entry(root4, textvariable=t3)
    entry_t3.place(relx=0.3, rely=0.15, relwidth=0.37, height=25)

    # 将输入框Entry放在一个列表中传入相关操作的函数中，利用get()获得输入值
    list4 = [entry_t1, entry_t2, entry_t3]

    Tree4 = ttk.Treeview(root4, show='headings', column=('tea_no', 'tea_name', 'sex', 'cour_name', 'patent'))
    Tree4.column('tea_no', width=150, anchor="center")
    Tree4.column('tea_name', width=150, anchor="center")
    Tree4.column('sex', width=150, anchor="center")
    Tree4.column('cour_name', width=150, anchor="center")
    Tree4.column('patent', width=150, anchor="center")
    # 表格标题设置
    Tree4.heading('tea_no', text='tea_no')
    Tree4.heading('tea_name', text='tea_name')
    Tree4.heading('sex', text='sex')
    Tree4.heading('cour_name', text='cour_name')
    Tree4.heading('patent', text='patent')

    Tree4.place(rely=0.25, relwidth=0.99)

    # 使用lambda匿名函数传参
    Button(root4, text="查找信息", command=lambda: findInfo(check=1, tree=Tree4, table='multi_table', list = list4)).place(relx=0.4, rely=0.2, width=100)


# 后续可以加一个登录界面，用户名密码就按照数据库的user和pwd进行比对，在之后的函数连接数据库部分就是用登录使用的变量值
# 登录成功后的主界面
def init():
    root0 = Tk()
    root0.geometry('300x300')
    root0.title('学校人事信息管理系统')
    Label(root0, text='学校人事信息管理', bg='white', fg='red', font=('宋体', 15)).pack(side=TOP, fill='x')

    Button(root0, text="教职工基本信息表", command=table1).place(relx=0.5, rely=0.2, width=100, anchor=CENTER)
    Button(root0, text="教职工教学信息表", command=table2).place(relx=0.5, rely=0.4, width=100, anchor=CENTER)
    Button(root0, text="教职工科研信息表", command=table3).place(relx=0.5, rely=0.6, width=100, anchor=CENTER)
    Button(root0, text="多表查询", command=table4).place(relx=0.5, rely=0.8, width=100, anchor=CENTER)


# 判断账号密码是否正确，若正确则进入主界面（这里还要关闭登录界面，待做！***）
def sign_in(root, table, username, pwd):
    db = pymysql.connect(host="localhost", user="root",
                         password="123456", db="school_teacher_information", port=3306)
    cur = db.cursor()
    cur.execute("select * from %s" % table)  # 执行sql语句
    results = cur.fetchall()  # 获取查询的所有记录
    for item in results:
        if (username.get() == item[0]) & (pwd.get() == item[1]):  # 这里简单规定好管理员账号密码，日后可改为从数据库中获取比对
            root.destroy()  # 进入主界面后，关闭登录窗口
            init()
        else:
            showinfo(title='提示', message='账号/密码错误！')
    cur.close()
    db.close()  # 关闭连接


root = Tk()
root.geometry('300x250')
root.title('Login')

Label(root, text='学校人事信息管理系统', bg='white', fg='red', font=('宋体', 15)).pack(side=TOP, fill='x')
Label(root, text='username').place(relx=0.1, rely=0.25)
Label(root, text='pwd').place(relx=0.1, rely=0.4)
username = StringVar()
pwd = StringVar()

entry_username = Entry(root, textvariable=username, show=None)
entry_username.place(relx=0.5, rely=0.25, relwidth=0.37)
entry_pwd = Entry(root, textvariable=pwd, show='*')
entry_pwd.place(relx=0.5, rely=0.4, relwidth=0.37)

# 将输入框作为参数传入函数中，再进行get，不能先判断，因为没有按下按钮触发动作，无法获取entry输入框的值
Button(root, text="登录", command=lambda: sign_in(root=root, table='admin', username=entry_username, pwd=entry_pwd)).place(relx=0.5, rely=0.7, width=100, anchor=CENTER)

root.mainloop()