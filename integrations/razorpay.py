import razorpay
import os
RAZORPAY_API_KEY = os.getenv('RAZORPAY_API_KEY')
RAZORPAY_API_SECRET = os.getenv('RAZORPAY_API_SECRET')

def create_payment_order(amount):
    client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET))
    payment_order_info = client.order.create({"amount": amount, "currency": "INR", "payment_capture": 1})
    return payment_order_info

def verify_payment(amount,razorpay_signature, razorpay_order_id, razorpay_payment_id):
    try:
        client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET))
        print("HERE WE GO" + razorpay_signature, razorpay_order_id, razorpay_payment_id)
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        client.utility.verify_payment_signature(params_dict)
        return {'success': True}
    except Exception as e:
        raise e