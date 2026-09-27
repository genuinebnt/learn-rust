Implement both formatting traits for `Money` by hand.

- `Display`: `<amount> <currency>` with two decimals and a leading `-` for negative amounts
  (`12.34 USD`, `-0.05 EUR`). With `{:+}`, zero and positive amounts get a leading `+`. It must respect
  width, fill and alignment, so `format!("{:>12}", m)` right-aligns the whole thing.
- `Debug`: `Money(12.34 USD)`, that is, a tuple struct whose one field is shown as its `Display`
  (no quotes). `{:#?}` gives the standard pretty form, `"Money(\n    12.34 USD,\n)"`.
