Bytes from a socket arrive in arbitrary chunks, so a multi-byte character can be split between two reads.
Write a streaming decoder:

- `push(chunk, out)` appends the decoded text of `chunk` to `out`. Invalid bytes become U+FFFD exactly as
  `String::from_utf8_lossy` replaces them. If the chunk ends partway through a character, hold those bytes
  and finish the character with the next chunk.
- `finish(out)` ends the input: if a character was left unfinished, append one U+FFFD.

Whatever the chunking, the output must equal `String::from_utf8_lossy` of all the bytes joined together.
