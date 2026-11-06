def import_rows(rows, save_batch, batch_size=3):
    batch = []
    count = 0
    for row in rows:
        batch.append(row)
        count += 1
        if len(batch) == batch_size:
            save_batch(batch)
            batch = []
    if batch:
        save_batch(batch)
    return count
