use solution::*;

use std::io::{self, Read};

/// Hands out at most `step` bytes per read.
#[allow(dead_code)]
struct Trickle<'a> {
    data: &'a [u8],
    step: usize,
}

#[allow(dead_code)]
impl Read for Trickle<'_> {
    fn read(&mut self, buf: &mut [u8]) -> io::Result<usize> {
        let n = self.step.min(buf.len()).min(self.data.len());
        buf[..n].copy_from_slice(&self.data[..n]);
        self.data = &self.data[n..];
        Ok(n)
    }
}

/// Fails every other read with ErrorKind::Interrupted, which callers are expected to retry.
#[allow(dead_code)]
struct Flaky<'a> {
    data: &'a [u8],
    fail_next: bool,
}

#[allow(dead_code)]
impl Read for Flaky<'_> {
    fn read(&mut self, buf: &mut [u8]) -> io::Result<usize> {
        self.fail_next = !self.fail_next;
        if !self.fail_next {
            return Err(io::Error::new(io::ErrorKind::Interrupted, "try again"));
        }
        let n = 3.min(buf.len()).min(self.data.len());
        buf[..n].copy_from_slice(&self.data[..n]);
        self.data = &self.data[n..];
        Ok(n)
    }
}

/// Gives `data`, then fails for real.
#[allow(dead_code)]
struct Broken<'a> {
    data: &'a [u8],
}

#[allow(dead_code)]
impl Read for Broken<'_> {
    fn read(&mut self, buf: &mut [u8]) -> io::Result<usize> {
        if self.data.is_empty() {
            return Err(io::Error::new(io::ErrorKind::ConnectionReset, "gone"));
        }
        let n = buf.len().min(self.data.len());
        buf[..n].copy_from_slice(&self.data[..n]);
        self.data = &self.data[n..];
        Ok(n)
    }
}

#[allow(dead_code)]
fn pairs(v: &[(&str, usize)]) -> Vec<(String, usize)> {
    v.iter().map(|&(w, n)| (w.to_string(), n)).collect()
}

#[test]
fn counts_sorted() {
    check!(r#""b a b c a b""#, word_counts("b a b c a b".as_bytes()).unwrap(), pairs(&[("b", 3), ("a", 2), ("c", 1)]));
}

#[test]
fn non_generic_worker() {
    let f: fn(&mut dyn Read) -> io::Result<Vec<(String, usize)>> = word_counts_dyn;
    check!(r#"word_counts_dyn as a fn pointer, on a Cursor"#, f(&mut io::Cursor::new("x y x")).unwrap(), pairs(&[("x", 2), ("y", 1)]));
}

#[test]
fn one_byte_at_a_time() {
    check!(r#""héllo wörld héllo", one byte per read"#, word_counts(Trickle { data: "héllo wörld héllo".as_bytes(), step: 1 }).unwrap(), pairs(&[("héllo", 2), ("wörld", 1)]));
}

#[test]
fn interrupted_is_retried() {
    check!(r#""to be or not to be", Interrupted every other read"#, word_counts(Flaky { data: b"to be or not to be", fail_next: false }).unwrap(), pairs(&[("be", 2), ("to", 2), ("not", 1), ("or", 1)]));
}

#[test]
fn invalid_utf8() {
    check!(r#"bytes [0x66, 0xFF]"#, word_counts(&[0x66u8, 0xFF][..]).map_err(|e| e.kind()), Err(io::ErrorKind::InvalidData));
}
