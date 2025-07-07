from flask import Blueprint, request, jsonify
from datetime import datetime
from app.models import Bill, User
from app.extensions import db

bill_bp = Blueprint('bill',__name__)

@bill_bp.route('/bills',methods=['GET'])
def get_bills():
    user = User.query.first() #TEMP: replace with auth later
    bills = Bill.query.filter_by(user_id=user.id).all()

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
def create_bill():
    user = User.query.first() #TEMP

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

    return jsonify({'message': 'Bill added successfully', 'id':bill.id}), 201

@bill_bp.route('/bills/<int:bill_id>',methods=['GET'])
def get_bill(bill_id):
    bill = Bill.query.get_or_404(bill_id)

    return jsonify({
        'id': bill.id,
        'utility_type': bill.utility_type,
        'amount': bill.amount,
        'billing_date': bill.billing_date.isoformat(),
        'due_date': bill.due_date.isoformat(),
        'status': bill.status
    }), 200

@bill_bp.route('/bills/<int:bill_id>',methods=['PUT'])
def update_bill(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    data = request.get_json()

    bill.utility_type = data.get('utility_type', bill.utility_type)
    bill.amount = data.get('amount', bill.amount)
    # bill.billing_date = data.get('billing_date', bill.billing_date)
    # bill.due_date = data.get('due_date', bill.due_date)

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
def delete_bill(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    db.session.delete(bill)
    db.session.commit()
    return jsonify({'message':'Bill deleted successfully'}), 200
