`decode_normalized` doesn't compile: `clean` does not live long enough (E0597). Fix its bound.

Also add `DecodeOwned`, a trait for "decodes from text of any lifetime" (like serde's
`DeserializeOwned`), implemented automatically for every such type, so callers can write `T: DecodeOwned`.
