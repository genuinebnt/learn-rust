use solution::*;

/// Plays `moves` on n disks that start on peg 0; the number of moves if they are legal and end on peg 2.
fn replay(n: u32, moves: &[(u8, u8)]) -> Result<usize, String> {
    let mut pegs: Vec<Vec<u32>> = vec![(1..=n).rev().collect(), Vec::new(), Vec::new()];
    for (i, &(from, to)) in moves.iter().enumerate() {
        if from > 2 || to > 2 || from == to {
            return Err(format!("move {i} ({from}, {to}) is not a move between two pegs"));
        }
        let Some(&disk) = pegs[from as usize].last() else {
            return Err(format!("move {i} takes from empty peg {from}"));
        };
        if pegs[to as usize].last().is_some_and(|&top| top < disk) {
            return Err(format!("move {i} puts disk {disk} on a smaller disk"));
        }
        pegs[from as usize].pop();
        pegs[to as usize].push(disk);
    }
    if pegs[2].len() != n as usize {
        return Err("not every disk ended on peg 2".into());
    }
    Ok(moves.len())
}

#[test]
fn four_disks() {
    check!(r#"n = 4"#, hanoi(4), vec![(0, 1), (0, 2), (1, 2), (0, 1), (2, 0), (2, 1), (0, 1), (0, 2), (1, 2), (1, 0), (2, 0), (1, 2), (0, 1), (0, 2), (1, 2)]);
}

#[test]
fn no_disks() {
    check!(r#"n = 0"#, hanoi(0), Vec::<(u8, u8)>::new());
}

#[test]
fn one_disk() {
    check!(r#"n = 1"#, hanoi(1), vec![(0, 2)]);
}

#[test]
fn five_disks_legal() {
    check!(r#"n = 5"#, replay(5, &hanoi(5)), Ok(31));
}

#[test]
fn six_disks_legal() {
    check!(r#"n = 6"#, replay(6, &hanoi(6)), Ok(63));
}

#[test]
fn seven_disks_first_and_last() {
    check!(r#"n = 7"#, { let m = hanoi(7); (m[0], m[63], m[126]) }, ((0, 2), (0, 2), (0, 2)));
}

#[test]
fn eight_disks_first_move() {
    check!(r#"n = 8 (even: the smallest disk goes to the spare first)"#, hanoi(8)[0], (0, 1));
}

#[test]
fn twelve_disks_legal() {
    check!(r#"n = 12"#, replay(12, &hanoi(12)), Ok(4095));
}

/// The classic iterative solution: move the smallest disk around a fixed cycle, then make the only other legal move.
fn iterative(n: u32) -> Vec<(u8, u8)> {
    let mut pegs: Vec<Vec<u32>> = vec![(1..=n).rev().collect(), Vec::new(), Vec::new()];
    let cycle: [u8; 3] = if n % 2 == 0 { [0, 1, 2] } else { [0, 2, 1] };
    let mut small = 0;
    let mut moves = Vec::new();
    for i in 0..(1usize << n) - 1 {
        if i % 2 == 0 {
            let (a, b) = (cycle[small], cycle[(small + 1) % 3]);
            let d = pegs[a as usize].pop().unwrap();
            pegs[b as usize].push(d);
            moves.push((a, b));
            small = (small + 1) % 3;
        } else {
            let others: Vec<u8> = (0..3).filter(|&p| p != cycle[small]).collect();
            let (x, y) = (others[0], others[1]);
            let (tx, ty) = (pegs[x as usize].last().copied(), pegs[y as usize].last().copied());
            let (a, b) = match (tx, ty) {
                (Some(p), Some(q)) if p < q => (x, y),
                (Some(_), Some(_)) => (y, x),
                (Some(_), None) => (x, y),
                _ => (y, x),
            };
            let d = pegs[a as usize].pop().unwrap();
            pegs[b as usize].push(d);
            moves.push((a, b));
        }
    }
    moves
}

#[test]
fn random_vs_iterative() {
    let mut rng = anneal_prelude::Rng::new(1104);
    for _ in 0..40 {
        let n = rng.int(0, 11) as u32;
        check!(format!("n = {n}"), hanoi(n), iterative(n));
    }
}

#[test]
fn scale_20_disks() {
    check!("n = 20", replay(20, &hanoi(20)), Ok((1 << 20) - 1));
}
