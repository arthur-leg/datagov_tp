"""CTP 2 - Exercise 4: replay the 'cents' incident.
Naive suite passes on payments_batch_2.csv (every amount is 100x too big: cents instead of euros).
The smart suite adds value-range / distribution / format checks that catch it.
"""
import pandas as pd
import great_expectations as gx

KIT = "../shopfast-kit/data/"
files = {"payments (history)": KIT + "payments.csv", "payments_batch_2 (new)": "payments_batch_2.csv"}

context = gx.get_context(mode="file")
source = context.data_sources.add_or_update_pandas("shopfast_payments")
asset = source.add_dataframe_asset(name="payments")
batch_def = asset.add_batch_definition_whole_dataframe("whole")
E = gx.expectations

naive = [E.ExpectColumnValuesToNotBeNull(column="payment_id"), E.ExpectColumnValuesToBeUnique(column="payment_id"),
         E.ExpectColumnValuesToNotBeNull(column="amount"), E.ExpectColumnValuesToBeInSet(column="currency", value_set=["EUR"]),
         E.ExpectColumnValuesToBeInSet(column="method", value_set=["card", "paypal", "apple_pay", "bank_transfer"])]

smart = naive + [
    # 1. Range per value: history max is 1400.79 EUR -> 2000 is a sensible ceiling (batch_2 reaches 37 996)
    E.ExpectColumnValuesToBeBetween(column="amount", min_value=0, max_value=2000, strict_min=True),
    # 2. Distribution: history mean = 235.9 EUR (batch_2 mean = 18 922)
    E.ExpectColumnMeanToBeBetween(column="amount", min_value=100, max_value=400),
    # 3. Median, more robust to outliers than the mean (history = 184.3)
    E.ExpectColumnMedianToBeBetween(column="amount", min_value=80, max_value=350),
    # 4. Format of the raw text: a decimal point and 1-2 decimals (history: always, batch_2: never = integers in cents)
    E.ExpectColumnValuesToMatchRegex(column="amount_txt", regex=r"^\d+\.\d{1,2}$"),
]

def run(name, expectations, df):
    suite = context.suites.add_or_update(gx.ExpectationSuite(name=name))
    for e in expectations: suite.add_expectation(e.copy() if hasattr(e, "copy") else e)
    suite.save()
    return batch_def.get_batch(batch_parameters={"dataframe": df}).validate(suite)

for label, path in files.items():
    df = pd.read_csv(path, dtype=str); df["amount_txt"] = df["amount"]; df["amount"] = pd.to_numeric(df["amount"])
    print(f"\n{label}: amount min={df['amount'].min()} median={df['amount'].median()} mean={df['amount'].mean():.2f} max={df['amount'].max()}")
    for suite_name, exps in [("naive_payments", naive), ("smart_payments", smart)]:
        res = run(suite_name, exps, df)
        failed = [r.expectation_config.type for r in res.results if not r.success]
        print(f"{label:<24} {suite_name:<15} success={res.success}  failed={failed}")
