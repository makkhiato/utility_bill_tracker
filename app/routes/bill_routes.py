from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.utils.auth import get_current_user
from datetime import date, datetime
from app.models import Bill, Notification
from app.extensions import db

bill_bp = Blueprint('bill',__name__)

@bill_bp.route('/bills',methods=['GET'])
@jwt_required(refresh=False)
def get_bills():
    user = get_current_user()
    bills_query = Bill.query.filter_by(user_id=user.id)

    month_str = request.args.get('month')
    if month_str:
        try:
            year, month = map(int, month_str.split('-'))
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)

            bills_query = bills_query.filter(
                Bill.billing_date >= start_date,
                Bill.billing_date < end_date
            )
        except ValueError:
            return jsonify({'error': 'Invalid month format. Use YYYY-MM.'}), 400

    is_paid_str = request.args.get('is_paid')
    if is_paid_str:
        if is_paid_str.lower() == 'true':
            bills_query = bills_query.filter(Bill.status == 'paid')
        elif is_paid_str.lower() == 'false':
            bills_query = bills_query.filter(Bill.status == 'unpaid')
        else:
            return jsonify({'error': 'is_paid must be true or false'}), 400

    utility_type = request.args.get('utility_type')
    if utility_type:
        bills_query = bills_query.filter(Bill.utility_type == utility_type.lower())

    sort_by = request.args.get('sort_by')
    if sort_by:
        sort_fields = sort_by.split(',')
        sort_clauses = []

        for field in sort_fields:
            desc = field.startswith('-')
            field_name = field[1:] if desc else field

            if hasattr(Bill, field_name):
                column = getattr(Bill, field_name)
                sort_clauses.append(column.desc() if desc else column.asc())
            else:
                return jsonify({'error':f'Invalid sort_by field: {field_name}'}), 400

        if sort_clauses:
            bills_query = bills_query.order_by(*sort_clauses)


    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        if page < 1 or limit < 1:
            raise ValueError
    except ValueError:
        return jsonify({'error': 'page and limit must be positive integers'}), 400

    bills_query = bills_query.offset((page - 1) * limit).limit(limit)

    bills = bills_query.all()

    return jsonify([
        {
            'id': bill.id,
            'utility_type': bill.utility_type,
            'amount': bill.amount,
            'billing_date': bill.billing_date.isoformat(),
            'due_date': bill.due_date.isoformat(),
            'status': bill.status
        }
        for bill in bills
    ]), 200

@bill_bp.route('/bills',methods=['POST'])
@jwt_required(refresh=False)
def create_bill():
    user = get_current_user()

    data = request.get_json()

    billing_date_str = data.get('billing_date')
    due_date_str = data.get('due_date')

    billing_date = datetime.strptime(billing_date_str, '%Y-%m-%d').date()
    due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

    bill = Bill(
        user_id=user.id,
        utility_type=data.get('utility_type'),
        amount=data.get('amount'),
        billing_date=billing_date,
        due_date=due_date,
        status=data.get('status','unpaid')
    )

    db.session.add(bill)
    db.session.commit()

    message = f"A new {str(bill.utility_type).capitalize()} bill of {bill.user.settings.currency} {bill.amount:.2f} was added. Due on {bill.due_date}"
    notification = Notification(user_id=bill.user_id, message=message)

    db.session.add(notification)
    db.session.commit()

    return jsonify({'message': 'Bill added successfully', 'id':bill.id}), 201

@bill_bp.route('/bills/<int:bill_id>',methods=['GET'])
@jwt_required(refresh=False)
def get_bill(bill_id):
    user = get_current_user()
    bill = Bill.query.get_or_404(bill_id)

    if bill.user_id != user.id:
        return jsonify({'error': 'Unauthorized access to this bill'})

    return jsonify({
        'id': bill.id,
        'utility_type': bill.utility_type,
        'amount': bill.amount,
        'billing_date': bill.billing_date.isoformat(),
        'due_date': bill.due_date.isoformat(),
        'status': bill.status
    }), 200

@bill_bp.route('/bills/<int:bill_id>',methods=['PUT'])
@jwt_required(refresh=False)
def update_bill(bill_id):
    user = get_current_user()
    bill = Bill.query.filter_by(id=bill_id, user_id=user).first_or_404()
    data = request.get_json()

    bill.utility_type = data.get('utility_type', bill.utility_type)
    bill.amount = data.get('amount', bill.amount)

    if 'billing_date' in data:
        try:
            bill.billing_date = datetime.strptime(data['billing_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid billing_date format. Use YYYY-MM-DD'}), 400

    if 'due_date' in data:
        try:
            bill.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid due_date format. Use YYYY-MM-DD'}), 400

    bill.status = data.get('status', bill.status)

    db.session.commit()

    return jsonify({'message':'Bill updated successfully'}), 200

@bill_bp.route('/bills/<int:bill_id>',methods=['DELETE'])
@jwt_required(refresh=False)
def delete_bill(bill_id):
    user = get_current_user()
    bill = Bill.query.filter_by(id=bill_id, user_id=user).first_or_404()

    db.session.delete(bill)
    db.session.commit()

    return jsonify({'message':'Bill deleted successfully'}), 200
