from flask import Blueprint, render_template, request, redirect, url_for, flash, session,jsonify

import mysql.connector
import time
import datetime
from datetime import date, timedelta
import connect_database
import ast
from datetime import datetime
from email.message import EmailMessage
import ssl
import smtplib



manager_app = Blueprint('manager',__name__)
current_date = date.today()
current_time = time.strftime("%H:%M:%S")
today = date.today()
tomorrow = today + timedelta(days=1)

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect_database.dbuser, \
    password=connect_database.dbpass, host=connect_database.dbhost, \
    database=connect_database.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

@manager_app.route("/manager/")   
def manager_home():
    email_input = session.get('email_input')
    return render_template("manager/manager_home.html",email_input=email_input,today=today,tomorrow=tomorrow)

@manager_app.route("/manager/room/")
def manager_room():
    cur=getCursor()
    query = """select * from room;"""
    cur.execute(query)
    rooms = cur.fetchall()
    return render_template("manager/manager_room.html",rooms=rooms)


@manager_app.route("/manager/room_availability/")
def manager_room_availability():
    # Calculate the date of this week
    days_until_monday = (today.weekday() - 0) % 7
    monday_date = today - timedelta(days=days_until_monday)
    tuesday_date = monday_date + timedelta(days=1)
    wednessday_date = monday_date + timedelta(days=2)
    thursday_date = monday_date + timedelta(days=3)
    friday_date = monday_date + timedelta(days=4)
    saturday_date = monday_date + timedelta(days=5)
    sunday_date = monday_date + timedelta(days=6)

# conver the type of the dates into string to tell in if someday is inside room_availability (which is a dic)
    monday_date = monday_date.strftime("%Y-%m-%d")
    tuesday_date =tuesday_date.strftime("%Y-%m-%d")
    wednessday_date =wednessday_date.strftime("%Y-%m-%d")
    thursday_date=thursday_date.strftime("%Y-%m-%d")
    friday_date=friday_date.strftime("%Y-%m-%d")
    saturday_date=saturday_date.strftime("%Y-%m-%d")
    sunday_date=sunday_date.strftime("%Y-%m-%d")


    print(monday_date)
    # fetch all the room number(we have 6 till now), room type and all bookings during this period
    cur=getCursor()
    cur.execute("""SELECT r.room_number, r.room_type, res.check_in_date, res.check_out_date
                    FROM room AS r
                    LEFT JOIN (
                        SELECT room_id, check_in_date, check_out_date
                        FROM reservation
                        WHERE check_in_date >= CURDATE() - INTERVAL WEEKDAY(CURDATE()) DAY
                        AND check_out_date <= CURDATE() + INTERVAL (6 - WEEKDAY(CURDATE())) DAY
                    ) AS res ON r.room_id = res.room_id
                    ORDER BY r.room_number, res.check_in_date;""")
    dbOutput = cur.fetchall()
    # Create a dictionary to store room availability data
    room_availability = {}

    # Iterate through dbOutput and populate the room_availability dictionary
    for booking in dbOutput:
        room_id, room_type, check_in_date, check_out_date = booking
        if room_id not in room_availability:
            room_availability[room_id] = {}

        if check_in_date is not None and check_out_date is not None:
            date_diff = (check_out_date - check_in_date).days
            for i in range(date_diff):
                occupied_date = (check_in_date + timedelta(days=i)).strftime("%Y-%m-%d")
                room_availability[room_id][occupied_date] = 'occupied'
    print(room_availability)
    return render_template("manager/manager_room_availability.html",room_availability=room_availability,dbOutput=dbOutput,today=today,monday_date=monday_date,tuesday_date=tuesday_date,wednessday_date=wednessday_date,thursday_date=thursday_date,friday_date=friday_date,saturday_date=saturday_date,sunday_date=sunday_date)


@manager_app.route("/manager/room_availability_next_week/")
def manager_room_availability_next_week():
    # Calculate the date of next week
    days_until_monday = (today.weekday() - 0) % 7
    monday_date_this_week = today - timedelta(days=days_until_monday)
    monday_date_next_week = monday_date_this_week + timedelta(days=7)
    tuesday_date_next_week = monday_date_this_week + timedelta(days=8)
    wednessday_date_next_week = monday_date_this_week + timedelta(days=9)
    thursday_date_next_week = monday_date_this_week + timedelta(days=10)
    friday_date_next_week = monday_date_this_week + timedelta(days=11)
    saturday_date_next_week = monday_date_this_week + timedelta(days=12)
    sunday_date_next_week = monday_date_this_week + timedelta(days=13)

   

