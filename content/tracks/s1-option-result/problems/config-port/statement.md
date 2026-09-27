Build a `Server` from a string map `cfg`:

- `host`: the `"host"` value, else the `"bind"` value, else `"127.0.0.1"`. An empty value counts as unset.
- `port`: required. `Err("missing port")` if absent, `Err("invalid port: <value>")` unless it's a `u16` other than 0.
- `tls`: true only when `"tls"` is exactly `"on"`.
- `name`: the `"name"` value, or `""`.
- `workers`: 1 if absent, otherwise a `usize` of at least 1, else `Err("invalid workers: <value>")`.

Check the port before the workers. Values are parsed as they are: no trimming.
