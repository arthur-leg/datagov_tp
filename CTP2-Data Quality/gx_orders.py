"""CTP 2 - Exercise 3: expectation suite for ShopFast orders (GX Core 1.x) - 12 expectations.
Run from the 02_CTP2 folder:  python gx_orders.py
"""
import pandas as pd
import great_expectations as gx

KIT = "../shopfast-kit/data/"
orders = pd.read_csv(KIT + "orders.csv", dtype=str)
customers = pd.read_csv(KIT + "customers.csv", dtype=str)
orders["total_amount_eur"] = pd.to_numeric(orders["total_amount_eur"], errors="coerce")
orders["order_date_dt"] = pd.to_datetime(orders["order_date"], format="%Y-%m-%d", errors="coerce")

# Look at the data BEFORE choosing allowed values (a rule is a business decision)
for c in ["status", "channel", "shipping_country"]:
    print(f"\n{c}:\n{orders[c].value_counts(dropna=False)}")
print("\ntotal_amount_eur:\n", orders["total_amount_eur"].describe())

context = gx.get_context(mode="file")
source = context.data_sources.add_or_update_pandas("shopfast")
asset = source.add_dataframe_asset(name="orders")
batch_def = asset.add_batch_definition_whole_dataframe("all_orders")

suite = context.suites.add_or_update(gx.ExpectationSuite(name="orders_suite"))
E = gx.expectations
for e in [
    # --- given (3) ---
    E.ExpectTableRowCountToBeBetween(min_value=1000, max_value=100000),
    E.ExpectColumnValuesToNotBeNull(column="order_id"),
    E.ExpectColumnValuesToBeUnique(column="order_id"),
    # --- TODO 1: an order without customer cannot be invoiced (Completeness)
    E.ExpectColumnValuesToNotBeNull(column="customer_id"),
    # --- TODO 2: foreign key, no orphan orders (Validity / referential integrity)
    E.ExpectColumnValuesToBeInSet(column="customer_id", value_set=list(set(customers["customer_id"].dropna()))),
    # --- TODO 3: date filled + ISO format (Completeness + Consistency)
    E.ExpectColumnValuesToNotBeNull(column="order_date"),
    E.ExpectColumnValuesToMatchRegex(column="order_date", regex=r"^\d{4}-\d{2}-\d{2}$"),
    # --- TODO 4: no order in the future (Accuracy)
    E.ExpectColumnValuesToBeBetween(column="order_date_dt", max_value=pd.Timestamp.now()),
    # --- TODO 5: lifecycle values defined by the business (Validity)
    E.ExpectColumnValuesToBeInSet(column="status", value_set=["pending", "shipped", "delivered", "cancelled", "returned"]),
    # --- TODO 6: A VERIFIER avec les value_counts affiches ci-dessus
    E.ExpectColumnValuesToBeInSet(column="channel", value_set=["web", "mobile_app", "marketplace"]),   # <-- adapt!
    E.ExpectColumnValuesToBeInSet(column="shipping_country", value_set=["FR", "DE", "ES", "BE"]),
    # --- TODO 7: strictly positive and below a sensible maximum (Accuracy) -> adapt max with describe()
    E.ExpectColumnValuesToBeBetween(column="total_amount_eur", min_value=0, max_value=5000, strict_min=True),
]:
    suite.add_expectation(e)
suite.save()
print("\nNumber of expectations:", len(suite.expectations))

vd = context.validation_definitions.add_or_update(gx.ValidationDefinition(name="orders_validation", data=batch_def, suite=suite))
checkpoint = context.checkpoints.add_or_update(gx.Checkpoint(name="orders_checkpoint", validation_definitions=[vd],
                                                             actions=[gx.checkpoint.UpdateDataDocsAction(name="docs")]))
result = checkpoint.run(batch_parameters={"dataframe": orders})

print("\nSuite passed:", result.success)
for vr in result.run_results.values():
    for r in vr.results:
        cfg = r.expectation_config
        print(f"{'PASS' if r.success else 'FAIL'}  {cfg.type:<45} {cfg.kwargs.get('column', ''):<18} unexpected={r.result.get('unexpected_count', '-')}")
print("\nOpen the report: gx/uncommitted/data_docs/local_site/index.html")
