from flask import Blueprint, render_template, request, redirect, url_for, flash, session,jsonify

import mysql.connector
import time
from datetime import date, timedelta
import connect_database
import ast
from datetime import datetime
from email.message import EmailMessage
import ssl
import smtplib



customer_app = Blueprint('customer',__name__)
current_date = date.today()
current_time = time.strftime("%H:%M:%S")

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect_database.dbuser, \
    password=connect_database.dbpass, host=connect_database.dbhost, \
    database=connect_database.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn



@customer_app.route("/customer/")   
def customer_home():
    email_input = session.get('email_input')
    today = date.today()
    tomorrow = today + timedelta(days=1)

    return render_template("customer/customer_home.html",email_input=email_input,today=today,tomorrow=tomorrow)

@customer_app.route("/customer/profile/",methods=['GET','POST'])
def customer_profile():
    if request.method == 'POST':
        customer_profile_now = request.form
        print(customer_profile_now)
        user_id = customer_profile_now['user_id']
        customer_fname_input = customer_profile_now['customer_fname']
        customer_lname_input = customer_profile_now['customer_lname']     
        email_input = customer_profile_now['email']        
        phone_input = customer_profile_now['phone']

        customer_fname_old = customer_profile_now['customer_fname_old']
        customer_lname_old =customer_profile_now['customer_lname_old']
        email_old = customer_profile_now['email_old']
        phone_old = customer_profile_now['phone_old']
        
        if customer_fname_input:
            customer_fname = customer_fname_input
        else:
            customer_fname = customer_fname_old

        if customer_lname_input:
            customer_lname = customer_lname_input
        else:
            customer_lname = customer_lname_old
        
        if email_input:
            email = email_input
        else:
            email = email_old

        if phone_input:
            phone = phone_input
        else:
            phone = phone_old



        cur = getCursor()   #update the new details into the db 
        dbsql = """update customer
                   set customer_fname=%s, customer_lname=%s,email=%s,phone=%s 
                   where user_id = %s;"""
        parameters = (customer_fname,customer_lname,email,phone,user_id)
        cur.execute(dbsql,parameters) 
        connection.commit()

        return redirect(url_for('customer.customer_profile', user_id = user_id, updated = 'yes'))
     
    else:
        email_input = session.get('email_input')
        cur = getCursor()
        query = """select user_id, customer_fname, customer_lname,email,phone from customer where email =%s;"""
        parameter = (email_input,)
        cur.execute(query,parameter)
        dbOutput=cur.fetchall()

        return render_template("customer/profile.html",dbOutput=dbOutput)


@customer_app.route("/customer/mybooking/")
def customer_mybooking():
    email_input = session.get('email_input')
    not_available= request.args.get('not_available')
    past_booking = request.args.get('past_booking')
    less_than_one_day = request.args.get('less_than_one_day')
    cancelled = request.args.get('cancelled')



    cur = getCursor() # fetch all the reservation of this customer
    query = """select c.customer_fname, c.customer_lname,r.room_type, re.check_in_date,re.check_out_date,re.total_room_charge,re.total_price,re.reservation_id,re.comfirmed
                from reservation as re
                join room as r
                on r.room_id = re.room_id
                join customer as c
                on c.customer_id = re.customer_id
                where c.email = %s
                ORDER BY 
                CASE
                    
                    WHEN (re.check_in_date > CURDATE() OR re.check_in_date = CURDATE()) and (re.comfirmed != -1) THEN 1  
                    ELSE 2  
                END,
                re.check_in_date;"""
    parameter = (email_input,)
    cur.execute(query,parameter)
    dbOutput=cur.fetchall()
    today = date.today()
    print(dbOutput)

    return render_template("customer/mybooking.html",cancelled=cancelled,less_than_one_day=less_than_one_day,past_booking=past_booking,dbOutput=dbOutput,today=today,not_available=not_available)

