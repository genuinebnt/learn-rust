use solution::*;

#[test]
fn nobody() {
    check!(r#"hats = []"#, number_ways(&[]), 1);
}

#[test]
fn one_person_one_hat() {
    check!(r#"hats = [[7]]"#, number_ways(&[vec![7]]), 1);
}

#[test]
fn someone_likes_nothing() {
    check!(r#"hats = [[1, 2], []]"#, number_ways(&[vec![1, 2], vec![]]), 0);
}

#[test]
fn one_person_every_hat() {
    check!(r#"hats = [[1..=40]]"#, number_ways(&[(1..=40).collect()]), 40);
}

#[test]
fn ends_of_the_range() {
    check!(r#"hats = [[1, 40], [1, 40]]"#, number_ways(&[vec![1, 40], vec![1, 40]]), 2);
}

#[test]
fn chain() {
    check!(r#"hats = [[1, 2], [2, 3], [3, 4], [4, 5]]"#, number_ways(&[vec![1, 2], vec![2, 3], vec![3, 4], vec![4, 5]]), 5);
}

#[test]
fn ten_people_every_hat() {
    let h: Vec<Vec<u8>> = vec![(1..=40).collect(); 10];
    check!(r#"10 people, each likes hats 1..=40"#, number_ways(&h), 502_474_470);
}

#[test]
fn ten_people_mixed() {
    let h: Vec<Vec<u8>> = (0..10u32).map(|p| (1..=40u8).filter(|&x| x as u32 * (p + 3) % 7 < 4).collect()).collect();
    check!(r#"person p likes hat x when x·(p + 3) % 7 < 4"#, number_ways(&h), 664_239_731);
}

#[test]
fn random_vs_brute_force() {
    fn count(hats: &[Vec<u8>], used: &mut [bool; 41]) -> u64 {
        let Some((first, rest)) = hats.split_first() else { return 1 };
        let mut total = 0;
        for &h in first {
            if !used[h as usize] {
                used[h as usize] = true;
                total += count(rest, used);
                used[h as usize] = false;
            }
        }
        total
    }
    let mut rng = anneal_prelude::Rng::new(1250);
    for _ in 0..300 {
        let n = rng.below(6);
        let hats: Vec<Vec<u8>> = (0..n).map(|_| (1..=8u8).filter(|_| rng.bool()).collect()).collect();
        check!(format!("hats = {hats:?}"), number_ways(&hats), count(&hats, &mut [false; 41]));
    }
}
