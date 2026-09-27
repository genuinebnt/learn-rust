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
fn empty() {
    check!(r#""""#, word_counts("".as_bytes()).unwrap(), Vec::<(String, usize)>::new());
}

#[test]
fn only_whitespace() {
    check!(r#"" \n\t ""#, word_counts(" \n\t ".as_bytes()).unwrap(), Vec::<(String, usize)>::new());
}

#[test]
fn read_error_is_passed_on() {
    check!(r#"a reader that fails after some data"#, word_counts(Broken { data: b"a b" }).map_err(|e| e.kind()), Err(io::ErrorKind::ConnectionReset));
}

#[test]
fn case_sensitive() {
    check!(r#""Go go GO go""#, word_counts("Go go GO go".as_bytes()).unwrap(), pairs(&[("go", 2), ("GO", 1), ("Go", 1)]));
}

#[test]
fn unicode_whitespace() {
    check!(r#""a\u{3000}b\u{a0}a""#, word_counts("a\u{3000}b\u{a0}a".as_bytes()).unwrap(), pairs(&[("a", 2), ("b", 1)]));
}

#[test]
fn split_char_across_reads() {
    check!(r#""日本 日本", 2 bytes per read"#, word_counts(Trickle { data: "日本 日本".as_bytes(), step: 2 }).unwrap(), pairs(&[("日本", 2)]));
}

#[test]
fn by_mut_reference() {
    let mut c = io::Cursor::new("q");
    check!(r#"&mut Cursor, then the cursor is at the end"#, (word_counts(&mut c).unwrap(), c.position()), (pairs(&[("q", 1)]), 1));
}

#[test]
fn dyn_worker_on_a_trickle() {
    check!(r#"word_counts_dyn over a 1-byte Trickle"#, word_counts_dyn(&mut Trickle { data: b"z z y", step: 1 }).unwrap(), pairs(&[("z", 2), ("y", 1)]));
}

#[test]
fn chain_of_readers() {
    check!(r#""ab c".chain(" ab")"#, word_counts("ab c".as_bytes().chain(" ab".as_bytes())).unwrap(), pairs(&[("ab", 2), ("c", 1)]));
}

#[test]
fn invalid_utf8_mid_stream() {
    let mut bytes = b"ok ok ".to_vec();
    bytes.push(0x80);
    check!(r#"valid words then a lone continuation byte"#, word_counts(Trickle { data: &bytes, step: 2 }).map_err(|e| e.kind()), Err(io::ErrorKind::InvalidData));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4518);
    for _ in 0..300 {
        let n = rng.below(20);
        let text = rng.string(n, "ab é\n");
        let step = 1 + rng.below(4);
        let mut want: Vec<(String, usize)> = Vec::new();
        for w in text.split_whitespace() {
            match want.iter_mut().find(|(x, _)| x == w) {
                Some((_, c)) => *c += 1,
                None => want.push((w.to_string(), 1)),
            }
        }
        want.sort_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(&b.0)));
        check!(format!("text = {text:?}, {step} bytes per read"), word_counts(Trickle { data: text.as_bytes(), step }).unwrap(), want);
    }
}

#[test]
fn scale_many_words() {
    let text: String = (0..200_000).map(|i| format!("w{} ", i % 50_000)).collect();
    let got = word_counts(text.as_bytes()).unwrap();
    check!("200000 words, 50000 distinct", (got.len(), got[0].clone(), got.iter().all(|(_, n)| *n == 4)), (50_000, ("w0".to_string(), 4), true));
}
