- `is_command(input, command)`: does `input`, with surrounding whitespace ignored, equal `command`,
  ignoring ASCII case? No allocation.
- `normalize_header(name)`: lower-case an HTTP header name in place. Only ASCII letters change (header
  names are ASCII; leave anything else as it is). No allocation.
- `title_case(s)`: for display. In each whitespace-separated word, the first character goes to upper
  case and the rest to lower case, by the full Unicode rules. Join the words with single spaces.
