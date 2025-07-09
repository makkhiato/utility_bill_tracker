from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from collections import defaultdict
from app.utils.auth import get_current_user
from app.models import Bill

analytics_bp = Blueprint('analytics',__name__)

@analytics_bp.route('/analytics',methods=['GET'])
@jwt_required(refresh=False, locations=['cookies'])
def get_analytics():
    user = get_current_user()

    start_month = request.args.get('start_month')
    utility_type = request.args.get('utility_type')

    if not start_month:
        return jsonify({'error':'Missing start_month parameter'}), 400

    try:
        start_date = datetime.strptime(start_month, '%Y-%m').date()
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
            'total': round(totals.get(month, 0), 2)
        })

    return jsonify(data), 200

@analytics_bp.route('/analytics/predict',methods=['GET'])
@jwt_required(refresh=False, locations=['cookies'])
def predict_next_month():
    user = get_current_user()

    months = int(request.args.get('months', 6))
    utility_type_filter = request.args.get('utility_type')

    query = Bill.query.filter(Bill.user_id == user.id)

    if utility_type_filter:
        query = query.filter_by(utility_type=utility_type_filter)

    bills = query.order_by(Bill.billing_date).all()

    grouped = defaultdict(lambda: defaultdict(float))
    for bill in bills:
        month = bill.billing_date.strftime('%Y-%m')
        grouped[bill.utility_type][month] += bill.amount

    predictions = []

    for utility_type, month_data in grouped.items():
        sorted_months = sorted(month_data.keys())[-months:]
        values = [month_data[m] for m in sorted_months]

        if len(values) < 2:
            continue

        alpha = 0.5
        smoothed = values[0]

        for val in values[1:]:
            smoothed = alpha * val + (1 - alpha) * smoothed

        predictions.append({
            'utility_type': utility_type,
            'predicted': round(smoothed, 2)
        })

    if utility_type_filter:
        result = next((p for p in predictions if p['utility_type'] == utility_type_filter), None)
        return jsonify(result or {'utility_type': utility_type_filter, 'predicted': 0.0})

    return jsonify(predictions), 200

@analytics_bp.route('/analytics/breakdown',methods=['GET'])
@jwt_required(refresh=False, locations=['cookies'])
def unpaid_breakdown():
    user = get_current_user()

    bills = Bill.query.filter_by(user_id=user.id, status='unpaid').all()

    utility_totals = defaultdict(float)
    total = 0.0
    for bill in bills:
        utility_totals[bill.utility_type] += bill.amount
        total += bill.amount

    breakdown = []
    for utility_type, amount in utility_totals.items():
        breakdown.append({
            'utility_type': utility_type,
            'amount': round(amount, 2),
            'percentage': round((amount / total) * 100, 2) if total > 0 else 0
        })

    return jsonify({
        'total': round(total, 2),
        'breakdown': breakdown
    }), 200