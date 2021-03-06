from datetime import datetime
from itsdangerous import URLSafeSerializer as Serializer
from app import app,db,login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique =True, nullable = False)
    profile_pic = db.Column(db.String(20), nullable = False, default = 'avatar.png')
    password = db.Column(db.String(100), nullable = False)
    admin = db.Column(db.Boolean, nullable = False, default = False)
    jobs_posted = db.relationship('Jobs', backref = 'author', lazy = True)
    products_posted = db.relationship('Products', backref = 'owner', lazy = True)
    docs = db.relationship('Docs', backref = 'uploader', lazy = True)
    proposals = db.relationship('Proposals', backref = 'job_seeker', lazy = True)
    phone_number = db.Column(db.String(50), nullable = False)
    instagram = db.Column(db.String(50))
    facebook = db.Column(db.String(50))
    twitter = db.Column(db.String(50))

    def get_reset_token(self,expires_sec=3600):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Users.query.get(user_id)


    def __repr__(self):
        return str(self.username) + str(self.email) + str(self.profile_pic)

association_table = db.Table('association_table',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('job_id', db.Integer, db.ForeignKey('jobs.id')),
)


class Jobs(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable = False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('jobschedule.id'), nullable = False)
    job_responsibilities = db.Column(db.Text, nullable = False)
    location_id = db.Column(db.Integer, db.ForeignKey('counties.id'), nullable = False)
    education = db.Column(db.String(200))
    experience = db.Column(db.String(500))
    additional_req = db.Column(db.String(500))
    compensation = db.Column(db.String(500))
    salary = db.Column(db.String(100), nullable = False)
    active = db.Column(db.Boolean, nullable = False, default = True)
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow) 
    proposals = db.relationship('Proposals', backref = 'its_job', lazy = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    users = db.relationship("Users", secondary=association_table, backref=db.backref('saved_jobs', lazy= 'dynamic'))

    def __repr__(self):
        return f"Job('{self.id}','{self.title}','{self.date_posted}')"


class Proposals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(200), nullable = False)
    lastname = db.Column(db.String(200), nullable = False)
    phone = db.Column(db.String(200), nullable = False)
    email = db.Column(db.String(200))
    docs = db.relationship('Docs', backref = 'proposal', lazy = True)
    message = db.Column(db.String(500), nullable = False)
    date_initiated = db.Column(db.DateTime, nullable = False, default = datetime.utcnow) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable = False)

    def __repr__(self):
        return f"Proposal('{self.id}','{self.firstname}','{self.phone}','{self.message}')"

class Docs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    docname = db.Column(db.String(200), nullable = False,unique=True)
    date_uploaded = db.Column(db.DateTime, nullable = False, default = datetime.utcnow) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposals.id'))

    def __repr__(self):
        return f"Doc('{self.id}','{self.docname}')"



class Counties(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable = False,unique=True)
    jobs = db.relationship('Jobs', backref = 'location', lazy = True)
    products = db.relationship('Products', backref = 'product_location', lazy = True)
    def __repr__(self):
        return f"County('{self.id}','{self.name}')"


class Jobschedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedulename = db.Column(db.String(200), nullable = False,unique=True)
    jobs = db.relationship('Jobs', backref = 'schedule', lazy = True)
    def __repr__(self):
        return f"JobSchedule('{self.id}','{self.schedulename}')"


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoryname = db.Column(db.String(200), nullable = False,unique=True)
    jobs = db.relationship('Jobs', backref = 'category', lazy = True)

    def __repr__(self):
        return f"Category('{self.id}','{self.categoryname}')"


class Productcategories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    productcategoryname = db.Column(db.String(200), nullable = False,unique=True)
    products = db.relationship('Products', backref = 'product_category', lazy = True)

    def __repr__(self):
        return f"Productcategory('{self.id}','{self.productcategoryname}')"

class Jobalerts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable = False)
    category = db.Column(db.String(200), nullable = False)
    schedule = db.Column(db.String(200), nullable = False)
    county = db.Column(db.String(200), nullable = False)

    def __repr__(self):
        return f"Jobalert('{self.id}','{self.email}')"

class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(200), nullable = False)
    receiver = db.Column(db.String(200), nullable = False)
    message = db.Column(db.String(200), nullable = False)
    read = db.Column(db.Boolean, nullable = False, default = False)
    date_sent = db.Column(db.DateTime, nullable = False, default = datetime.utcnow) 

    def __repr__(self):
        return f"Notification('{self.id}')"

favourites = db.Table('favourites',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id')),
)
class Products(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    category_id = db.Column(db.Integer, db.ForeignKey('productcategories.id'), nullable = False)
    location_id = db.Column(db.Integer, db.ForeignKey('counties.id'), nullable = False)
    additional_details = db.Column(db.String(500))
    price = db.Column(db.String(100), nullable = False)
    images = db.relationship('Productimg', backref = 'product', lazy = True)
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    users = db.relationship("Users", secondary=favourites, backref=db.backref('saved_products', lazy= 'dynamic'))

    def __repr__(self):
        return f"Product('{self.id}','{self.title}','{self.date_posted}')"

class Productalerts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable = False)
    category = db.Column(db.String(200), nullable = False)
    county = db.Column(db.String(200), nullable = False)

    def __repr__(self):
        return f"Jobalert('{self.id}','{self.email}')"


class Productimg(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable = False)
    date_uploaded = db.Column(db.DateTime, nullable = False, default = datetime.utcnow) 

    def __repr__(self):
        return f"Productimg('{self.id}','{self.name}','{self.date_uploaded}')"