@customer_app.route("/customer/mybooking/unpaid/")
def customer_mybooking_unpaid():
    email_input = session.get('email_input')
    today = date.today()
    cur = getCursor() # fetch all the unpaid reservation of this customer
    query = """select c.customer_fname, c.customer_lname,r.room_type, re.check_in_date,re.check_out_date,re.total_room_charge,re.total_price,re.reservation_id,re.comfirmed
                from reservation as re
                join room as r
                on r.room_id = re.room_id
                join customer as c
                on c.customer_id = re.customer_id
                where c.email = %s and re.comfirmed = 0 and re.check_in_date >= %s;"""
    parameter = (email_input,today)
    cur.execute(query,parameter)
    dbOutput=cur.fetchall()  
    if dbOutput:
        unpaid = True 
    else:
        unpaid = False
    print(dbOutput) 
    return render_template("customer/mybooking.html",dbOutput=dbOutput,today=today,unpaid=unpaid)

@customer_app.route("/customer/mybooking/edit/",methods=["GET","POST"])
def customer_mybooking_edit():
    if request.method == "POST":
        reservation_id=request.form.get("reservation_id")
        room_type_old=request.form.get("room_type_old")
        check_in_date_old=request.form.get("check_in_date_old")
        check_out_date_old=request.form.get("check_out_date_old")
        selected_services_old=request.form.getlist("selected_services_old")
        special_needs_old=request.form.get("special_needs_old")

        check_in_date_new_str=request.form.get("check_in_date")
        check_in_date_new = datetime.strptime(check_in_date_new_str, '%Y-%m-%d').date()
        check_out_date_new_str=request.form.get("check_out_date")
        check_out_date_new = datetime.strptime(check_out_date_new_str, '%Y-%m-%d').date()
        special_needs_new=request.form.get("special_needs")

        room_type=request.form.get("room_type")  # got room_type new
        selected_services_list=request.form.getlist("selected_services")
        selected_services = ','.join(selected_services_list) # got selected services new

        selected_services_price = 0  # got selected_services_price
    
        if 'service_breakfast' in selected_services:
            selected_services_price += 20
        
        if 'service_earlier_checkin' in selected_services:  
            selected_services_price += 80
        
        if 'service_late_checkout' in selected_services:
            selected_services_price += 80 

        if special_needs_new != '':
            special_needs = special_needs_new
        else:
            special_needs = special_needs_old   # got special_needs new

        print(check_in_date_new,check_out_date_new,room_type,selected_services,special_needs,selected_services_price)
        

        # situation one only change services or special need, no date change ,no room type change
        if room_type == room_type_old and check_in_date_new == check_in_date_old and check_out_date_new == check_out_date_old:
            # fetch the current total_room_charge
            cur3=getCursor()
            query3="""select total_room_charge,total_price from reservation where reservation_id = %s;"""
            parameter3=(reservation_id,)
            cur3.execute(query3,parameter3)
            dbOutput3=cur3.fetchall()
            total_room_charge =dbOutput3[0][0]
            total_price_current = dbOutput3[0][1]
            total_price_new = float(total_room_charge) + float(selected_services_price)
            difference_price = float(total_price_new) - float(total_price_current)

            if difference_price > 0 :# customer needs to pay more money
                ## change the reservation table
                cur=getCursor()
                query="""update reservation
                            set selected_services = %s,special_needs = %s, total_price = %s, comfirmed = 0
                            where reservation_id = %s;"""
                parameters=(selected_services,special_needs,total_price_new,reservation_id)
                cur.execute(query,parameters)
                connection.close()

                return redirect(url_for('customer.customer_mybooking_edit_pay',difference_price=difference_price,reservation_id=reservation_id))
            elif difference_price < 0:  #customer will get the refund back
                # Extract date and time components
                today = date.today() ########################
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                ##############change payment table 
                cur=getCursor()
                query="""insert into payment (reservation_id,amount,date,time,method,payment_status)
                        values(%s,%s,%s,%s,'refund','paid');"""
                parameters=(reservation_id,difference_price,today,current_time)
                cur.execute(query,parameter)
                connection.close
                ##############change reservation table 改动checkin checkout等数据
                cur1=getCursor()
                query1="""update reservation
                                set selected_services = %s,special_needs = %s, total_price = %s
                                where reservation_id = %s;"""
                parameters1=(selected_services,special_needs,total_price_new,reservation_id)
                cur1.execute(query1,parameters1)
                connection.close()  
                booking_edited = True                  
                return render_template("customer/customer_home.html",booking_edited=booking_edited)
            else:
                # no more payment or refund, but only change reservation table
                ##############change reservation table 改动checkin checkout等数据
                cur1=getCursor()
                query1="""update reservation
                                set selected_services = %s,special_needs = %s, total_price = %s
                                where reservation_id = %s;"""
                parameters1=(selected_services,special_needs,total_price_new,reservation_id)
                cur1.execute(query1,parameters1)
                connection.close()  
                booking_edited = True                  
                return render_template("customer/customer_home.html",booking_edited=booking_edited)
               
            #print(f"this is total_room_charge{total_room_charge}, this is total price {total_price_new}")
            # update reservation table
            #cur2=getCursor()
            #query2="""update reservation
            #            set selected_services = %s,special_needs = %s, total_price = %s + %s ,comfirmed = 0
            #            where reservation_id = %s;"""
            #parameters2 =(selected_services,special_needs,total_price_new,selected_services_price,reservation_id)
            #cur2.execute(query2,parameters2)
            #connection.close()

            #return redirect(url_for('customer.customer_mybooking_edit_pay',difference_price=difference_price,reservation_id=reservation_id))  
        # #########################################situation 2 : date or room_type changed
        elif room_type != room_type_old or check_in_date_new != check_in_date_old or check_out_date_new != check_out_date_old:
            # make sure check_in_date is larger than or equal to today's date
            today = date.today()
            print(type(check_in_date_new),type(today))
            
            if check_in_date_new < today:
                print("past_booking!!!!!!!!!!")
                return redirect(url_for('customer.customer_mybooking',past_booking = True))
            elif check_out_date_new - check_in_date_new < timedelta(days=1):
                return redirect(url_for('customer.customer_mybooking',less_than_one_day = True))
            else:
                cur= getCursor()
                # explain the query: check_out_date only should bigger than varieble check_out_date since the room won't be occupied if they are same day
                query="""SELECT room_id, room_type, description, price_per_night FROM room
                    WHERE room_id NOT IN (
                        SELECT room_id FROM reservation
                        WHERE (check_in_date >= %s AND check_out_date <= %s) OR  
                    (check_in_date <= %s AND check_out_date > %s)
                    ) and room_type = %s
                    ;"""
                cur.execute(query,(check_in_date_new,check_out_date_new,check_in_date_new,check_in_date_new,room_type))
                available_rooms = cur.fetchall()  

                if available_rooms:
                    room_id = available_rooms[0][0]
                    price_per_night = available_rooms[0][3]
                    ##### check if the customer need to pay more or get refund
                    ## fetch the total price of the old reservation
                    cur= getCursor()
                    query="""select total_price from reservation where reservation_id = %s;"""
                    parameter = (reservation_id,)
                    cur.execute(query,parameter)
                    dbOutput=cur.fetchall()
                    total_price_current = dbOutput[0][0]
                    total_price_current = float(total_price_current)
                    print(f"this is total price current{total_price_current}")
                    ## fetch the total price if for the new reservation
                    check_in_date = check_in_date_new

                    check_out_date = check_out_date_new
      
                    # Calculate the number of days between check_in and check_out
                    delta = check_out_date - check_in_date
                    num_of_days = delta.days

                    # Convert the price to a float (assuming it's a string)
                    price_per_night = float(price_per_night)

                    # Calculate the total_price for new reservation
                    total_room_charge_new = price_per_night * num_of_days 
                    total_price_new =  total_room_charge_new + selected_services_price
                    print(f"this is total price new{total_price_new}")      
                    # calculate the difference between the current and new reservation on total price
                    difference_price = total_price_new - total_price_current
                    print(f"this is difference_price {difference_price}")

                    if difference_price > 0 :# customer needs to pay more money
                    ## change the reservation table
                        cur=getCursor()
                        query="""update reservation
                                        set room_id=%s, check_in_date = %s, check_out_date=%s, total_room_charge =%s,selected_services = %s,special_needs = %s, total_price = %s
                                        where reservation_id = %s;"""
                        parameters=(room_id,check_in_date,check_out_date,total_room_charge_new,selected_services,special_needs,total_price_new,reservation_id)
                        cur.execute(query,parameters)
                        connection.close()

                        return redirect(url_for('customer.customer_mybooking_edit_pay',difference_price=difference_price,reservation_id=reservation_id))
                    elif difference_price < 0:  #customer will get the refund back
                        # Extract date and time components
                        today = date.today() ########################
                        now = datetime.now()
                        current_time = now.strftime("%H:%M:%S")
                        ##############change payment table 
                        cur4=getCursor()
                        query4="""insert into payment (reservation_id,amount,date,time,method,payment_status)
                            values(%s,%s,%s,%s,'refund','paid');"""
                        parameters4=(reservation_id,difference_price,today,current_time)
                        cur4.execute(query4,parameters4)
                        connection.close
                        ##############change reservation table 改动checkin checkout等数据
                        cur1=getCursor()
                        query1="""update reservation
                                        set room_id=%s, check_in_date = %s, check_out_date=%s, total_room_charge =%s,selected_services = %s,special_needs = %s, total_price = %s
                                        where reservation_id = %s;"""
                        parameters1=(room_id,check_in_date,check_out_date,total_room_charge_new,selected_services,special_needs,total_price_new,reservation_id)
                        cur1.execute(query1,parameters1)
                        connection.close()  
                        booking_edited = True                  
                        return render_template("customer/customer_home.html",booking_edited=booking_edited)
                    else:
                        # no more payment or refund, but only change reservation table
                        ##############change reservation table 改动checkin checkout等数据
                        cur1=getCursor()
                        query1="""update reservation
                                        set room_id=%s, check_in_date = %s, check_out_date=%s, total_room_charge =%s,selected_services = %s,special_needs = %s, total_price = %s
                                        where reservation_id = %s;"""
                        parameters1=(room_id,check_in_date,check_out_date,total_room_charge_new,selected_services,special_needs,total_price_new,reservation_id)
                        cur1.execute(query1,parameters1)
                        connection.close()  
                        booking_edited = True                  
                        return render_template("customer/customer_home.html",booking_edited=booking_edited)               
                else: 
                    return redirect(url_for('customer.customer_mybooking',not_available=True))
    else:
        reservation_id = request.args.get("reservation_id")
        cur=getCursor()
        query="""select re.room_id,r.room_type,re.check_in_date,re.check_out_date,re.total_room_charge,re.selected_services,re.special_needs,re.total_price
                from reservation as re
                join room as r
                on re.room_id = r.room_id
                where reservation_id = %s;"""
        parameter =(reservation_id,)
        cur.execute(query,parameter)
        dbOutput=cur.fetchall()
        return render_template('customer/mybooking_edit.html',dbOutput=dbOutput,reservation_id=reservation_id)

