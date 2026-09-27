`size` parses `"width=80;height=24;scale=1.5"`. It doesn't compile: *`?` couldn't convert the error to `SizeError`*
(E0277), three times. Make it compile without touching `size` or `field`, keeping each parse error in its variant.
