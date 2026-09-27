`User` has a name, maybe a nickname, and maybe a list of emails (`Some(vec![])` is a user with no emails). Write,
without cloning anything:

- `display_name`: the nickname if there is one (even an empty one), else the name.
- `primary_email`: the first email, or `None`.
- `handles`: the name, then the nickname if any, then every email, in that order.
- `shout_nickname`: uppercases the nickname in place (ASCII only).
- `add_email`: appends an email, creating the list if it's `None`.
