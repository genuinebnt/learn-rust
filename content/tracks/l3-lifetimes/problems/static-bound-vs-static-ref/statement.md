`Stash` stores values of any type and gets them back by type. `Box<dyn Any>` needs `T: 'static`,
which means the value owns its data (or borrows only `'static` data). It does not mean it lives
forever: a `String` built at runtime qualifies.
