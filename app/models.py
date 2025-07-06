from .extensions import db
from datetime import datetime,timezone
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),nullable=False)
    email = db.Column(db.String(100),nullable=False)
    password_hash = db.Column(db.String(255),nullable=False)
    created_at = db.Column(db.DateTime,default=lambda: datetime.now(timezone.utc))

    bills = db.relationship('Bill',backref='user',cascade='all, delete-orphan')
    settings = db.relationship('UserSettings',uselist=False,backref='user',cascade='all, delete-orphan')

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return f'<User {self.id} - {self.name}>'

class Bill(db.Model):
    __tablename__ = 'bills'

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    utility_type = db.Column(db.String(50),nullable=False)
    amount = db.Column(db.Float,nullable=False)
    billing_date = db.Column(db.Date,nullable=False)
    due_date = db.Column(db.Date,nullable=False)
    status = db.Column(db.String(20),default='unpaid')
    created_at = db.Column(db.DateTime,default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'Bill: {self.utility_type} - PHP {self.amount} for User {self.user_id}'

class UserSettings(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    currency = db.Column(db.String(10),default='PHP')
    dark_mode = db.Column(db.Boolean,default=False)

    def __repr__(self):
        return f'<Settings for User {self.user_id}>'