@customer_app.route("/customer/mybooking/edit/pay",methods=["GET","POST"])
def customer_mybooking_edit_pay():
    if request.method == 'POST':
        difference_price = request.form.get('difference_price')
        reservation_id = request.form.get('reservation_id')
        print(f"this is after submit payment {difference_price},{reservation_id}")
        # Extract date and time components
        today = date.today() ########################
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        # insert new data into payment table
        cur4 = getCursor()
        query4 ="""insert into payment (reservation_id,amount,date,time,method,payment_status)
                   values(%s,%s,%s,%s,'online payment','paid');"""  
        parameters4 =(reservation_id,difference_price,today,current_time) 
        cur4.execute(query4,parameters4)
        connection.close() 
        booking_edited = True
        

        # change the reservation table
        cur = getCursor()
        query = """update reservation
                   set comfirmed = 1 where reservation_id = %s;"""
        parameter = (reservation_id,)
        cur.execute(query,parameter)
        connection.close()
        return render_template("customer/customer_home.html",booking_edited=booking_edited)
    else:
        difference_price = request.args.get('difference_price')
        reservation_id = request.args.get('reservation_id')
        print(difference_price,reservation_id)
        return render_template("customer/customer_pay_edit.html",difference_price=difference_price,reservation_id=reservation_id)

   
