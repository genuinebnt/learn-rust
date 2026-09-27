A user-space TCP stack keeps a `SegmentMeta` for every queued segment, and its `TcpFlags` is six `bool`s:
6 bytes where the wire uses one, which makes `SegmentMeta` 16 bytes instead of 12. Its methods also
can't be used in `const` items, and conntrack wants a lookup table built at compile time.

Rewrite `TcpFlags` as **one byte** (`#[repr(transparent)]` over `u8`, bit values as on the wire:
FIN = 0x01, SYN = 0x02, RST = 0x04, PSH = 0x08, ACK = 0x10, URG = 0x20), keeping the API, and:

- make every inherent method a `const fn`;
- add `pub const VALID: [bool; 64]`, indexed by the flag byte and computed at compile time: the
  combinations netfilter accepts, ignoring PSH, are SYN, SYN|URG, SYN|ACK, RST, RST|ACK, FIN|ACK,
  FIN|ACK|URG, ACK and ACK|URG; `is_valid` reads it;
- `Debug` prints set flags in bit order: `TcpFlags(SYN | ACK)`, or `TcpFlags(empty)`.

`!flags` and `complement` stay within the six flags; `from_bits` rejects any other bit.
