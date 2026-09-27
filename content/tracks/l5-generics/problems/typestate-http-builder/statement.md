Build HTTP requests with a builder whose **type** says whether it has a URL yet. `RequestBuilder<NoUrl>`
has no `build` method, so "forgot the URL" is a compile error instead of a runtime one.

- `new()` starts with no headers and a 30 000 ms timeout.
- `url(u)` trims `u`. It fails with `UrlError::Empty` if nothing is left, and with `UrlError::NoScheme` unless
  it starts with `http://` or `https://`. On success it moves everything set so far into a
  `RequestBuilder<HasUrl>`.
- `header` and `timeout_ms` work in either state. Headers accumulate in call order (a repeated key is
  kept twice); the last `timeout_ms` wins.
- `build()` exists only on `RequestBuilder<HasUrl>` and can't fail.
