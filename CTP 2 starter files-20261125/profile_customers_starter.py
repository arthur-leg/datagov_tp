"""CTP 2 - Exercise 1 STARTER: profile customers.csv with pandas.
Run from the 02_CTP2 folder:  python profile_customers_starter.py
Goal: measure at least 8 rules (2 per dimension) and copy the numbers into quality_scorecard_template.csv
"""
import pandas as pd

df = pd.read_csv("../shopfast-kit/data/customers.csv", dtype=str)   # dtype=str: keep the raw text (e.g. 01300)
n = len(df)
print("Rows:", n)
print(df.head())

# --- Completeness: how many empty values per column? ---
print("\nEmpty values per column:\n", df.isna().sum())

# --- Uniqueness: is customer_id unique? ---
print("\nDuplicated customer_id rows:", df["customer_id"].duplicated(keep=False).sum())

# TODO 1 (Uniqueness): normalise email (strip + lower case) and count people registered twice
# TODO 2 (Validity): count emails that do not match the regex  ^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$   (hint: .str.match)
# TODO 3 (Consistency): list the distinct values of country with value_counts() - how many spellings for 4 countries?
# TODO 4 (Consistency): count signup_date values that are NOT in the format YYYY-MM-DD
# TODO 5 (Validity): loyalty_tier values outside bronze / silver / gold / platinum
# TODO 6 (Accuracy): birth dates in the future or before 1906 (convert the ISO ones with pd.to_datetime)
# TODO 7 (Validity): French postal codes that do not have 5 digits
# Bonus: compute score_pct = 100 * (1 - failing_rows / n) for each rule
