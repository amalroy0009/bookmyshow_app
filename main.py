from flask import Flask,render_template,request,redirect,url_for,render_template_string,flash
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.secret_key = 'my_secret_key'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///bookmyshow.sqlite3'
db=SQLAlchemy(app)

class Venuemgmt(db.Model):
  id=db.Column(db.Integer(),primary_key=True)
  venue_name=db.Column(db.String(length=30),nullable=False,unique=True)
  place=db.Column(db.String(length=20),nullable=False)
  location=db.Column(db.String(length=20),nullable=False)
  capacity=db.Column(db.Integer(),nullable=False)
  shows=db.relationship('Showmgmt',secondary='association', backref='venues')
  
 


  def __repr__(self):
    return f'{self.venue_name}'
  

class Showmgmt(db.Model):
  id=db.Column(db.Integer(),primary_key=True)
  show_name=db.Column(db.String(length=30),nullable=False)
  rating=db.Column(db.Integer(),nullable=False)
  tags=db.Column(db.String(length=30),nullable=False)
  timing=db.Column(db.String(length=30),nullable=False,unique=True)
  ticket_price=db.Column(db.Integer(),nullable=False)
  seats=db.Column(db.Integer(),nullable=False)

 


  def __repr__(self):
    return f'{self.show_name}'
class Association(db.Model):
  venue_id=db.Column(db.Integer(),db.ForeignKey('venuemgmt.id'),primary_key=True)
  show_id=db.Column(db.Integer(),db.ForeignKey('showmgmt.id'),primary_key=True)  
class Registeruser(db.Model):
  id=db.Column(db.Integer(),primary_key=True)
  name=db.Column(db.String(length=30),nullable=False)  
  username=db.Column(db.String(length=30),nullable=False,unique=True)
  password=db.Column(db.String(length=12),nullable=False)
  def __repr__(self):
    return  f'{self.name}'

class Booking(db.Model):
  booking_id=db.Column(db.Integer(),primary_key=True)
  username=db.Column(db.String(length=20),nullable=False)
  show_name=db.Column(db.String(length=25),nullable=False)
  venue_name=db.Column(db.String(length=25),nullable=False)
  tickets=db.Column(db.Integer(),nullable=False)
  timing=db.Column(db.String(length=20),nullable=False)
  price=db.Column(db.Integer(),nullable=False)
  def __repr__(self):
    return  f'{self.username}'
db.create_all()
    
@app.route('/venuemgmt',methods=['GET','POST'])
def userlogin():
  
  if request.method=="POST":
    venue=request.form['venue']
    place=request.form['place']
    location=request.form['location']
    capacity=request.form['capacity']
    mydata=Venuemgmt(venue_name=venue,place=place,location=location,capacity=capacity)

    db.session.add(mydata)
    db.session.commit()
    return redirect("/venuemgmt")
  data=Venuemgmt.query.all()
  return render_template('adminhome.html',data=data)


@app.route('/<venuename>/showsmgmt',methods=['POST','GET'])
def showsmgmt(venuename):
  
  
  s1=Venuemgmt.query.filter_by(venue_name=venuename).first()
   
  if request.method=="POST":
    show=request.form['show']
    rating=request.form['rating']
    tags=request.form['tags']
    timing=request.form['timing']
    
    ticket_price=request.form['ticket_price']
    seats=s1.capacity
    myshow=Showmgmt(show_name=show,rating=rating,tags=tags,timing=timing,ticket_price=ticket_price,seats=seats)
    
    

    db.session.add(myshow)
    s1.shows.append(myshow)
    db.session.commit()
    
    return redirect(f'/{venuename}/showsmgmt')
    
      
  shows=s1.shows
  

  
  return render_template('adminshows.html',shows=shows,venuename=venuename)

@app.route('/register',methods=['GET','POST'])  
def registerpage():
  if request.method=="POST":
    name=request.form['name']
    username=request.form['username']
    password=request.form['password']
    myreg=Registeruser(name=name,username=username,password=password)
    db.session.add(myreg)
    db.session.commit()
    return redirect(f"/")
  return render_template('register.html')


@app.route('/',methods=['GET','POST'])
def loginpage():
  L=[]
  for i in Registeruser.query.all():
    L.append(i.username)
  if request.method=="POST":
    username=request.form['username']
    password=request.form['password']
    if username in L:
      return redirect(f'/user/{username}')
    else:
      return "Username not found,Please Register and login"
  return render_template('login.html') 



@app.route('/user/<username>',methods=['POST','GET'])
def userpage(username):
  l=[]
  
  
  for i in Venuemgmt.query.all():
    l.append(i.place)
  if request.method=="POST":
      k=request.form['city']
      city=Venuemgmt.query.filter_by(place=k).all()
      
      return render_template('venues.html',city=city,username=username)
  
  return render_template('userpage.html',cities=l,username=username )

