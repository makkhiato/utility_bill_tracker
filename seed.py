from dotenv import load_dotenv
load_dotenv()
from app import create_app
from app.extensions import db
from app.models import User, Bill, UserSettings
from datetime import date, timedelta
import random
import os
print("ENV VAR DATABASE_URL =", os.getenv('DATABASE_URL'))

app = create_app()

with app.app_context():
    Bill.query.delete()
    UserSettings.query.delete()
    User.query.delete()
    db.session.commit()

    user1 = User(name='Alice',email='alice@example.com')
    user1.set_password('alice123')

    user2 = User(name='Bob',email='bob@example.com')
    user2.set_password('bob123')

    db.session.add_all([user1, user2])
    db.session.commit()

    users = [user1, user2]
    utility_types = ['electricity', 'water', 'internet']

    base_date = date(2025, 1, 1)

    for user in users:
        for utility in utility_types:
            for i in range(6):
                billing_date = base_date + timedelta(days=30 * i)
                due_date = billing_date + timedelta(days=10)
                amount = round(random.uniform(500, 2000), 2)
                status = 'paid' if i < 4 else 'unpaid'

                bill = Bill(
                    user_id=user.id,
                    utility_type=utility,
                    amount=amount,
                    billing_date=billing_date,
                    due_date=due_date,
                    status=status
                )
                db.session.add(bill)

    db.session.commit()
    print('Database seeded successfully')