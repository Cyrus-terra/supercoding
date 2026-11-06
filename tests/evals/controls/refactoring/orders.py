import json


def summarize(orders, audit):
    result = []
    for order in orders:
        status = order['status']
        if status not in ('paid', 'refunded'):
            continue
        amount = order['amount']
        if amount is None:
            amount = 0
        audit(status, order['id'])
        result.append({'id': order['id'], 'amount': amount if status == 'paid' else -amount})
    return json.dumps(result, separators=(',', ':'), ensure_ascii=False)
