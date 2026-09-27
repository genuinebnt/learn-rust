`triage` uses an `Inbox` API that doesn't exist yet. Write `impl Inbox` with these methods. Pick each
receiver and return type yourself: a method that only reads must be callable while other readers are
alive (the tests hold two at once), and nothing may copy a message or its text.

- `new()` and `push(id, from, body)`: a new message is unread and has no reply.
- `get(id)`: the message, borrowed. `get_mut(id)`: the message, for editing.
- `unread()`: the unread messages, borrowed, oldest first, in a `Vec`.
- `reply_to(id)`: the reply's text as a string slice, `None` if there's no such message or no reply.
- `mark_read(id)`: marks it read and returns whether it was unread (`false` for an unknown id).
- `reply_mut(id)`: the reply for editing in place, created empty when the message has none yet; `None`
  for an unknown id.
- `newest_unread_mut()`: the most recent unread message, for editing.
