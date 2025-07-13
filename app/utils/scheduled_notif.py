from datetime import date, timedelta
from app.extensions import db
from app.models import Bill, Notification

def notify_upcoming_bills():
    today = date.today()
    upcoming_due_date = today + timedelta(days=7)

    bills = Bill.query.filter(
        Bill.due_date == upcoming_due_date,
        Bill.status == 'unpaid'
    ).all()

    for bill in bills:
        user = bill.user
        message = f'Your {bill.utility_type} bill of {user.settings.currency} {bill.amount:.2f} is due on {bill.due_date}.'
        notification = Notification(user_id=user.id, message=message)
        db.session.add(notification)

    db.session.commit()