@customer_app.route("/customer/check_availability/",methods=['GET','POST'])
def check_availability():
    check_in = datetime.strptime(request.form['check_in_date'], '%Y-%m-%d')
    check_in_date=check_in.date()
    check_out = datetime.strptime(request.form['check_out_date'], '%Y-%m-%d')
    check_out_date=check_out.date()

    print(check_in_date)
    print(check_out_date)
    
    available_rooms = get_available_rooms(check_in_date, check_out_date)
    print(f"this is available_rooms:{available_rooms}")

    return render_template('customer/availability.html', available_rooms=available_rooms,check_in_date=check_in_date,check_out_date=check_out_date)

def get_available_rooms(check_in_date, check_out_date):
    cur= getCursor()
    # explain the query: check_out_date only should bigger than varieble check_out_date since the room won't be occupied if they are same day
    query="""SELECT room_type, description, price_per_night FROM room
        WHERE room_id NOT IN (
            SELECT room_id FROM reservation
            WHERE (check_in_date >= %s AND check_out_date <= %s) OR  
          (check_in_date <= %s AND check_out_date > %s)
        )
        GROUP BY room_type;"""
    cur.execute(query,(check_in_date,check_out_date,check_in_date,check_in_date))
    available_rooms = cur.fetchall()
    connection.close()
    return available_rooms

    
