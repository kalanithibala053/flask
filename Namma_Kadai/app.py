from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from flask_mysqldb import MySQL
import MySQLdb.cursors
app = Flask(__name__)
app.secret_key = "your_secret_key"  
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="20ita18@1234567890",
    database="demo"
)


@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']       
		if username=='root' and password=='root':
            
			msg = 'Logged in successfully !'
			return redirect(url_for('index'))
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
	
	return redirect(url_for('login'))

@app.route('/index')
def index():
    
    cursor = db.cursor()
    cursor.execute('SELECT company_name FROM company')
    account = cursor.fetchone()[0]
    name=account
    db.commit()
    cursor.close()
    return render_template('index.html',company_name=name)

@app.route('/newitem',methods=['GET','POST'])
def newitem():
    msg = ""
    cursor = db.cursor()
    cursor.execute('SELECT item_id FROM item ORDER BY item_id DESC LIMIT 1')
    last_itemid = cursor.fetchone()
    cursor.execute('SELECT item_name,qty FROM item')
    item = cursor.fetchall()
    
    if request.method == 'POST':
        itemname = request.form['itemname']
        if itemname !="":
            quantity = 0
        
            if last_itemid:
                last = last_itemid[0]
                l = last[0]   
                num = last[1:] 
                last_itemid = f'{int(num) + 1:04d}'
                itemid = l + last_itemid

                cursor.execute('INSERT INTO item (item_id, item_name, qty) VALUES (%s, %s, %s)',
                           (itemid, itemname, quantity))
                db.commit()
                msg = "Successfully added"
                cursor=db.cursor()
                
                cursor.execute("insert  into itemrepo (From_ID,item_id,qty) values('Create',%s,%s)",(itemid,quantity))
               
        return redirect('/viewitem')
    cursor=db.cursor()
    cursor.execute("select * from itemrepo")
    itemrepo=cursor.fetchall()
    return render_template('viewitem.html',item=item,itemrepo=itemrepo)

@app.route('/viewpurchase')

def viewpurchase():
    
    cursor = db.cursor()
    cursor.execute('SELECT * FROM purchase')
    purchase = cursor.fetchall()
    cursor.execute('SELECT cash_balance FROM company WHERE company_name ="Namma Kadai" ')
    account = cursor.fetchone()
    balance=account[0]
    msg=purchase
    db.commit()
    cursor.close()
    return render_template('viewpurchase.html',purchase=purchase,balance=balance)

@app.route('/viewsales')
def viewsales():
    cursor = db.cursor()
    cursor.execute('SELECT * FROM sales ')
    sales = cursor.fetchall()
    cursor.execute('SELECT cash_balance FROM company WHERE company_name ="Namma Kadai" ')
    account = cursor.fetchone()
    balance=account[0]
    db.commit()
    cursor.close()
    return render_template('viewsales.html',sales=sales,balance=balance)

@app.route('/itemdelete',methods=['POST','GET'])
def itemdelete():
    cursor = db.cursor()
    if request.method == 'POST':
        itemname = request.form['item']
        cursor.execute("select * from item where item_name=%s",(itemname,))
        id=cursor.fetchone()[0]
        cursor.execute("DELETE FROM item WHERE item_name=%s",(itemname,))
        msg="The item is succesfully deleted"
        cursor.execute('SELECT cash_balance FROM company WHERE company_name ="Namma Kadai" ')
        account = cursor.fetchone()
        balance=account[0]
        cursor.execute('SELECT item_name,qty FROM item')
        item = cursor.fetchall()
        db.commit()
        cursor.close()
        cursor=db.cursor()
                
        cursor.execute("insert  into itemrepo (From_ID,item_id,qty) values('Delete',%s,'0')",(id,))
    cursor=db.cursor()
    cursor.execute("select * from itemrepo")
    itemrepo=cursor.fetchall()  
    return render_template('viewitem.html',item=item,itemrepo=itemrepo)

@app.route('/viewitem')
def viewitem():
    cursor = db.cursor()
    cursor.execute('SELECT item_name,qty FROM item')
    item = cursor.fetchall()
    cursor.execute('SELECT cash_balance FROM company WHERE company_name ="Namma Kadai" ')
    account = cursor.fetchone()
    balance=account[0]
    db.commit()
    cursor.close()
    cursor=db.cursor()
   
    cursor.execute("select * from itemrepo")
    itemrepo=cursor.fetchall()
    return render_template('viewitem.html',item=item,balance=balance,itemrepo=itemrepo)

@app.route('/cash',methods=['POST','GET'])
def cash():
     cash=0
     msg='assign'
     cursor=db.cursor()
     cursor.execute("select cash_balance from company where company_name='Namma Kadai'")
     bal1=cursor.fetchone()
     bal=float(bal1[0])
     if request.method=='POST' and 'cash' in request.form:
          cash=float(request.form['cash'])
          final=bal+cash
          cursor=db.cursor()
          cursor.execute("update company set cash_balance=%s WHERE company_name='Namma Kadai'",((final),))
          
          cursor=db.cursor()
          cursor.execute("INSERT INTO balance (From_ID,action,current_bal) VALUES (%s,%s,%s)",
                       (msg,str(cash),(final),))
          
          cursor=db.cursor()
          cursor.execute("select * from balance")
          cash_h=cursor.fetchall()
     return render_template('balance.html',balance=final,cash_history=cash_h)
