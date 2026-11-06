import csv
from collections import deque
from concurrent.futures import ThreadPoolExecutor


def process_csv(source, destination, transform, workers=4, timeout=5):
    with open(source, newline='', encoding='utf-8') as incoming, \
            open(destination, 'w', newline='', encoding='utf-8') as outgoing, \
            ThreadPoolExecutor(max_workers=workers) as pool:
        reader = iter(csv.DictReader(incoming))
        writer = csv.DictWriter(outgoing, fieldnames=['id', 'value'])
        writer.writeheader()
        pending = deque()
        for _ in range(workers):
            row = next(reader, None)
            if row is None:
                break
            pending.append(pool.submit(transform, row, timeout=timeout))
        while pending:
            writer.writerow(pending.popleft().result())
            row = next(reader, None)
            if row is not None:
                pending.append(pool.submit(transform, row, timeout=timeout))