# conver the type of the dates into string to tell in if someday is inside room_availability (which is a dic)
    monday_date = monday_date_next_week.strftime("%Y-%m-%d")
    tuesday_date =tuesday_date_next_week.strftime("%Y-%m-%d")
    wednessday_date =wednessday_date_next_week.strftime("%Y-%m-%d")
    thursday_date=thursday_date_next_week.strftime("%Y-%m-%d")
    friday_date=friday_date_next_week.strftime("%Y-%m-%d")
    saturday_date=saturday_date_next_week.strftime("%Y-%m-%d")
    sunday_date=sunday_date_next_week.strftime("%Y-%m-%d")


    print(monday_date)
    # fetch all the room number(we have 6 till now), room type and all bookings during this period
    cur=getCursor()
    cur.execute("""SELECT r.room_number, r.room_type, res.check_in_date, res.check_out_date
                    FROM room AS r
                    LEFT JOIN (
                        SELECT room_id, check_in_date, check_out_date
                        FROM reservation
                        WHERE check_in_date > CURDATE() + INTERVAL (6 - WEEKDAY(CURDATE())) DAY 
                        AND check_out_date <= CURDATE() + INTERVAL (13 - WEEKDAY(CURDATE())) DAY
                    ) AS res ON r.room_id = res.room_id
                    ORDER BY r.room_number, res.check_in_date;""")
    dbOutput = cur.fetchall()
    # Create a dictionary to store room availability data
    room_availability = {}

    # Iterate through dbOutput and populate the room_availability dictionary
    for booking in dbOutput:
        room_id, room_type, check_in_date, check_out_date = booking
        if room_id not in room_availability:
            room_availability[room_id] = {}

        if check_in_date is not None and check_out_date is not None:
            date_diff = (check_out_date - check_in_date).days
            for i in range(date_diff):
                occupied_date = (check_in_date + timedelta(days=i)).strftime("%Y-%m-%d")
                room_availability[room_id][occupied_date] = 'occupied'
    print(room_availability)
    return render_template("manager/manager_room_availability.html",next_week=True,room_availability=room_availability,dbOutput=dbOutput,today=today,monday_date=monday_date,tuesday_date=tuesday_date,wednessday_date=wednessday_date,thursday_date=thursday_date,friday_date=friday_date,saturday_date=saturday_date,sunday_date=sunday_date)


@manager_app.route("/manager/booking/")
def manager_booking():
    reservation_id = request.args.get('reservation_id')
    past_booking = request.args.get('past_booking')
    not_available = request.args.get('not_available')
    less_than_one_day = request.args.get('less_than_one_day')
    remind = request.args.get('remind')
    if reservation_id:
        booking_edited = True
    else:
        booking_edited = False
        print(booking_edited)
    cur=getCursor()
    query="""select re.reservation_id, re.comfirmed, re.customer_id, concat(c.customer_fname,' ',c.customer_lname) as customer_name,re.check_in_date,re.check_out_date
            from reservation as re
            join customer as c
            on re.customer_id=c.customer_id
            ORDER BY 
            CASE
                WHEN re.check_in_date > CURDATE() or re.check_in_date = CURDATE() THEN 1
                ELSE 2
            END,
            re.check_in_date;"""
    cur.execute(query)
    reservations=cur.fetchall()
    return render_template("manager/manager_booking.html",today=today,remind=remind,less_than_one_day=less_than_one_day,not_available=not_available,past_booking=past_booking,booking_edited=booking_edited,reservations=reservations,reservation_id=reservation_id)
    

