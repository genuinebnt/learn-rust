use solution::*;

#[test]
fn back_and_forth() {
    check!(r#"board = ["AB"], word = "ABA""#, exist(&["AB"], "ABA"), false);
}

#[test]
fn letter_missing() {
    check!(r#"board = ["a"], word = "b""#, exist(&["a"], "b"), false);
}

#[test]
fn case_sensitive() {
    check!(r#"board = ["aB"], word = "ab""#, exist(&["aB"], "ab"), false);
}

#[test]
fn snake_through_everything() {
    check!(r#"board = ["ABC", "FED", "GHI"], word = "ABCDEFGHI""#, exist(&["ABC", "FED", "GHI"], "ABCDEFGHI"), true);
}

#[test]
fn right_to_left() {
    check!(r#"board = ["AB"], word = "BA""#, exist(&["AB"], "BA"), true);
}

#[test]
fn longer_than_board() {
    check!(r#"board = ["AAA", "AAA"], word = "AAAAAAA""#, exist(&["AAA", "AAA"], "AAAAAAA"), false);
}

#[test]
fn leetcode_restore_on_backtrack() {
    check!(r#"board = ["ABCE", "SFES", "ADEE"], word = "ABCESEEEFS""#, exist(&["ABCE", "SFES", "ADEE"], "ABCESEEEFS"), true);
}

#[test]
fn leetcode_first_path_fails() {
    check!(r#"board = ["CAA", "AAA", "BCD"], word = "AAB""#, exist(&["CAA", "AAA", "BCD"], "AAB"), true);
}

#[test]
fn whole_board_of_one_letter() {
    check!(r#"board = ["AAAA", "AAAA", "AAAA"], word = 12 × "A""#, exist(&["AAAA", "AAAA", "AAAA"], "AAAAAAAAAAAA"), true);
}

#[test]
fn single_column() {
    check!(r#"board = ["A", "B", "C"], word = "CBA""#, exist(&["A", "B", "C"], "CBA"), true);
}

/// Every path of distinct cells, with a bitmask of used cells instead of editing the board.
fn brute(board: &[&str], word: &[u8]) -> bool {
    fn walk(g: &[&[u8]], word: &[u8], r: usize, c: usize, used: u64) -> bool {
        let w = g[0].len();
        if g[r][c] != word[0] || used >> (r * w + c) & 1 == 1 {
            return false;
        }
        if word.len() == 1 {
            return true;
        }
        let used = used | 1 << (r * w + c);
        let near = [(r.wrapping_sub(1), c), (r + 1, c), (r, c.wrapping_sub(1)), (r, c + 1)];
        near.iter().any(|&(a, b)| a < g.len() && b < w && walk(g, &word[1..], a, b, used))
    }
    let g: Vec<&[u8]> = board.iter().map(|row| row.as_bytes()).collect();
    (0..g.len()).any(|r| (0..g[0].len()).any(|c| walk(&g, word, r, c, 0)))
}

#[test]
fn random_vs_bitmask_paths() {
    let mut rng = anneal_prelude::Rng::new(1129);
    for _ in 0..400 {
        let (h, w) = (rng.int(1, 3) as usize, rng.int(1, 4) as usize);
        let rows: Vec<String> = (0..h).map(|_| rng.string(w, "ABC")).collect();
        let board: Vec<&str> = rows.iter().map(|s| s.as_str()).collect();
        let len = rng.int(1, 7) as usize;
        let word = rng.string(len, "ABC");
        check!(format!("board = {board:?}, word = {word:?}"), exist(&board, &word), brute(&board, word.as_bytes()));
    }
}

#[test]
fn scale_letter_the_board_lacks() {
    // 6×6 of A, and 24 A's then a B: every path of A's is a dead end.
    let board = vec!["AAAAAA"; 6];
    let word = "A".repeat(24) + "B";
    check!("board = 6×6 of A, word = 24 × \"A\" + \"B\"", exist(&board, &word), false);
}

#[test]
fn scale_one_letter_short() {
    // 35 A's and one C; the word needs 36 A's.
    let board = vec!["AAAAAA", "AAAAAA", "AAAAAA", "AAACAA", "AAAAAA", "AAAAAA"];
    let word = "A".repeat(36);
    check!("board = 6×6 of A with one C, word = 36 × \"A\"", exist(&board, &word), false);
}

#[test]
fn scale_rare_last_letter() {
    let board = vec!["AAAAAA", "AAAAAA", "AAAAAA", "AAAAAA", "AAAAAA", "AAAAAB"];
    let word = "A".repeat(30) + "B";
    check!("board = 6×6 of A with a B in the corner, word = 30 × \"A\" + \"B\"", exist(&board, &word), true);
}
