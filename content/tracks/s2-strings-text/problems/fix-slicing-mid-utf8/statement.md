Three helpers for showing user text. They were tested on ASCII only: each one either panics or gives the
wrong answer on accented text, emoji or `ß`. Fix them to match their doc comments, counting characters
(Unicode scalar values), not bytes.
