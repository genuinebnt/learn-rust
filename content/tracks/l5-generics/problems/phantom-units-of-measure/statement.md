`Length<U>` is an `f64` tagged with a unit. The unit exists only in the type: `Length<Meters>` and
`Length<Feet>` are different types, and `to::<V>()` converts. It has three problems:

- Adding a `Length<Feet>` to a `Length<Meters>` compiles and adds the raw numbers. Make it a type error.
- It doesn't compile for the tests' own units. `Length<U>` must be `Copy`, `Clone`, `PartialEq`,
  `PartialOrd` and `Debug` (printed like `Display`: `"2.5 in"`) for **every** `U: Unit`, including units
  that derive nothing.
- `Length<Handle>` isn't `Send` or `Sync`, because `Handle` holds a raw pointer. A length never contains a
  unit value, so it must be `Send + Sync` whatever `U` is.