@app.route('/<venuename>/<username>/shows',methods=['GET','POST'])
def shows(venuename,username):
  l=[]
  for i in Showmgmt.query.all():
    l.append(i.tags)
  if request.method=="POST":
      tags=request.form['city']
      tags=Showmgmt.query.filter_by(tags=tags).all()
      
      return render_template('shows.html',tags=tags,username=username)
  s1=Venuemgmt.query.filter_by(venue_name=venuename).first()
  
  return render_template('shows.html',shows=s1.shows,username=username,venuename=venuename,l=l)

@app.route('/<username>/<showname>/<timing>/<venuename>/booking',methods=['GET','POST'])
def booking(showname,username,venuename,timing):
  s1=Showmgmt.query.filter_by(show_name=showname,timing=timing).first()
  seats=s1.seats
  rate=s1.ticket_price
  if request.method=="POST":
    tickets=request.form['tickets']
    total=int(rate)*int(tickets)
    
    if (int(tickets)>s1.seats):
      return render_template_string("<center><h2>Sorry the number of tickets booked are more than the available seats</h2></center>")
    
    else:
      book=Booking(username=username,show_name=showname,venue_name=venuename,tickets=tickets,timing=timing,price=total)
      s1.seats=s1.seats-int(tickets)
      db.session.add(book)
      db.session.commit()
    if (s1.seats>=0.75*seats):
      s1.ticket_price=s1.ticket_price-100
      db.session.commit()
    elif(s1.seats<=0.3*seats):
      s1.ticket_price=s1.ticket_price+200  
      db.session.commit()
    else:
      s1.ticket_price=s1.ticket_price
      db.session.commit()    
    
      
    return redirect(f'/{venuename}/{username}/shows')
  
  return render_template('bookings.html',showname=showname,username=username,venuename=venuename,seats=seats,timing=timing,
                         rate=rate)

@app.route('/<showname>/<timing>/<venuename>/deleteshow',methods=['GET','POST'])
def deleteshow(showname,timing,venuename):
  s1=Showmgmt.query.filter_by(show_name=showname,timing=timing).first()
  s2=Booking.query.filter_by(show_name=s1.show_name,timing=s1.timing).first()
  db.session.delete(s2)
  
  db.session.delete(s1)
  db.session.commit()
  return redirect(f'/{venuename}/showsmgmt')

@app.route('/update/<id>/<venuename>',methods=['GET','POST'])
def updateshow(id,venuename):
  s1=Showmgmt.query.get(id)
  if request.method=="POST":
    show=request.form['show']
    rating=request.form['rating']
    tags=request.form['tags']
    ticketprice=request.form['ticketprice']
    timing=request.form['timing']
    s1.show_name=show
    s1.timing=timing
    s1.rating=int(rating)
    s1.tags=tags
    s1.ticket_price=int(ticketprice)
    db.session.commit()
    return redirect(f'/{venuename}/showsmgmt')
  return render_template('editshows.html',id=id,venuename=venuename,k=s1)
@app.route('/admin',methods=['POST','GET'])
def admin():
  if request.method=="POST":
    admin=request.form['username']
    if (admin=="amalroy717"):
      return redirect('/venuemgmt')
    else:
      return render_template_string("<center><h1>WRONG ADMIN</h1></center>")
  return render_template('adminlogin.html')

@app.route('/<username>/mybookings')
def mybookings(username):
  s1=Booking.query.filter_by(username=username)
  return render_template('mybookings.html',booking=s1,username=username)

@app.route('/<id>/cancelbooking',methods=['GET','POST'])
def cancelbooking(id):
  s1=Booking.query.get(id)
  show=s1.show_name
  time=s1.timing

  username=s1.username
  s2=Showmgmt.query.filter_by(show_name=show,timing=time).first()
  s2.seats=s1.tickets+s2.seats
  db.session.delete(s1)

  db.session.commit()
  return redirect(f'/{username}/mybookings')  

@app.route('/<id>/deletevenue',methods=['GET','POST'])
def deletevenue(id):
  s1=Venuemgmt.query.get(id)
  s2=Booking.query.filter_by(venue_name=s1.venue_name).all()
  for i in s2:
    db.session.delete(i)
  db.session.delete(s1)
  db.session.commit()
  return redirect('/venuemgmt')

@app.route('/<id>/updatevenue',methods=['GET','POST'])
def updatevenue(id):
  s1=Venuemgmt.query.get(id)
  if request.method=="POST":
    venue=request.form['venue']
    place=request.form['place']
    location=request.form['location']
    capacity=request.form['capacity']
    
    s1.venue_name=venue
    s1.place=place
    s1.location=location
    s1.capacity=capacity
    for  i in s1.shows:
      i.seats=capacity
    
    db.session.commit()
    return redirect('/venuemgmt')
  return render_template('updatevenue.html',k=s1,id=id)





    
      
      
  

  
  
    


if __name__ == "__main__":

  app.run(host='0.0.0.0',port=5000,debug=True)