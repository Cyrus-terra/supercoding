import unittest
from listing import Listings


class ReviewChecks(unittest.TestCase):
    def setUp(self):
        self.now = 0
        self.calls = []
        def fetch(tenant, status):
            self.calls.append((tenant, status))
            return [tenant, status, len(self.calls)]
        self.subject = Listings(fetch, lambda: self.now)

    def test_filters_do_not_collide(self):
        self.subject.list_orders('a', 'paid', {'orders:read'})
        self.assertEqual(self.subject.list_orders('a', 'pending', {'orders:read'})[:2], ['a', 'pending'])

    def test_cache_expires_and_reuses_within_ttl(self):
        first = self.subject.list_orders('a', 'paid', {'orders:read'})
        self.now = 4
        self.assertEqual(self.subject.list_orders('a', 'paid', {'orders:read'}), first)
        self.now = 5
        self.assertNotEqual(self.subject.list_orders('a', 'paid', {'orders:read'}), first)
        self.assertEqual(len(self.calls), 2)

    def test_permissions_and_tenant_boundaries(self):
        self.subject.list_orders('a', 'paid', {'orders:read'})
        with self.assertRaises(PermissionError):
            self.subject.list_orders('a', 'paid', set())
        with self.assertRaises(PermissionError):
            self.subject.export_orders('a', 'paid', {'orders:read'})
        self.assertEqual(self.subject.export_orders('b', 'paid', {'orders:export'})[:2], ['b', 'paid'])
        self.assertEqual(self.subject.list_orders('b', 'paid', {'orders:read'})[:2], ['b', 'paid'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
