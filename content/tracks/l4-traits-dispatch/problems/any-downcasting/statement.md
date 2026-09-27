An `Entity` holds at most one component of each type as `Box<dyn Component>`. Implement it:

- `insert` adds a component, or replaces the one of the same type *in place* and returns the old value.
- `get`, `get_mut` and `remove` find the component of type `T`; `remove` hands it back by value.
- `names` lists `name()` of each component in insertion order.

Components are defined by users of the crate (the tests define their own), so `Component` can't grow new
required methods.
