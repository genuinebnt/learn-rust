Write the two traits the code at the bottom uses, then finish `first_decoded` (its `where` clause too)
and `to_both`.

- `Convert<T>` with `fn convert(&self) -> T`. `Celsius` converts to `Fahrenheit` (×9/5 + 32) and to
  `Kelvin` (+273.15).
- `Decoder` with an associated type `Output`, an associated const `NAME: &'static str`, and
  `fn decode(&self, input: &str) -> Option<Self::Output>`.
  - `CsvInts` (`"csv"`) gives `Vec<i64>`. Parts are split on `,` and trimmed; a blank input is an empty
    list; any part that isn't an integer makes the whole input fail.
  - `KeyValue` (`"kv"`) gives `(String, String)`, split at the first `=`, both sides trimmed. No `=` fails.
