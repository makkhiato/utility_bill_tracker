from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from collections import defaultdict
from app.models import Bill, User

analytics_bp = Blueprint('analytics',__name__)

@analytics_bp.route('/analytics',methods=['GET'])
def get_analytics():
    user = User.query.first() #TEMP: replace with auth user later

    start_month = request.args.get('start_month')
    utility_type = request.args.get('utility_type')

    if not start_month:
        return jsonify({'error':'Missing start_month parameter'}), 400

    try:
        start_date = datetime.strptime(start_month, '%Y-%m')
    except ValueError:
        return jsonify({'error':'Invalid start_month format (use YYYY-MM)'}), 400

    month_labels = []
    current = start_date
    for _ in range(6):
        month_labels.append(current.strftime('%Y-%m'))
        current = current.replace(day=28) + timedelta(days=4)
        current = current.replace(day=1)

    end_date = current

    query = Bill.query.filter(
        Bill.user_id == user.id,
        Bill.billing_date >= start_date,
        Bill.billing_date < end_date
    )

    if utility_type:
        query = query.filter_by(utility_type=utility_type)

    bills = query.all()

    totals = defaultdict(float)
    for bill in bills:
        month_key = bill.billing_date.strftime('%Y-%m')
        totals[month_key] += bill.amount

    data = []
    for month in month_labels:
        data.append({
            'month': month,
            'total ': round(totals.get(month, 0), 2)
        })

    return jsonify(data), 200