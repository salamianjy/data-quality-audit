# Data Quality Audit — pandas / NumPy

**Question:** How much reported revenue is trustworthy after cleaning a noisy transaction export?

## Skills demonstrated
- Generate reproducible synthetic transaction data (fixed random seed)
- Detect duplicate transaction identifiers, invalid dates, blank customer IDs, and negative/missing amounts
- Standardize inconsistent category labels; produce both cleaned data and machine-readable audit report
- Write unit tests against known injected problems

## Run
```bash
python -m pip install -r requirements.txt
python main.py
python -m unittest discover -s tests -v
```

Expected: 301 input rows; 1 duplicate ID; 4 invalid amounts; 1 invalid date; 1 missing customer; 294 clean rows. The issue counts refer to records *after* deduplication; overlapping reasons would be counted individually.

`outputs/` contains generated files and is ignored by Git. Nothing here uses real customer information.

## AI-model evaluation task idea
Ask an AI model to clean the source table without dropping valid zero-value transactions, to explain how multiple data-quality failures on the same row should be counted, and to reconcile source row counts with output row counts. Evaluate using the unit tests.

## Next extensions
Support currency normalization, a severity scoring system, and an HTML quality dashboard.
