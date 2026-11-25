"""CTP 2 - Exercise 1: profile customers.csv and WRITE the scorecard automatically.
Run from the 02_CTP2 folder:  python profile_customers.py   -> quality_scorecard.csv
Adapt the column names below if they differ (print(df.columns) is shown first).
"""
import pandas as pd

df = pd.read_csv("../shopfast-kit/data/customers.csv", dtype=str)
n = len(df)
print("Rows:", n, "\nColumns:", list(df.columns))
PHONE, POSTAL = "phone", "postal_code"          # <-- adapt to the real column names

today = pd.Timestamp.now().normalize()
rows = []
def add(dim, rule, col, how, failing, severity, who):
    failing = int(failing)
    rows.append([dim, rule, col, how, failing, n, round(100 * (1 - failing / n), 2), severity, who])

# Completeness
email_empty = df["email"].isna() | (df["email"].str.strip() == "")
add("Completeness", "email is filled", "email", "empty or blank values", email_empty.sum(), "medium", "Owner")
dob_empty = df["birth_date"].isna() | (df["birth_date"].str.strip() == "")
add("Completeness", "birth_date is filled", "birth_date", "empty or blank values", dob_empty.sum(), "low", "Steward")

# Uniqueness
add("Uniqueness", "customer_id is unique", "customer_id", "extra rows with an already seen customer_id",
    df["customer_id"].duplicated(keep="first").sum(), "high", "Custodian")
email_norm = df["email"].str.strip().str.lower()
add("Uniqueness", "one account per person", "email", "extra rows with same strip+lower email (non empty)",
    (email_norm.duplicated(keep="first") & email_norm.notna()).sum(), "medium", "Steward")

# Validity
regex = r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$"
bad_email = df["email"].notna() & ~df["email"].str.strip().str.match(regex, na=False)
add("Validity", "email looks like an email", "email", f"non-empty not matching {regex}", bad_email.sum(), "medium", "Owner")
add("Validity", "loyalty_tier in bronze/silver/gold/platinum", "loyalty_tier", "non-empty values outside the 4 tiers",
    (df["loyalty_tier"].notna() & ~df["loyalty_tier"].isin(["bronze", "silver", "gold", "platinum"])).sum(), "low", "Steward")
if POSTAL in df.columns and "country" in df.columns:
    fr = df["country"].str.strip().str.lower().isin(["fr", "france", "fra"])
    add("Validity", "French postal code has 5 digits", POSTAL, "FR rows whose postal code is not 5 digits",
        (fr & ~df[POSTAL].fillna("").str.fullmatch(r"\d{5}")).sum(), "medium", "Custodian")

# Consistency
print("\nCountry spellings:\n", df["country"].value_counts(dropna=False))
add("Consistency", "country is an ISO-2 code", "country", "values not in {FR, DE, ES, BE}",
    (~df["country"].isin(["FR", "DE", "ES", "BE"])).sum(), "medium", "Custodian")
add("Consistency", "signup_date is YYYY-MM-DD", "signup_date", "values not matching ^\\d{4}-\\d{2}-\\d{2}$",
    (~df["signup_date"].fillna("").str.fullmatch(r"\d{4}-\d{2}-\d{2}")).sum(), "low", "Custodian")

# Accuracy: only ISO dates are converted (other formats are already counted in consistency)
dob = pd.to_datetime(df["birth_date"], format="%Y-%m-%d", errors="coerce")
implausible = dob.notna() & ((dob < pd.Timestamp("1906-01-01")) | (dob > today - pd.DateOffset(years=18)))
add("Accuracy", "birth_date between 1906 and today-18y", "birth_date", "ISO dates outside the range",
    implausible.sum(), "high", "Owner")

out = pd.DataFrame(rows, columns=["dimension", "rule_in_plain_words", "column", "how_you_measured_it", "failing_rows",
                                  "total_rows", "score_pct", "severity_high_medium_low", "who_should_fix_owner_steward_custodian"])
out.to_csv("quality_scorecard.csv", index=False)
print("\n", out[["dimension", "rule_in_plain_words", "failing_rows", "score_pct"]].to_string(index=False))
