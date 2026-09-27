A tag-length-value format: each record is a tag byte, a length byte `len`, then `len` bytes of value.

- `parse_tlv(data)`: the records in order, as `(tag, value)` with each value borrowed from `data`. If the
  data starts with the magic bytes `b"TLV"`, skip them first. Return `None` if the last record is cut
  short (a tag with no length, or fewer than `len` value bytes).
- `encode_tlv(records)`: the bytes for these records, in one allocation of exactly the final size (no
  allocation at all for no records). `None` if any value is longer than 255 bytes.
- `join_values(records, sep)`: all the values, with the byte `sep` between each pair.
