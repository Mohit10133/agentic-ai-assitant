import sys
sys.path.insert(0, 'd:\\Valtech\\GCP\\ecommerce-assistant')
from app.tools.ecommerce import handle_ecommerce

queries = [
    'Show available coupons',
    'Check coupon SAVE20',
    'What coupons are available for me?',
    'Show details for coupon FESTIVE10',
    'What is the status of my order 12345?',
    'Show details of order 12345',
    'When will my order be delivered?',
    'Cancel order 10234',
    'Change delivery address for order 12345',
    'Update quantity for item in order 12345',
    'Register a new user with email test@example.com',
    'Create a new account',
    'Register me with name John and email john@example.com',
    'Show my profile details',
    'What is my registered address?',
    'Show my order history',
    'How can I register a new account?',
    'How do I cancel my order?',
    'How can I apply a coupon?'
]

failed = []
for query in queries:
    result = handle_ecommerce(query, 'user1')
    intent = result['intent']
    status = 'PASS' if intent != 'unknown' else 'FAIL'
    if status == 'FAIL':
        failed.append(query)
    print('Query: ' + query)
    print('Intent: ' + str(intent))
    print('Status: ' + status)
    print('---')

if failed:
    print('\n\nFAILED QUERIES:')
    for q in failed:
        print('  - ' + q)
else:
    print('\n\nALL QUERIES PASSED!')
