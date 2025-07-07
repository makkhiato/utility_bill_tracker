from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import numpy as np
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

@analytics_bp.route('/analytics/predict',methods=['GET'])
def predict_next_month():
    user = User.query.first() # TEMP: replace with auth later

    months = int(request.args.get('months', 6))
    utility_type_filter = request.args.get('utility_type')

    end_date = datetime.now(timezone.utc).replace(day=1)
    start_date = end_date - relativedelta(months=months)

    query = Bill.query.filter(
        Bill.user_id == user.id,
        Bill.billing_date >= start_date,
        Bill.billing_date < end_date
    )

    if utility_type_filter:
        query = query.filter_by(utility_type=utility_type_filter)

    bills = query.all()

    grouped = defaultdict(lambda: defaultdict(float))
    for bill in bills:
        month = bill.billing_date.strftime('%Y-%m')
        grouped[bill.utility_type][month] += bill.amount

    predictions = []

    for utility_type, month_data in grouped.items():
        sorted_months = sorted(month_data.keys())

        x = np.arange(len(sorted_months))
        y = np.array([month_data[m] for m in sorted_months])

        if len(x) < 2:
            continue

        a, b = np.polyfit(x, y, 1)

        next_x = len(x)
        predicted = round(float(a * next_x + b), 2)

        predictions.append({
            'utility_type': utility_type,
            'predicted': max(predicted, 0.0)
        })

    if utility_type_filter:
        result = next((p for p in predictions if p['utility_type'] == utility_type_filter), None)
        return jsonify(result or {'utility_type': utility_type_filter, 'predicted': 0.0})

    return jsonify(predictions), 200