import csv
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

import process_csv as subject


class StreamingChecks(unittest.TestCase):
    def test_streaming_order_bounds_and_timeout(self):
        workers = 3
        consumed = completed = active = peak = emitted = 0
        lock = threading.Lock()
        later_finished = threading.Event()
        completion_order = []
        real_reader = csv.DictReader
        real_writer = csv.DictWriter

        class TrackingWriter:
            def __init__(self, *args, **kwargs):
                self.writer = real_writer(*args, **kwargs)

            def writeheader(self):
                return self.writer.writeheader()

            def writerow(self, row):
                nonlocal emitted
                result = self.writer.writerow(row)
                with lock:
                    emitted += 1
                return result

            def writerows(self, rows):
                for row in rows:
                    self.writerow(row)

        def guarded_reader(handle):
            nonlocal consumed
            for row in real_reader(handle):
                with lock:
                    consumed += 1
                    if consumed - emitted > workers:
                        raise AssertionError('Input consumed beyond the output window')
                yield row

        def transform(row, *, timeout):
            nonlocal completed, active, peak
            self.assertEqual(timeout, 2)
            with lock:
                active += 1
                peak = max(peak, active)
            try:
                if row['id'] == '0':
                    self.assertTrue(later_finished.wait(5), 'later row never completed')
                with lock:
                    completion_order.append(row['id'])
                if row['id'] == '1':
                    later_finished.set()
                return {'id': row['id'], 'value': str(int(row['value']) * 2)}
            finally:
                with lock:
                    completed += 1
                    active -= 1

        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'input.csv'
            destination = Path(directory) / 'output.csv'
            with source.open('w', newline='', encoding='utf-8') as handle:
                writer = csv.writer(handle)
                writer.writerow(['id', 'value'])
                writer.writerows((index, index) for index in range(1000))
            with patch.object(subject.csv, 'DictReader', guarded_reader), patch.object(subject.csv, 'DictWriter', TrackingWriter):
                subject.process_csv(source, destination, transform, workers=workers, timeout=2)
            with destination.open(newline='', encoding='utf-8') as handle:
                output = list(real_reader(handle))
            self.assertEqual(output, [{'id': str(i), 'value': str(i * 2)} for i in range(1000)])
        self.assertLess(completion_order.index('1'), completion_order.index('0'))
        self.assertLessEqual(peak, workers)
        self.assertEqual(completed, 1000)
        self.assertEqual(active, 0)

    def test_failure_propagates_and_files_close(self):
        handles = []
        real_open = open

        def track_open(*args, **kwargs):
            handle = real_open(*args, **kwargs)
            handles.append(handle)
            return handle

        def fail(row, *, timeout):
            raise TimeoutError('simulated downstream timeout')

        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'input.csv'
            source.write_text('id,value\n1,2\n', encoding='utf-8')
            with patch.object(subject, 'open', track_open, create=True):
                with self.assertRaises(TimeoutError):
                    subject.process_csv(source, Path(directory) / 'output.csv', fail)
        self.assertTrue(handles)
        self.assertTrue(all(handle.closed for handle in handles))


if __name__ == '__main__':
    unittest.main(verbosity=2)