@manager_app.route("/manager/booking/edit/",methods=['GET','POST'])
def manager_booking_edit():
    if request.method == 'POST':
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
        print(reservation_id,room_type_old,check_in_date_old,check_out_date_old,selected_services_old,special_needs_old)
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

                return redirect(url_for('manager.manager_booking_edit_pay',difference_price=difference_price,reservation_id=reservation_id))
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
                ##############change reservation table 
                cur1=getCursor()
                query1="""update reservation
                                set selected_services = %s,special_needs = %s, total_price = %s
                                where reservation_id = %s;"""
                parameters1=(selected_services,special_needs,total_price_new,reservation_id)
                cur1.execute(query1,parameters1)
                connection.close()  
                booking_edited = True                  
                return render_template("manager/manager_booking.html",booking_edited=booking_edited,reservation_id = reservation_id)
            else:
                # no more payment or refund, but only change reservation table
                ##############change reservation table 
                cur1=getCursor()
                query1="""update reservation
                                set selected_services = %s,special_needs = %s, total_price = %s
                                where reservation_id = %s;"""
                parameters1=(selected_services,special_needs,total_price_new,reservation_id)
                cur1.execute(query1,parameters1)
                connection.close()  
                booking_edited = True                  
                return render_template("manager/manager_booking.html",booking_edited=booking_edited,reservation_id = reservation_id)
        elif room_type != room_type_old or check_in_date_new != check_in_date_old or check_out_date_new != check_out_date_old:
            # make sure check_in_date is larger than or equal to today's date
            today = date.today()
            
            if check_in_date_new < today:
                return redirect(url_for('manager.manager_booking',past_booking = True))
            elif check_out_date_new - check_in_date_new < timedelta(days=1):
                return redirect(url_for('manager.manager_booking',less_than_one_day = True))
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

                        return redirect(url_for('manager.manager_booking_edit_pay',difference_price=difference_price,reservation_id=reservation_id))
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
                        return redirect(url_for('manager.manager_booking',booking_edited = True,reservation_id = reservation_id))
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
                        return redirect(url_for('manager.manager_booking',booking_edited = True,reservation_id = reservation_id))             
                else: 
                    return redirect(url_for('manager.manager_booking',not_available=True,reservation_id = reservation_id))
    

     
    else:
        reservation_id = request.args.get('reservation_id')
        cur=getCursor()
        query="""select re.reservation_id, re.comfirmed, r.room_number, r.room_type, re.customer_id, concat(c.customer_fname,' ',c.customer_lname) as customer_name,re.check_in_date,re.check_out_date,re.total_room_charge,re.total_price,re.selected_services,re.special_needs
                from reservation as re
                join customer as c
                on re.customer_id=c.customer_id
                join room as r
                on re.room_id = r.room_id
                where reservation_id = %s;"""
        parameter=(reservation_id,)
        cur.execute(query,parameter)
        reservations=cur.fetchall()
        return render_template("manager/manager_booking_edit.html",reservations=reservations)


@manager_app.route("/manager/booking/edit/pay/",methods=['GET','POST'])
def manager_booking_edit_pay():
    if request.method == 'POST':
        difference_price = request.form.get('difference_price')
        reservation_id = request.form.get('reservation_id')
        method = request.form.get('method')
        print(difference_price,reservation_id,method)
        # Extract date and time components
        today = date.today() ########################
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        # insert new data into payment table
        cur4 = getCursor()
        query4 ="""insert into payment (reservation_id,amount,date,time,method,payment_status)
                   values(%s,%s,%s,%s,%s,'paid');"""  
        parameters4 =(reservation_id,difference_price,today,current_time,method) 
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

        return redirect(url_for('manager.manager_booking',booking_edited=booking_edited,reservation_id=reservation_id)) 


    else:
        difference_price = request.args.get('difference_price')
        reservation_id = request.args.get('reservation_id')

        return render_template("manager/manager_booking_edit_pay.html",difference_price=difference_price,reservation_id=reservation_id)
    

@manager_app.route("/manager/check_availability/",methods=['GET','POST'])
def check_availability():
    check_in = datetime.strptime(request.form['check_in_date'], '%Y-%m-%d')
    check_in_date=check_in.date()
    check_out = datetime.strptime(request.form['check_out_date'], '%Y-%m-%d')
    check_out_date=check_out.date()
    
    # Ensure check_in_date is larger than or equal to today's date
    today = date.today()
    if check_in_date < today:
        return "Check-in date cannot be in the past."

    print(check_in_date)
    print(check_out_date)
    
    available_rooms = get_available_rooms(check_in_date, check_out_date)
    print(f"this is available_rooms:{available_rooms}")

    return render_template('manager/availability.html', available_rooms=available_rooms,check_in_date=check_in_date,check_out_date=check_out_date)

