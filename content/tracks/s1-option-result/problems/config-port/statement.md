Read the `"port"` key from `cfg` and parse it as a `u16`.
Return `Err("missing port")` if the key is absent and `Err("invalid port: <value>")` if it doesn't parse.
