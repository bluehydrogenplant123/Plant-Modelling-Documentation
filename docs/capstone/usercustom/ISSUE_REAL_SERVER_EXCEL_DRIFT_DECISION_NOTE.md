# Decision Note: Excel Baseline Drift

## 0. Trigger

I merged a new version, but compat-check implicitly treated the latest Excel as
the default baseline.

The gap is:

- Raunak may already have changed Excel for this merged version
- compat-check did not first confirm that Excel changed
- compat-check did not record which Excel workbook was accepted for this merge

So the real issue is not only "Excel changed", but "which exact Excel baseline
belongs to this merged version".

---

## 1. Confirmed

Raunak creates a new dated Excel workbook whenever he changes Excel.

Implication:

- each accepted merge/version should record the exact Excel baseline
- compat-check should not silently assume "latest Excel" without recording it

---

## 2. Confirmed

We should compare the recorded accepted Excel baseline with the current runtime
input/import status.

If they do not match, the system should warn in:

- dashboard
- terminal / server startup logs

This is the minimum reminder that repo baseline and runtime may be out of sync.

---

## 3. Deferred

Do not handle removed variables with existing computed results yet.

---

## 4. Deferred

Do not handle diagram storage location / developer access yet.
