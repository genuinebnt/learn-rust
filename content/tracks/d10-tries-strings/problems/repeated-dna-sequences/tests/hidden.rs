use solution::*;

#[test]
fn no_repeat() {
    check!(r#"s = "ACGT", k = 1"#, find_repeated_dna_sequences("ACGT", 1), Vec::<&str>::new());
}

#[test]
fn k_equals_len() {
    check!(r#"s = "ACGT", k = 4"#, find_repeated_dna_sequences("ACGT", 4), Vec::<&str>::new());
}

#[test]
fn k_32_repeat() {
    let s = "A".repeat(33);
    check!(r#"s = 'A' × 33, k = 32"#, find_repeated_dna_sequences(&s, 32), vec!["A".repeat(32)]);
}

#[test]
fn k_32_first_letter_differs() {
    let s = format!("C{}", "A".repeat(32));
    check!(r#"s = "C" + 'A' × 32, k = 32 (the two windows differ only in their first letter)"#, find_repeated_dna_sequences(&s, 32), Vec::<&str>::new());
}

#[test]
fn k_32_last_letter_differs() {
    let s = format!("{}G", "T".repeat(32));
    check!(r#"s = 'T' × 32 + "G", k = 32"#, find_repeated_dna_sequences(&s, 32), Vec::<&str>::new());
}

#[test]
fn k_32_period_4() {
    let s = "ACGT".repeat(16);
    check!(r#"s = "ACGT" × 16, k = 32"#, find_repeated_dna_sequences(&s, 32), vec!["ACGT".repeat(8), "CGTA".repeat(8), "GTAC".repeat(8), "TACG".repeat(8)]);
}

#[test]
fn three_copies_once() {
    check!(r#"s = "ACACAC", k = 2"#, find_repeated_dna_sequences("ACACAC", 2), vec!["AC", "CA"]);
}

#[test]
fn all_t() {
    check!(r#"s = "TTTT", k = 3"#, find_repeated_dna_sequences("TTTT", 3), vec!["TTT"]);
}

#[test]
fn slices_of_s() {
    let s = String::from("GATTGA");
    let got = find_repeated_dna_sequences(&s, 2);
    check!(r#"the answers point into s"#, std::ptr::eq(got[0].as_ptr(), s.as_ptr()), true);
}

#[test]
fn random_vs_brute_force() {
    use std::collections::HashMap;
    let mut rng = anneal_prelude::Rng::new(1017);
    for _ in 0..400 {
        let len = rng.below(20);
        let s = if rng.bool() { rng.string(len, "AC") } else { rng.string(len, "ACGT") };
        let k = 1 + rng.below(6);
        let mut count: HashMap<&str, usize> = HashMap::new();
        let mut order: Vec<&str> = Vec::new();
        for i in 0..(s.len() + 1).saturating_sub(k) {
            let w = &s[i..i + k];
            let c = count.entry(w).or_insert(0);
            if *c == 0 {
                order.push(w);
            }
            *c += 1;
        }
        let want: Vec<&str> = order.into_iter().filter(|w| count[w] >= 2).collect();
        check!(format!("s = {s:?}, k = {k}"), find_repeated_dna_sequences(&s, k), want);
    }
}

#[test]
fn scale_100k() {
    use std::collections::HashMap;
    // Pseudo-random DNA with a planted 32-letter block repeated 5 times, plus a run of A's.
    let mut x: u64 = 12345;
    let mut dna: Vec<u8> = (0..100_000)
        .map(|_| {
            x = x.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
            b"ACGT"[(x >> 60) as usize & 3]
        })
        .collect();
    let block: Vec<u8> = dna[500..532].to_vec();
    for at in [20_000, 40_000, 60_000, 80_000] {
        dna[at..at + 32].copy_from_slice(&block);
    }
    dna[90_000..90_100].fill(b'A');
    let s = String::from_utf8(dna).unwrap();
    let mut count: HashMap<&str, (usize, usize)> = HashMap::new();
    for i in 0..=s.len() - 32 {
        count.entry(&s[i..i + 32]).or_insert((i, 0)).1 += 1;
    }
    let mut want: Vec<(usize, &str)> = count.into_iter().filter(|(_, (_, c))| *c >= 2).map(|(w, (i, _))| (i, w)).collect();
    want.sort_unstable();
    let want: Vec<&str> = want.into_iter().map(|(_, w)| w).collect();
    check!("s = 10⁵ pseudo-random letters with a 32-letter block planted 5 times and 100 A's, k = 32", find_repeated_dna_sequences(&s, 32), want);
}
