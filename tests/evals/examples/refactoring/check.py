import unittest
from orders import summarize


class RefactoringChecks(unittest.TestCase):
    def test_serialization_order_and_side_effects(self):
        events = []
        rows = [
            {'id': '零', 'status': 'paid', 'amount': 0},
            {'id': 'ignored', 'status': 'pending'},
            {'id': 'null', 'status': 'paid', 'amount': None},
            {'id': 'refund', 'status': 'refunded', 'amount': 12},
        ]
        self.assertEqual(summarize(rows, lambda *args: events.append(args)),
                         '[{"id":"零","amount":0},{"id":"null","amount":0},{"id":"refund","amount":-12}]')
        self.assertEqual(events, [('paid', '零'), ('paid', 'null'), ('refunded', 'refund')])
        self.assertEqual(summarize([], lambda *args: self.fail('unexpected audit')), '[]')

    def test_errors_preserve_prior_side_effects(self):
        events = []
        with self.assertRaises(KeyError):
            summarize([{'id': 1, 'status': 'paid', 'amount': 2}, {'status': 'paid'}],
                      lambda *args: events.append(args))
        self.assertEqual(events, [('paid', 1)])

    def test_audit_failure_propagates(self):
        def fail(*args):
            raise OSError('audit unavailable')
        with self.assertRaisesRegex(OSError, 'audit unavailable'):
            summarize([{'id': 1, 'status': 'paid', 'amount': 0}], fail)


if __name__ == '__main__':
    unittest.main(verbosity=2)