@customer_app.route("/customer/book_room/",methods=['GET','POST'])
def book_room():

    if request.method == 'POST':
        check_in_date = request.form.get("check_in")
        check_out_date = request.form.get("check_out")
        room_type = request.form.get("room_type")
        total_room_charge = request.form.get("total_room_charge")
        special_needs = request.form.get("special_needs")

        email_input = session.get('email_input')

        selected_services_list=request.form.getlist("selected_services")
        selected_services_price = 0
    
        if 'service_breakfast' in request.form:
            selected_services_list.append('service_breakfast')
            selected_services_price += 20
        
        if 'service_earlier_checkin' in request.form:
            selected_services_list.append('service_earlier_checkin')
            selected_services_price += 80
        
        if 'service_late_checkout' in request.form:
            selected_services_list.append('service_late_checkout')
            selected_services_price += 80 

        print(total_room_charge,selected_services_price,selected_services_list,special_needs)
        selected_services = ','.join(selected_services_list)
        total_price = float(total_room_charge) + float(selected_services_price)    
        
        # Extract date and time components
        
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")    

        # fetch all the room_ids under specific room type
        cur1 = getCursor()
        query1="""select room_id from room where room_type = %s;"""
        parameter=(room_type,)
        cur1.execute(query1,parameter)
        dbOutput1 = cur1.fetchall()
        all_room_ids = [item[0] for item in dbOutput1]
        print(all_room_ids)

        # fetch the occupied room_ids during this period
        cur= getCursor()
        query="""select room_id from reservation where check_in_date = %s and check_out_date = %s;"""
        parameters = (check_in_date,check_out_date)
        cur.execute(query,parameters)
        dbOutput = cur.fetchall()
        occupied_room_ids = [item[0] for item in dbOutput]
        print(f"this is occupied_rooms{occupied_room_ids}")

        # Calculate available room IDs
        available_room_ids = [room_id for room_id in all_room_ids if room_id not in occupied_room_ids]
        print(f"this is available_rooms{available_room_ids}")

        # the room for this user
        room_id = available_room_ids[0]
        print(f"this is room_id{room_id}")
        #fetch the customer id
        cur2=getCursor()
        query2="""select customer_id from customer where email = %s;"""
        parameter2 = (email_input,)
        cur2.execute(query2,parameter2)
        dbOutput2 = cur2.fetchall()
        customer_id = dbOutput2[0][0]
        
        print(customer_id,room_id,check_in_date,check_out_date,total_room_charge,total_price,special_needs,selected_services,now)
        
        # insert new data into reservation table with the value '0' for 'comfirmed'
        cur=getCursor()
        query = ("""INSERT INTO reservation (customer_id,room_id,check_in_date, check_out_date,total_room_charge,total_price,special_needs,selected_services,comfirmed,reservation_time)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,0,%s);""")         
        parameters2 = (customer_id,room_id,check_in_date,check_out_date,total_room_charge,total_price,special_needs,selected_services,now)
        cur.execute(query,parameters2)
        connection.close()   

        # fetch the reservation id
        cur3=getCursor()
        query3="""select reservation_id from reservation where customer_id = %s and room_id = %s and check_in_date =%s and check_out_date = %s;"""
        parameters3 = (customer_id,room_id,check_in_date,check_out_date)
        cur3.execute(query3,parameters3)
        dbOutput3=cur3.fetchall()
        reservation_id = dbOutput3[0][0]
        return redirect(url_for('customer.pay',reservation_id=reservation_id))
    else: 
        # fetch reservation details
        check_in_date = request.args.get("check_in")
        check_out_date = request.args.get("check_out")
        room_type = request.args.get("room_type")
        price=request.args.get("price")

        check_in_date_time = datetime.strptime(check_in_date, "%Y-%m-%d")
        check_in_date = check_in_date_time.date()
        check_out_date_time = datetime.strptime(check_out_date, "%Y-%m-%d")
        check_out_date = check_out_date_time.date()

        # Calculate the number of days between check_in and check_out
        delta = check_out_date - check_in_date
        num_of_days = delta.days

        # Convert the price to a float (assuming it's a string)
        price = float(price)

        # Calculate the total_price
        total_room_charge = price * num_of_days

        # fetch customer info
        email_input = session.get('email_input')
        cur=getCursor()
        cur.execute("select concat(customer_fname,' ',customer_lname) from customer where email = %s",(email_input,))
        dbOutput=cur.fetchall()
        customer_name = dbOutput[0][0]
        return render_template('customer/book_room.html',email_input=email_input,customer_name=customer_name,check_in_date=check_in_date,check_out_date=check_out_date,room_type=room_type,num_of_days=num_of_days,total_room_charge=total_room_charge)


