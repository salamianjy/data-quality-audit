import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import audit, make_dataset

class TestAudit(unittest.TestCase):
    def test_deterministic_counts(self):
        cleaned, issues = audit(make_dataset())
        self.assertEqual(issues['input_rows'], 301)
        self.assertEqual(issues['duplicate_transaction_ids'], 1)
        self.assertEqual(issues['invalid_amount_rows'], 4)
        self.assertEqual(issues['invalid_date_rows'], 1)
        self.assertEqual(issues['missing_customer_rows'], 1)
        self.assertEqual(len(cleaned), 294)
    def test_cleaned_integrity(self):
        cleaned, _ = audit(make_dataset())
        self.assertTrue(cleaned['amount'].ge(0).all())
        self.assertFalse(cleaned['transaction_id'].duplicated().any())
        self.assertIn('tech', cleaned['category'].unique())
    def test_missing_required_column(self):
        with self.assertRaises(ValueError):
            audit(make_dataset().drop(columns='date'))

if __name__ == '__main__': unittest.main()
