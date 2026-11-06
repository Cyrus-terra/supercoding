def import_rows(rows, save_batch, batch_size=3):
    batch = []
    for row in rows:
        batch.append(row)
        if len(batch) == batch_size:
            save_batch(batch)
            batch = []
    return len(rows)
