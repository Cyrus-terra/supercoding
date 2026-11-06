import unittest
from import_rows import import_rows


class ImportChecks(unittest.TestCase):
    def test_partial_batch_is_saved(self):
        saved = []
        self.assertEqual(import_rows(list(range(7)), lambda batch: saved.extend(batch)), 7)
        self.assertEqual(saved, list(range(7)))

    def test_full_and_empty_batches(self):
        batches = []
        self.assertEqual(import_rows(list(range(6)), batches.append), 6)
        self.assertEqual(batches, [[0, 1, 2], [3, 4, 5]])
        self.assertEqual(import_rows([], batches.append), 0)
        self.assertEqual(len(batches), 2)

    def test_save_failure_propagates(self):
        def fail(batch):
            raise OSError('storage unavailable')
        with self.assertRaisesRegex(OSError, 'storage unavailable'):
            import_rows([1, 2, 3], fail)


if __name__ == '__main__':
    unittest.main(verbosity=2)
