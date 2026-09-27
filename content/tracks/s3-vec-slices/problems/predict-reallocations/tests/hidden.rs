use solution::*;

#[test]
fn with_capacity_never_reallocates() {
    let mut v: Vec<u32> = Vec::with_capacity(100);
    let cap = v.capacity();
    v.extend(0..100u32);
    check!("Vec::with_capacity(100) then 100 pushes", (REALLOCATIONS > 0, v.capacity() == cap), (true, true));
}

fn run() -> (usize, usize) {
    let mut v: Vec<u32> = Vec::new();
    let (mut changes, mut cap) = (0, v.capacity());
    for i in 0..100 {
        v.push(i);
        if v.capacity() != cap {
            changes += 1;
            cap = v.capacity();
        }
    }
    (changes, v.capacity())
}

#[test]
fn both_constants() {
    check!("(REALLOCATIONS, FINAL_CAPACITY) for 100 pushes", (REALLOCATIONS, FINAL_CAPACITY), run());
}

#[test]
fn first_capacity_is_not_one() {
    check!("FINAL_CAPACITY >> (REALLOCATIONS - 1): the first capacity", FINAL_CAPACITY >> REALLOCATIONS.saturating_sub(1), 4);
}

#[test]
fn not_an_exact_fit() {
    check!("FINAL_CAPACITY != 100", FINAL_CAPACITY != 100, true);
}

#[test]
fn doubling_steps() {
    check!("REALLOCATIONS as doublings from 4", REALLOCATIONS, (FINAL_CAPACITY / 4).trailing_zeros() as usize + 1);
}

#[test]
fn fewer_than_ten() {
    check!("REALLOCATIONS < 10", REALLOCATIONS < 10, true);
}

#[test]
fn capacity_below_double() {
    check!("FINAL_CAPACITY < 200", FINAL_CAPACITY < 200, true);
}

#[test]
fn reallocations_exact() {
    check!("REALLOCATIONS", REALLOCATIONS, run().0);
}
