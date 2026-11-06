import json


def summarize(orders, audit):
    result = []
    for order in orders:
        if order['status'] == 'paid':
            amount = order['amount']
            if amount is None:
                amount = 0
            audit('paid', order['id'])
            result.append({'id': order['id'], 'amount': amount})
        else:
            if order['status'] == 'refunded':
                amount = order['amount']
                if amount is None:
                    amount = 0
                audit('refunded', order['id'])
                result.append({'id': order['id'], 'amount': -amount})
    return json.dumps(result, separators=(',', ':'), ensure_ascii=False)