@customer_app.route("/customer/pay/",methods=['GET','POST'])
def pay():

    if request.method == 'POST':
        reservation_id = request.form.get('reservation_id')

        total_price_form =request.form.get('total_price')

        if total_price_form:
            total_price = total_price_form
        else:
            # fetch the price the customer need to pay
            cur=getCursor()
            cur.execute("""select total_price from reservation where reservation_id = %s""",(reservation_id,))
            dbOutput=cur.fetchall()
            total_price = dbOutput[0][0]
            



        #fetch room_id
        cur=getCursor()
        cur.execute("""select room_id,customer_id from reservation where reservation_id =%s""",(reservation_id,))
        dbOutput = cur.fetchall()
        room_id = dbOutput[0][0]
        customer_id = dbOutput[0][1]

        
        
        # ######################### CHANGE COMFIRMED COLUMN IN RESERVATION TABLE################################################
        cur1=getCursor()
        cur1.execute("""update reservation
                       set comfirmed = 1 where reservation_id = %s""",(reservation_id,))
        connection.close()
        
 

        # insert new data into payment table
        today = date.today() ########################
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S") 
        cur4 = getCursor()
        query4 ="""insert into payment (reservation_id,amount,date,time,method,payment_status)
                   values(%s,%s,%s,%s,'online payment','paid');"""  
        parameters4 =(reservation_id,total_price,today,current_time) 
        cur4.execute(query4,parameters4)
        connection.close() 
        book_successfully = True

        return render_template("customer/customer_home.html",book_successfully=book_successfully)
    else:

        reservation_id =request.args.get('reservation_id')
        total_price =request.args.get('total_price')
        if total_price:
            return render_template("customer/customer_pay.html",reservation_id=reservation_id,total_price=total_price)
        else:
            cur=getCursor()
            cur.execute("""select re.*,r.room_type from reservation as re join room as r on re.room_id = r.room_id where re.reservation_id=%s""",(reservation_id,))
            dbOutput=cur.fetchall()
            print(f"this is dbOutput ;{dbOutput}")
            check_in_date = dbOutput[0][3]
            check_out_date = dbOutput[0][4]
            room_type = dbOutput[0][11]
            total_price = dbOutput[0][8]
            special_needs = dbOutput[0][7]
            selected_services= dbOutput[0][6]
            total_room_charge =dbOutput[0][5]

    
            return render_template("customer/customer_pay.html",reservation_id=reservation_id,total_room_charge=total_room_charge,special_needs=special_needs,selected_services=selected_services,check_in_date=check_in_date,check_out_date=check_out_date,room_type=room_type,total_price=total_price)