def get_available_rooms(check_in_date, check_out_date):
    cur= getCursor()
    # explain the query: check_out_date only should bigger than varieble check_out_date since the room won't be occupied if they are same day
    query="""SELECT room_type, description, price_per_night, COUNT(room_id) AS room_num, GROUP_CONCAT(room_id) AS room_ids FROM room
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

@manager_app.route("/manager/customer/")
def manager_customer():
    # fetch customer details and if this customer has booking
    cur=getCursor()
    cur.execute("""SELECT
                    c.*,
                    CASE
                        WHEN r.customer_id IS NOT NULL THEN 'YES'
                        ELSE 'NO'
                    END AS has_reservation
                FROM
                    customer c
                LEFT JOIN
                    reservation r
                ON
                    c.customer_id = r.customer_id
                group by c.customer_id;""")
    customers = cur.fetchall()
    return render_template("manager/manager_customer.html",customers=customers)

@manager_app.route("/manager/customer/profile/",methods=['GET','POST'])
def manager_customer_profile():
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

        return redirect(url_for('manager.manager_customer_profile', user_id = user_id, updated = 'yes'))
     
    else:
        user_id = request.args.get("user_id")
        cur = getCursor()
        query = """select user_id, customer_fname, customer_lname,email,phone from customer where user_id =%s;"""
        parameter = (user_id,)
        cur.execute(query,parameter)
        dbOutput=cur.fetchall()

        return render_template("manager/customer_profile.html",dbOutput=dbOutput)


@manager_app.route("/manager/customer/booking/")
def manager_customer_booking():
    user_id = request.args.get("user_id")
    reservation_id = request.args.get('reservation_id')
    past_booking = request.args.get('past_booking')
    not_available = request.args.get('not_available')
    less_than_one_day = request.args.get('less_than_one_day')
    cur=getCursor()
    cur.execute("""    select re.reservation_id, re.comfirmed, re.customer_id, concat(c.customer_fname,' ',c.customer_lname) as customer_name,re.check_in_date,re.check_out_date
            from reservation as re
            join customer as c
            on re.customer_id=c.customer_id
            where c.user_id = %s
            ORDER BY 
                CASE
                    WHEN re.comfirmed = -1 THEN 3  -- Lowest priority for comfirmed = -1
                    WHEN re.check_in_date > CURDATE() OR re.check_in_date = CURDATE() THEN 1  -- High priority for future check-in
                    ELSE 2  -- Medium priority for other cases
                END,
                re.check_in_date;""",(user_id,))
    reservations = cur.fetchall()
    return render_template("manager/customer_booking.html",reservations=reservations,reservation_id=reservation_id,past_booking=past_booking,not_available=not_available,less_than_one_day=less_than_one_day)

@manager_app.route("/manager/customer/booking/edit/",methods = ['GET','POST'])
def manager_customer_booking_edit():
    if request.method == 'POST':
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
        print(reservation_id,room_type_old,check_in_date_old,check_out_date_old,selected_services_old,special_needs_old)
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

                return redirect(url_for('manager.manager_booking_edit_pay',difference_price=difference_price,reservation_id=reservation_id))
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
                ##############change reservation table 
                cur1=getCursor()
                query1="""update reservation
                                set selected_services = %s,special_needs = %s, total_price = %s
                                where reservation_id = %s;"""
                parameters1=(selected_services,special_needs,total_price_new,reservation_id)
                cur1.execute(query1,parameters1)
                connection.close()  
                booking_edited = True                  
                return render_template("manager/customer_booking.html",booking_edited=booking_edited,reservation_id = reservation_id)
            else:
                # no more payment or refund, but only change reservation table
                ##############change reservation table 
                cur1=getCursor()
                query1="""update reservation
                                set selected_services = %s,special_needs = %s, total_price = %s
                                where reservation_id = %s;"""
                parameters1=(selected_services,special_needs,total_price_new,reservation_id)
                cur1.execute(query1,parameters1)
                connection.close()  
                booking_edited = True                  
                return render_template("manager/customer_booking.html",booking_edited=booking_edited,reservation_id = reservation_id)
        elif room_type != room_type_old or check_in_date_new != check_in_date_old or check_out_date_new != check_out_date_old:
            # make sure check_in_date is larger than or equal to today's date
            today = date.today()
            
            if check_in_date_new < today:
                return redirect(url_for('manager.manager_customer_booking',past_booking = True))
            elif check_out_date_new - check_in_date_new < timedelta(days=1):
                return redirect(url_for('manager.manager_customer_booking',less_than_one_day = True))
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

                        return redirect(url_for('manager.manager_booking_edit_pay',difference_price=difference_price,reservation_id=reservation_id))
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
                        return redirect(url_for('manager.manager_customer_booking',booking_edited = True,reservation_id = reservation_id))
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
                        return redirect(url_for('manager.manager_customer_booking',booking_edited = True,reservation_id = reservation_id))             
                else: 
                    return redirect(url_for('manager.manager_customer_booking',not_available=True,reservation_id = reservation_id))
    

     
    else:
        reservation_id = request.args.get('reservation_id')
        cur=getCursor()
        query="""select re.reservation_id, re.comfirmed, r.room_number, r.room_type, re.customer_id, concat(c.customer_fname,' ',c.customer_lname) as customer_name,re.check_in_date,re.check_out_date,re.total_room_charge,re.total_price,re.selected_services,re.special_needs
                from reservation as re
                join customer as c
                on re.customer_id=c.customer_id
                join room as r
                on re.room_id = r.room_id
                where reservation_id = %s;"""
        parameter=(reservation_id,)
        cur.execute(query,parameter)
        reservations=cur.fetchall()
        return render_template("manager/manager_customer_booking_edit.html",reservations=reservations)

@manager_app.route("/manager/staff/")
def manager_staff():
    # fetch staff details and if this customer has booking
    cur=getCursor()
    cur.execute("""SELECT * from staff;""")
    staff = cur.fetchall()
    return render_template("manager/manager_staff.html",staff=staff)

@manager_app.route("/manager/staff/profile/",methods = ['GET','POST'])
def manager_staff_profile():
    if request.method == 'POST':
        staff_profile_now = request.form
        print(staff_profile_now)
        user_id = staff_profile_now['user_id']
        staff_fname_input = staff_profile_now['staff_fname']
        staff_lname_input = staff_profile_now['staff_lname']     
        email_input = staff_profile_now['email']        
        phone_input = staff_profile_now['phone']

        staff_fname_old = staff_profile_now['staff_fname_old']
        staff_lname_old =staff_profile_now['staff_lname_old']
        email_old = staff_profile_now['email_old']
        phone_old = staff_profile_now['phone_old']
        
        if staff_fname_input:
            staff_fname = staff_fname_input
        else:
            staff_fname = staff_fname_old

        if staff_lname_input:
            staff_lname = staff_lname_input
        else:
            staff_lname = staff_lname_old
        
        if email_input:
            email = email_input
        else:
            email = email_old

        if phone_input:
            phone = phone_input
        else:
            phone = phone_old

        print(f"this is new data :{staff_fname},{staff_lname},{email},{phone},{user_id}")

        cur = getCursor()   #update the new details into the db 
        dbsql = """update staff
                   set staff_fname=%s, staff_lname=%s,email=%s,phone=%s 
                   where user_id = %s;"""
        parameters = (staff_fname,staff_lname,email,phone,user_id)
        cur.execute(dbsql,parameters) 
        connection.commit()

        return redirect(url_for('manager.manager_staff_profile', user_id = user_id, updated = 'yes'))
    else:
        user_id = request.args.get("user_id")
        cur = getCursor()
        query = """select user_id, staff_fname, staff_lname,email,phone from staff where user_id =%s;"""
        parameter = (user_id,)
        cur.execute(query,parameter)
        dbOutput=cur.fetchall()

        return render_template("manager/staff_profile.html",dbOutput=dbOutput)


@manager_app.route("/manager/schedule/",methods = ['GET','POST'])
def manager_schedule():
    edited_shift = request.args.get('edited_shift')
    # fetch all the shifts in this week
    cur=getCursor()
    cur.execute("""SELECT w.*, s.user_id, CONCAT(s.staff_fname, ' ', s.staff_lname)
                    FROM workschedule AS w
                    JOIN staff AS s ON w.staff_id = s.staff_id
                    WHERE `date` >= CURDATE() - INTERVAL WEEKDAY(CURDATE()) DAY 
                    AND `date` <= CURDATE() + INTERVAL (6 - WEEKDAY(CURDATE())) DAY
                    order by w.date; """)
    dbOutput=cur.fetchall()
    print(dbOutput)

    # Calculate the date of this week
    days_until_monday = (today.weekday() - 0) % 7
    monday_date = today - timedelta(days=days_until_monday)
    tuesday_date = monday_date + timedelta(days=1)
    wednessday_date = monday_date + timedelta(days=2)
    thursday_date = monday_date + timedelta(days=3)
    friday_date = monday_date + timedelta(days=4)
    saturday_date = monday_date + timedelta(days=5)
    sunday_date = monday_date + timedelta(days=6)

   
    return render_template("manager/schedule.html",edited_shift=edited_shift,dbOutput=dbOutput,today=today,monday_date=monday_date,tuesday_date=tuesday_date,wednessday_date=wednessday_date,thursday_date=thursday_date,friday_date=friday_date,saturday_date=saturday_date,sunday_date=sunday_date)
    
@manager_app.route("/manager/past_schedule/")
def manager_past_schedule():
    update_status=request.args.get('update_status')
    cur=getCursor()
    cur.execute("""select w.*, s.user_id,concat(s.staff_fname,' ',s.staff_lname)
                    FROM workschedule as w
                    join staff as s
                    on w.staff_id = s.staff_id
                    where w.date < %s
                    order by date DESC""",(today,))
    schedule = cur.fetchall()
    return render_template("manager/past_schedule.html",schedule=schedule,update_status=update_status)

@manager_app.route("/manager/past_schedule/update_status/",methods = ['GET','POST'])
def manager_past_schedule_update_status():
    if request.method == 'POST':
        schedule_id = request.form.get('schedule_id')
        status = request.form.get('status')
        # change the data in workschedule tabel
        cur=getCursor()
        cur.execute("""update workschedule
                       set status = %s
                       where schedule_id = %s""",(status,schedule_id))
        connection.commit()
        cur.close()
        connection.close()
        return redirect(url_for('manager.manager_past_schedule',update_status=True))
    else:
        schedule_id = request.args.get('schedule_id')
        # fetch the details of this schedule
        cur=getCursor()
        cur.execute("""select w.*, s.user_id,concat(s.staff_fname,' ',s.staff_lname)
                    FROM workschedule as w
                    join staff as s
                    on w.staff_id = s.staff_id
                    where w.schedule_id = %s""",(schedule_id,))
        dbOutput = cur.fetchall()
        return render_template("manager/past_schedule_update_status.html",dbOutput=dbOutput)


@manager_app.route("/manager/schedule/edit/",methods = ['GET','POST'])
def manager_schedule_edit():
    if request.method == 'POST':
        date=request.form.get('date')
        shift=request.form.get('shift')
        staff_id=request.form.get('staff_id')  

        print(date,shift,staff_id) 

        # fetch the schedule id
        cur=getCursor()
        cur.execute("""select schedule_id from workschedule where date = %s and shift = %s""",(date,shift))
        dbOutput = cur.fetchall()
        print(dbOutput)
        schedule_id = dbOutput[0][0]

        # update the workschedule table
        cur=getCursor()
        cur.execute("""update workschedule
                       set staff_id = %s where schedule_id = %s""",(staff_id,schedule_id,))
        connection.commit()
        cur.close()
        connection.close()
        return redirect(url_for('manager.manager_schedule',edited_shift=True))
    else:
    # fetch all the dates in the future(the shift has not occured)
        cur=getCursor()
        cur.execute("""SELECT DISTINCT `date`
                        FROM workschedule
                        WHERE `date` >= CURDATE();

                        """)
        date=cur.fetchall()
    # fetch all the staff name
        cur1=getCursor()
        cur1.execute("""select staff_id,concat(staff_fname,' ',staff_lname) from staff;""")
        staff = cur1.fetchall()
       

        return render_template("manager/schedule_edit.html",date=date,staff=staff)

@manager_app.route("/manager/next_week_schedule/")
def manager_next_week_schedule():
    # fetch the schedule details for next week
    cur=getCursor()
    cur.execute("""SELECT w.*, s.user_id, CONCAT(s.staff_fname, ' ', s.staff_lname)
                    FROM workschedule AS w
                    JOIN staff AS s ON w.staff_id = s.staff_id
                    WHERE `date` > CURDATE() + INTERVAL (6 - WEEKDAY(CURDATE())) DAY 
                    AND `date` <= CURDATE() + INTERVAL (13 - WEEKDAY(CURDATE())) DAY
                    order by w.date;""")
    dbOutput=cur.fetchall()

    # Calculate the date of next week
    days_until_monday = (today.weekday() - 0) % 7
    monday_date_this_week = today - timedelta(days=days_until_monday)
    monday_date_next_week = monday_date_this_week + timedelta(days=7)
    tuesday_date_next_week = monday_date_this_week + timedelta(days=8)
    wednessday_date_next_week = monday_date_this_week + timedelta(days=9)
    thursday_date_next_week = monday_date_this_week + timedelta(days=10)
    friday_date_next_week = monday_date_this_week + timedelta(days=11)
    saturday_date_next_week = monday_date_this_week + timedelta(days=12)
    sunday_date_next_week = monday_date_this_week + timedelta(days=13)

   
    return render_template("manager/next_week_schedule.html",dbOutput=dbOutput,today=today,monday_date_next_week=monday_date_next_week,tuesday_date_next_week=tuesday_date_next_week,
                           wednessday_date_next_week=wednessday_date_next_week,thursday_date_next_week=thursday_date_next_week,
                           friday_date_next_week=friday_date_next_week,saturday_date_next_week=saturday_date_next_week,sunday_date_next_week=sunday_date_next_week)    
    
@manager_app.route("/manager/creat_schedule/",methods = ['GET','POST'])
def manager_creat_schedule():
    if request.method == 'POST':
        monday_date_this_week = request.form.get('monday_date_this_week')
        sunday_date_this_week = request.form.get('sunday_date_this_week')
        cur=getCursor()
        cur.execute("""select staff_id, date, shift from workschedule where date >= %s and date <= %s""",(monday_date_this_week,sunday_date_this_week))
        dbOutput = cur.fetchall()

        # Define a new list to store the updated values for next week
        updatedDbOutput = []

        # Iterate through the original list and add 7 days to each date
        for item in dbOutput:
            updated_date = item[1] + timedelta(days=7)  # Add 7 days
            updated_item = (item[0], updated_date, item[2])  # Create a new tuple
            updatedDbOutput.append(updated_item)

        # add default value 'pending' to each item
        next_week_details = []
        for item in updatedDbOutput:
            updated_item = item + ('pending',)
            next_week_details.append(updated_item)
        print(next_week_details)

        # insert data into workschedule table
        cur=getCursor()
        query = "INSERT INTO workschedule (staff_id, date, shift, status) VALUES (%s, %s, %s, %s);"

        for item in next_week_details:
            cur.execute(query, item)
        connection.commit()
        connection.close()
        return redirect(url_for('manager.manager_next_week_schedule'))
    else:
        # Calculate the date of next week
        days_until_monday = (today.weekday() - 0) % 7
        monday_date_this_week = today - timedelta(days=days_until_monday)
        sunday_date_this_week = monday_date_this_week + timedelta(days=6)
        monday_date_next_week = monday_date_this_week + timedelta(days=7)
        sunday_date_next_week = monday_date_this_week + timedelta(days=13)
        return render_template("manager/creat_schedule.html",monday_date_this_week=monday_date_this_week,sunday_date_this_week=sunday_date_this_week,
                               monday_date_next_week=monday_date_next_week,sunday_date_next_week=sunday_date_next_week)

@manager_app.route("/manager/booking/remind/")
def manager_booking_remind():
    return redirect(url_for('manager.manager_booking',remind=True))