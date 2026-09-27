Implement `Display` for `Money` as `<amount> <currency>` with two decimals, and a leading `-` for
negative amounts. It must respect width and alignment, so `format!("{:>12}", m)` right-aligns it.
`Debug` stays derived.
