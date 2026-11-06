import csv
from concurrent.futures import ThreadPoolExecutor


def process_csv(source, destination, transform, workers=4, timeout=5):
    with open(source, newline='', encoding='utf-8') as incoming:
        rows = list(csv.DictReader(incoming))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(transform, row, timeout=timeout) for row in rows]
        results = [future.result() for future in futures]
    with open(destination, 'w', newline='', encoding='utf-8') as outgoing:
        writer = csv.DictWriter(outgoing, fieldnames=['id', 'value'])
        writer.writeheader()
        writer.writerows(results)
