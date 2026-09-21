# Muwajjih model card

## Intended use

Route short municipal/government complaints to a department and baseline priority. The service is not a substitute for emergency dispatch or human safety procedures.

## Data

The training set is synthetic and bilingual (Arabic/English). No real personal data is included or required.

## Model

Two scikit-learn character n-gram TF-IDF + Logistic Regression classifiers predict department and baseline priority. A deterministic safety policy overrides priority to `urgent` for explicit emergency signals.

## Behavioural guarantees

- Casing/whitespace normalization should not change the decision.
- Explicit emergency signals must produce `urgent` priority.
- The golden reference is versioned with the model artifact.

## Limitations

Synthetic data cannot represent all municipal language, dialects, misspellings or unseen categories. Real deployment would require reviewed labeled data, monitoring, drift analysis and human escalation pathways.
