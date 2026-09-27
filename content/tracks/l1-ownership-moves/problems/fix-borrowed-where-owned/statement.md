`Tag::new` doesn't compile: `Tag` owns its data, and `new` is handed borrowed data. Fix it so the tests
compile. They build tags from string literals and from `String`s the caller already owns; an owned
name must be moved into the tag, not copied.
