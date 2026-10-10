//! A block of sorted keys with the shared prefix of each key left out.

/// The keys must be sorted and at most 255 bytes each, and there are at most 255 of them.
pub fn encode_keys(keys: &[Vec<u8>]) -> Vec<u8> {
    // @begin 2a-c4
    let mut out = vec![keys.len() as u8];
    let mut prev: &[u8] = &[];
    for k in keys {
        let shared = prev.iter().zip(k).take_while(|(a, b)| a == b).count();
        out.push(shared as u8);
        out.push((k.len() - shared) as u8);
        out.extend_from_slice(&k[shared..]);
        prev = k;
    }
    out
    //~ todo!("2a-c4: the count, then (shared, rest length, rest) for each key")
    // @end
}

/// The keys of a block, or `None` if the bytes are not exactly one well-formed block.
pub fn decode_keys(bytes: &[u8]) -> Option<Vec<Vec<u8>>> {
    // @begin 2a-c4
    let (&count, mut rest) = bytes.split_first()?;
    let mut keys: Vec<Vec<u8>> = Vec::new();
    for _ in 0..count {
        let (&shared, r) = rest.split_first()?;
        let (&len, r) = r.split_first()?;
        let (len, shared) = (len as usize, shared as usize);
        if r.len() < len {
            return None;
        }
        let prev: &[u8] = keys.last().map_or(&[], |k| k.as_slice());
        if shared > prev.len() {
            return None;
        }
        let mut key = prev[..shared].to_vec();
        key.extend_from_slice(&r[..len]);
        keys.push(key);
        rest = &r[len..];
    }
    if rest.is_empty() {
        Some(keys)
    } else {
        None
    }
    //~ todo!("2a-c4: rebuild each key from the previous key's prefix; refuse anything malformed")
    // @end
}
