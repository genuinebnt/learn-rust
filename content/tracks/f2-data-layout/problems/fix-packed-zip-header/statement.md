A backup tool lists ZIP archives without unpacking them: `LocalHeader::view` casts the bytes in place to
a `LocalHeader` and `entries` walks header → name → extra field → data → next header.

It returns garbage. A local header is 30 bytes with `crc32` at offset **14**, but `#[repr(C)]` pads
`crc32` to offset 16, making the struct 32 bytes with alignment 4. `view`'s `SAFETY` comment claims
alignment 1, which is also false, so any header at an odd offset is undefined behaviour (debug builds
catch it as a misaligned-pointer panic).

Make `LocalHeader` match the format: **30 bytes, alignment 1**, fields at their on-disk offsets.
Then fix what that breaks without changing the API: `view`, the accessors, `is_stored`, `describe`
and `entries` behave as documented, and `LocalHeader` stays `Debug`, `PartialEq`, `Eq` and `Hash`.