@customer_app.route("/customer/mybooking/cancel/",methods=['GET','POST'])
def cancel():
    if request.method == 'POST':
        reservation_id=request.form.get('reservation_id')
        # fetch if the reservation has been paid (will has refund or not)
        cur=getCursor()
        cur.execute("""select comfirmed,total_price from reservation where reservation_id=%s""",(reservation_id,))
        dbOutput=cur.fetchall()
        paid=dbOutput[0][0]
        total_price=dbOutput[0][1]
        # change the reservation table
        cur1=getCursor()
        cur1.execute("""update reservation set comfirmed = -1 where reservation_id = %s""",(reservation_id,))
        connection.close()  

        # make the refund (change payment table)
        if paid:
         # Extract date and time components     
           today = date.today()   
           now = datetime.now()
           current_time = now.strftime("%H:%M:%S")   
           refund_amount = -total_price

           cur2=getCursor()
           cur2.execute("""insert into payment (reservation_id,amount,date,time,method,payment_status)
                           values(%s,%s,%s,%s,'refund','paid')""",(reservation_id,refund_amount,today,current_time))   
           connection.close()   

        return redirect(url_for('customer.customer_mybooking',cancelled=True))
    else:
        reservation_id = request.args.get('reservation_id')
        cur=getCursor()
        cur.execute("""select re.*, r.room_type,r.price_per_night from reservation as re join room as r on re.room_id=r.room_id where reservation_id = %s""",(reservation_id,))
        dbOutput = cur.fetchall()

        return render_template("customer/cancel.html",dbOutput=dbOutput)


@customer_app.route("/customer/room/")
def customer_room():
    email_input = session.get('email_input')
    cur = getCursor()
    cur.execute("""select * from room group by room_type;""")
    rooms = cur.fetchall()

    

    return render_template("customer/customer_room.html",email_input=email_input,rooms=rooms)
   

@customer_app.route('/customer/handle_login/', methods=['GET','POST'])
def handle_login():
    print(f"enter handle")
    if request.method == 'POST':
        data = request.json  # Get the JSON data sent by the client
        email_input = data.get('email')
        password_input = data.get('password')
        role_input = data.get('role')

        print(email_input,password_input,role_input)

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
                    print(f"logged in")   
                    return redirect(url_for('customer.customer_home'))   # head to cutomer home page
                else:
                    return render_template("main/home.html", incorrect_password = "Incorrect password, please try again!")
            else:
                return render_template("main/home.html", not_customer = "We can't find your information, please check your email or register first, thank you!")  
        elif role_input == 'staff':  ##########role1 supervisor
            cur = getCursor()  # fetch emial list of all supervisors
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
                    return redirect(url_for('staff.staff_home'))  # head to student home page
                else:
                    return render_template("main/home.html", incorrect_password = "Incorrect password, please try again!")
            else:
                return render_template("main/home.html", incorrect_email = "Email not exists, please try again")

        else:
            new_customer = request.args.get('new_customer')
            return render_template("main/home.html",new_customer=new_customer)
    else:
        return "nothing"