@app.route('/balance')
def balance():
     cursor=db.cursor()
     cursor.execute("select cash_balance from company where company_name='Namma Kadai'")
     bal1=cursor.fetchone()
     bal=bal1[0]
     cursor.execute("select * from balance")
     cash_h=cursor.fetchall()
     return render_template('balance.html',balance=bal,cash_history=cash_h)

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    msg=''
    
    cursor =db.cursor()
    cursor.execute("SELECT cash_balance FROM company WHERE company_name = 'Namma Kadai'")
    cash_balance = cursor.fetchone()
    cash=int(cash_balance[0])
    
    cursor.close()

    msg1=''
    msg2=''

    if request.method == 'POST':
        item = request.form['item']
        qty = int(request.form['qty'])
        rate = int(request.form['rate'])
        purc=qty*rate
        amount=cash-(qty*rate)
        msg2=qty
        msg1=rate
        cursor = db.cursor()
        cursor.execute('SELECT purchase_id FROM purchase ORDER BY purchase_id DESC LIMIT 1')
        last_purchaseid = cursor.fetchone()
        if last_purchaseid is None:
            purchaseid="P0001"
        else:
            last=last_purchaseid[0]
            l = last[0]   
            num = last[1:] 
            last_purchaseid = f'{int(num) + 1:04d}'
            purchaseid=l+last_purchaseid
        if amount >=0 and qty>0:
            cursor = db.cursor()
            cursor.execute("SELECT item_id FROM item WHERE item_name = %s",(item,))
            id=cursor.fetchone()
            

            cursor.execute("INSERT INTO purchase (purchase_id,item_name, qty, rate, amount,item_id) VALUES (%s,%s, %s, %s, %s,%s)",
                       (purchaseid,item, qty, rate, qty * rate,id[0],))
            
            cursor.execute("UPDATE item SET qty = qty+%s where item_name=%s", (qty,item,))
            cursor.execute("UPDATE company SET cash_balance = %s where company_name='Namma Kadai'", (amount,))
            cursor.execute("INSERT INTO balance (From_ID,action,current_bal) VALUES (%s,%s,%s)",
                       (purchaseid,str(qty*rate),amount,))
            cash=amount
            msg = f"Your purchased amount is {purc}"
            db.commit()
            cursor.close()
            cursor=db.cursor()
            cursor.execute("insert  into itemrepo (From_ID,item_id,qty) values(%s,%s,%s)",(purchaseid,id[0],msg2))
            
        elif qty<0:
            msg="Enter valid quantity"
        else:
            cash_balance="quantity exceeds"
    cursor = db.cursor()
    cursor.execute("SELECT * FROM item")
    items = cursor.fetchall()
    cursor.execute("select * from itemrepo")
    itemrepo=cursor.fetchall()
    cursor.close()
    return render_template('purchase.html', items=items,msg=msg,itemrepo=itemrepo)

@app.route('/sales', methods=['GET', 'POST'])
def sales():
   
    msg=''
    if request.method == 'POST':
        item = request.form['item']
        qty = int(request.form['qty'])
        rate = int(request.form['rate'])
        cursor = db.cursor()
        msg2=str(qty)
        cursor.execute('SELECT sales_id FROM sales ORDER BY sales_id DESC LIMIT 1')
        last_salesid = cursor.fetchone()
        if last_salesid is None:
            salesid="S0001"
        else:
            last=last_salesid[0]
            l = last[0]   
            num = last[1:] 
            last_salesid = f'{int(num) + 1:04d}'
            salesid=l+last_salesid
        cursor.execute("SELECT cash_balance FROM company WHERE company_name = 'Namma Kadai'")
        cash_balance = cursor.fetchone()
        cash=int(cash_balance[0])
        
        cursor.execute("select qty from item where item_name=%s",(item,))
        iiqty=cursor.fetchone()
        if iiqty is not None:
            iqty=int(iiqty[0])

        else:
            iqty=0 
        if qty <=iqty and qty>0:   
            cursor.execute("SELECT item_id FROM item WHERE item_name = %s",(item,))
            id=cursor.fetchone()
            amount=cash+(qty*rate)
            uqty=int(iqty)-qty
            
            cursor.execute("UPDATE item SET qty =%s where item_name =%s",  (uqty,item,))
            cursor.execute("INSERT INTO balance (From_ID,action,current_bal) VALUES (%s,%s,%s)",
                       (salesid,str(qty*rate),amount))
            cursor.execute("INSERT INTO sales (sales_id,item_name, qty, rate, amount,item_id) VALUES (%s, %s, %s, %s,%s,%s)",
                       (salesid,item, qty, rate, qty * rate,id[0]))
            db.commit()
            cursor = db.cursor()
            
            query="UPDATE company SET cash_balance =  %s where company_name = 'Namma Kadai'"
            data = (amount,) 
            cursor.execute(query, data)
            cursor=db.cursor()
                
            cursor.execute("insert  into itemrepo (From_ID,item_id,qty) values(%s,%s,%s)",(salesid,id[0],msg2))
            
            db.commit()
            msg=f'Your sold amount is {qty*rate}' 
            cursor.close()
        elif qty<0:
            msg="Enter valid quantity"
        else:
             msg="The quantity is greater than available quantity"
    cursor = db.cursor()
    cursor.execute("SELECT * FROM item where qty>0")
    items = cursor.fetchall()
    cursor.execute("select * from itemrepo")
    itemrepo=cursor.fetchall()
    cursor.close()
    return render_template('sales.html', items=items,msg=msg,itemrepo=itemrepo )

if __name__ == '__main__':
    app.run(debug=True)
