use solution::*;

#[test]
fn empty_board() {
    check!(r#"board = [], words = ["a"]"#, find_words(&[], &["a"]), Vec::<&str>::new());
}

#[test]
fn single_cell() {
    check!(r#"board = ["z"], words = ["z", "y"]"#, find_words(&["z"], &["z", "y"]), vec!["z"]);
}

#[test]
fn no_diagonals() {
    check!(r#"board = ["ab", "cd"], words = ["ad", "bc"]"#, find_words(&["ab", "cd"], &["ad", "bc"]), Vec::<&str>::new());
}

#[test]
fn prefixes_and_words() {
    check!(r#"board = ["abc"], words = ["a", "ab", "abc", "abcd", "cba"]"#, find_words(&["abc"], &["a", "ab", "abc", "abcd", "cba"]), vec!["a", "ab", "abc", "cba"]);
}

#[test]
fn snake_through_all() {
    check!(r#"board = ["abc", "fed", "ghi"], words = ["abcdefghi"]"#, find_words(&["abc", "fed", "ghi"], &["abcdefghi"]), vec!["abcdefghi"]);
}

#[test]
fn leetcode_column() {
    check!(r#"board = ["a", "a"], words = ["aaa"]"#, find_words(&["a", "a"], &["aaa"]), Vec::<&str>::new());
}

#[test]
fn found_by_many_paths() {
    check!(r#"board = ["aa", "aa"], words = ["aa"]"#, find_words(&["aa", "aa"], &["aa"]), vec!["aa"]);
}

#[test]
fn one_row() {
    check!(r#"board = ["hello"], words = ["hell", "olleh", "lol"]"#, find_words(&["hello"], &["hell", "olleh", "lol"]), vec!["hell", "olleh"]);
}

#[test]
fn answers_are_the_input_slices() {
    let w = String::from("ba");
    let got = find_words(&["ab"], &[&w]);
    check!(r#"the answer points into words"#, std::ptr::eq(got[0].as_ptr(), w.as_ptr()), true);
}

        #[test]
        fn random_vs_brute_force() {
            fn on_board(g: &mut Vec<Vec<u8>>, r: usize, c: usize, w: &[u8]) -> bool {
                if g[r][c] != w[0] {
                    return false;
                }
                if w.len() == 1 {
                    return true;
                }
                let keep = g[r][c];
                g[r][c] = b'#';
                let (rows, cols) = (g.len(), g[0].len());
                let ok = (r > 0 && on_board(g, r - 1, c, &w[1..]))
                    || (r + 1 < rows && on_board(g, r + 1, c, &w[1..]))
                    || (c > 0 && on_board(g, r, c - 1, &w[1..]))
                    || (c + 1 < cols && on_board(g, r, c + 1, &w[1..]));
                g[r][c] = keep;
                ok
            }
            let mut rng = anneal_prelude::Rng::new(1018);
            for _ in 0..300 {
                let (rows, cols) = (1 + rng.below(3), 1 + rng.below(3));
                let board: Vec<String> = (0..rows).map(|_| rng.string(cols, "ab")).collect();
                let mut words: Vec<String> = Vec::new();
                for _ in 0..rng.below(6) {
                    let len = 1 + rng.below(5);
                    words.push(rng.string(len, "ab"));
                }
                let b: Vec<&str> = board.iter().map(|s| s.as_str()).collect();
                let w: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
                let mut g: Vec<Vec<u8>> = board.iter().map(|s| s.as_bytes().to_vec()).collect();
                let mut want: Vec<&str> = w
                    .iter()
                    .copied()
                    .filter(|word| (0..rows).any(|r| (0..cols).any(|c| on_board(&mut g, r, c, word.as_bytes()))))
                    .collect();
                want.sort_unstable();
                want.dedup();
                check!(format!("board = {b:?}, words = {w:?}"), find_words(&b, &w), want);
            }
        }

        #[test]
        fn scale_30k_words_one_search() {
            // 12 × 12 a's with a b in the corner. 30000 words start with six a's and then leave the board,
            // so searching once per word repeats the same walk 30000 times.
            let mut board: Vec<String> = vec!["a".repeat(12); 12];
            board[11] = format!("{}b", "a".repeat(11));
            let b: Vec<&str> = board.iter().map(|s| s.as_str()).collect();
            let mut words: Vec<String> = (0..30_000).map(|i| format!("aaaaaa{}", base10(i * 3, 5).replace('a', "k"))).collect();
            for w in ["b", "ba", "aab", "bab", "aaaaaaaaab"] {
                words.push(w.to_string());
            }
            let w: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            check!("12 × 12 board of a's with a b in the corner; 30000 words 'a' × 6 + five letters from b..k, plus b, ba, aab, bab, aaaaaaaaab", find_words(&b, &w), vec!["aaaaaaaaab", "aab", "b", "ba"]);
        }

        #[test]
        fn scale_found_words_are_pruned() {
            // Every word is found on the first long path; without pruning, every cell starts a search through
            // all self-avoiding paths of 15 steps.
            let board = vec!["a".repeat(12); 12];
            let b: Vec<&str> = board.iter().map(|s| s.as_str()).collect();
            let words: Vec<String> = (1..=16).map(|n| "a".repeat(n)).collect();
            let w: Vec<&str> = words.iter().map(|s| s.as_str()).collect();
            check!("12 × 12 board of a's, words = 'a' × 1..=16", find_words(&b, &w), w.clone());
        }

fn base10(mut i: usize, len: usize) -> String {
    let mut w = vec![b'a'; len];
    for k in (0..len).rev() {
        w[k] = b'a' + (i % 10) as u8;
        i /= 10;
    }
    String::from_utf8(w).unwrap()
}
