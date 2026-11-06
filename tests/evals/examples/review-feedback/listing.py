class Listings:
    def __init__(self, fetch, clock, ttl=5):
        self.fetch = fetch
        self.clock = clock
        self.ttl = ttl
        self.cache = {}

    def list_orders(self, tenant, status, permissions):
        if 'orders:read' not in permissions:
            raise PermissionError('orders:read required')
        key = tenant
        now = self.clock()
        if key not in self.cache or now - self.cache[key][0] >= self.ttl:
            self.cache[key] = (now, self.fetch(tenant, status))
        return self.cache[key][1]

    def export_orders(self, tenant, status, permissions):
        if 'orders:export' not in permissions:
            raise PermissionError('orders:export required')
        return self.fetch(tenant, status)
