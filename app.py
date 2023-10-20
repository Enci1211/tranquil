import mysql.connector
from mysql.connector import FieldType
import datetime
import time
from datetime import date,timedelta
import connect_database
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, flash
from customer import customer_app
from staff import staff_app
from manager import manager_app



app = Flask(__name__)


########Blueprint############

app.register_blueprint(customer_app)

app.register_blueprint(staff_app)

app.register_blueprint(manager_app)


app.secret_key = "supersecretkey"


# Configure Celery
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'  # Use your own broker URL
# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)
# get current date and calculate the date 7 days from now
current_date = date.today()

future_date = current_date + timedelta(days=7)
current_time = time.strftime("%H:%M:%S")

# format dates for the query
current_date_str = current_date.strftime('%Y-%m-%d')
future_date_str =future_date.strftime('%Y-%m-%d')

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect_database.dbuser, \
    password=connect_database.dbpass, host=connect_database.dbhost, \
    database=connect_database.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

# Define the Celery task
# @celery.task
# def cancel_unpaid_booking(reservation_id):
#     try:
#         cur = getCursor()
#         cur.execute("SELECT reservation_time, comfirmed FROM reservation WHERE reservation_id = %s", (reservation_id,))
#         dbOutput = cur.fetchone()
#         cur.close()

#         reservation_time = dbOutput[0]
#         comfirmed_status = dbOutput[1]

#         if comfirmed_status == 0:
#             current_time = datetime.now()
#             if current_time - reservation_time > timedelta(minutes=30):
#                 cur = getCursor()
#                 cur.execute("UPDATE reservation SET confirmed = 'cancelled' WHERE reservation_id = %s", (reservation_id,))
#                 cur.close()

#     except Exception as e:
#         # Handle any exceptions or errors here
#         print(f"Error processing task: {str(e)}")



# home page for login 
@app.route("/", methods = ['POST','GET'])
def home():    
    if request.method == 'POST':
        email_input = request.form['email_input'] 
        password_input = request.form['password_input']
        role_input = request.form['role']

        print(email_input)
        print(password_input)
        print(role_input)
        
        if role_input == 'customer':   ###########role1 customer
           cur = getCursor()  # fetch emial list of all customer
           cur.execute("""SELECT email FROM customer;""") 
           dbOutput = cur.fetchall()
           emailList_customer = [item for m in dbOutput for item in m]

           if email_input in emailList_customer:
              cur1 = getCursor()  # fetch correct password matching this email
              sql1 = """select password from user as u 
                        join customer as c
                        on c.user_id = u.user_id
                        where c.email = %s """
              parameter1 = (email_input,)
              cur1.execute(sql1,parameter1)
              dbOutput1 = cur1.fetchall()
              correct_password = dbOutput1[0][0]

              if password_input == correct_password:
                    session['email_input'] = email_input  # store user's email and password into session for re-use in the future
                    session['role_input'] = role_input
                    session['password_input'] = password_input
                        
                    return redirect(url_for('customer.customer_home'))   # head to student home page
              else:
                 return render_template("main/home.html", incorrect_password = "Incorrect password, please try again!")
           else:
              return render_template("main/home.html", not_customer = "We can't find your information, please check your email or register first, thank you!")  
        elif role_input == 'staff':  ##########role1 staff
           cur = getCursor()  # fetch emial list of all staff
           cur.execute("""SELECT email FROM staff;""") 
           dbOutput = cur.fetchall()
           emailList_staff = [item for m in dbOutput for item in m]

           if email_input in emailList_staff:
              cur1 = getCursor()  # fetch correct password matching this email
              sql1 = """select password from user as u 
                        join staff as s
                        on s.user_id = u.user_id
                        where s.email = %s  """
              parameter1 = (email_input,)
              cur1.execute(sql1,parameter1)
              dbOutput1 = cur1.fetchall()
              print(dbOutput1)
              correct_password = dbOutput1[0][0]

              if password_input == correct_password:
                 session['email_input'] = email_input  # store user's email and password into session for re-use in the future
                 session['role_input'] = role_input
                 session['password_input'] = password_input

                 # judge if the user is a manager or not
                 cur2 = getCursor()
                 query2 = """select is_manager from staff where email = %s;"""
                 parameter2 =(email_input,)
                 cur2.execute(query2,parameter2)
                 dbOutput=cur2.fetchall()
                 is_manager = dbOutput[0][0]
                 if is_manager:
                     return redirect(url_for('manager.manager_home')) # head to manager home page
                 else:
                     return redirect(url_for('staff.staff_home'))  # head to staff home page
              else:
                 return render_template("main/home.html", incorrect_password = "Incorrect password, please try again!")
           else:
              return render_template("main/home.html", incorrect_email = "Email not exists, please try again")
    
    else:
        new_customer = request.args.get('new_customer')
        return render_template("main/home.html",new_customer=new_customer)
    





#### register #####
@app.route("/register", methods = ['POST','GET'])   
def register():
   if request.method == 'POST':
      new_customer = request.form
 
      first_name = new_customer.get('first_name')
      last_name = new_customer.get('last_name')
      email = new_customer.get('email')
      password = new_customer.get('password')
      phone = new_customer.get('phone')

      
      cur = getCursor()
      cur.execute("SELECT email FROM customer WHERE email = %s", (email,))
      dbOutput = cur.fetchall()

            # Validate email
      if dbOutput:
         exist_email = True   # NOT exited email
         return redirect(url_for('register',exist_email=exist_email))
            # Validate phone number
      elif not phone.isdigit():
         wrong_phone = True
         return redirect(url_for('register',wrong_phone=wrong_phone))
 
      else:  
            new_customer=True    # update user & customer table
            
            cur2 = getCursor() # update user table firstly
            sql2=("""insert into user
                     (password, role) values
                     (%s, 'customer');""")
            parameter2 = (password,)
            cur2.execute(sql2,parameter2)
            connection.commit()
            connection.close()

            cur3 = getCursor()  # fetch new user id
            sql3 = ("""select user_id from user where password = %s;""")
            parameter3 = (password,)
            cur3.execute(sql3,parameter3)
            dbOutput3 = cur3.fetchall()

            user_id= dbOutput3[0][0]
            
            print(user_id)
            
            cur = getCursor() # update customer table
            sql=("""INSERT INTO customer
                            (user_id, customer_fname, customer_lname,email,phone)
                            VALUES (%s,%s,%s,%s,%s);""")
            parameters = (user_id, first_name, last_name, email, phone)
            cur.execute(sql,parameters)
            connection.commit()   

            return render_template("main/home.html",new_customer=new_customer)
   else:
        exist_email = request.args.get('exist_email')
        wrong_phone = request.args.get('wrong_phone')

        return render_template("main/register.html",exist_email=exist_email,wrong_phone=wrong_phone)



