The code at the bottom uses two traits that don't exist yet. Write them and implement both for `Circle`
and `Rect`:

- `Named`: `fn name(&self) -> String`, giving `"circle"` and `"rect"`.
- `Shape`, which requires `Named`: an associated const `SIDES: u32` (0 for a circle, 4 for a rect),
  `area` and `perimeter` returning `f64`, and a default `describe` returning
  `"<name>, <SIDES> sides, area <area to 2 decimals>"`.

Then finish `both_names`. `Rect` also implements `Label`, which has its own `name`.
