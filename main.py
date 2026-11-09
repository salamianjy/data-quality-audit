"""Deterministic data-quality pipeline for synthetic transaction records."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

SEED = 42

def make_dataset(n=300):
    rng = np.random.default_rng(SEED)
    customers = rng.integers(1000, 1050, size=n)
    amounts = np.round(rng.gamma(shape=2, scale=65, size=n), 2)
    timestamps = pd.Timestamp('2025-01-01') + pd.to_timedelta(rng.integers(0, 90, size=n), unit='D')
    rows = pd.DataFrame({'transaction_id': [f'TX-{i:04d}' for i in range(n)],
                         'customer_id': customers.astype(str),
                         'date': timestamps.strftime('%Y-%m-%d'),
                         'amount': amounts,
                         'category': rng.choice(['food', 'travel', 'tech'], size=n)})
    rows.loc[[3, 25, 120], 'amount'] = np.nan
    rows.loc[40, 'amount'] = -18
    rows.loc[80, 'date'] = 'not-a-date'
    rows.loc[100, 'category'] = '  Tech '
    rows.loc[200, 'customer_id'] = ''
    return pd.concat([rows, rows.iloc[[10]]], ignore_index=True)

def audit(df):
    """Return cleaned transactions and a transparent issue summary.

    Rules: deduplicate IDs; normalize categories; parse dates; reject invalid/missing
    amounts (including negative amounts), invalid dates, and missing customers.
    """
    required = {'transaction_id', 'customer_id', 'date', 'amount', 'category'}
    if not required.issubset(df.columns):
        raise ValueError(f'Missing columns: {sorted(required-set(df.columns))}')
    out = df.copy()
    issues = {'input_rows': len(out), 'duplicate_transaction_ids': int(out.duplicated('transaction_id').sum())}
    out = out.drop_duplicates('transaction_id', keep='first')
    out['category'] = out['category'].astype('string').str.strip().str.lower()
    out['date'] = pd.to_datetime(out['date'], errors='coerce')
    out['amount'] = pd.to_numeric(out['amount'], errors='coerce')
    bad_amount = out['amount'].isna() | (out['amount'] < 0)
    bad_date = out['date'].isna()
    bad_customer = out['customer_id'].astype('string').str.strip().fillna('').eq('')
    issues.update({'invalid_amount_rows': int(bad_amount.sum()),
                   'invalid_date_rows': int(bad_date.sum()),
                   'missing_customer_rows': int(bad_customer.sum())})
    out = out.loc[~(bad_amount | bad_date | bad_customer)].copy()
    issues['clean_rows'] = len(out)
    issues['removed_rows_total'] = issues['input_rows'] - issues['clean_rows']
    return out.reset_index(drop=True), issues

def main():
    base = Path(__file__).resolve().parent
    cleaned, report = audit(make_dataset())
    dest = base/'outputs'; dest.mkdir(exist_ok=True)
    cleaned.to_csv(dest/'clean_transactions.csv', index=False)
    (dest/'audit_report.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    print('Total validated revenue:', round(float(cleaned.amount.sum()), 2))

if __name__ == '__main__':
    main()
