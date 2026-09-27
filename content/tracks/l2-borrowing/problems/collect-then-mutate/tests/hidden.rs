use solution::*;

use std::alloc::{GlobalAlloc, Layout, System};
use std::cell::Cell;

struct CountingAlloc;

thread_local! {
    static ALLOCS: Cell<usize> = const { Cell::new(0) };
}

unsafe impl GlobalAlloc for CountingAlloc {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        let _ = ALLOCS.try_with(|n| n.set(n.get() + 1));
        unsafe { System.alloc(layout) }
    }

    unsafe fn realloc(&self, ptr: *mut u8, layout: Layout, new_size: usize) -> *mut u8 {
        let _ = ALLOCS.try_with(|n| n.set(n.get() + 1));
        unsafe { System.realloc(ptr, layout, new_size) }
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        unsafe { System.dealloc(ptr, layout) }
    }
}

#[global_allocator]
static GLOBAL: CountingAlloc = CountingAlloc;

/// Runs `f` and returns its result with the number of allocations (and reallocations) it made.
fn allocs<R>(f: impl FnOnce() -> R) -> (R, usize) {
    let before = ALLOCS.with(|n| n.get());
    let r = f();
    (r, ALLOCS.with(|n| n.get()) - before)
}

#[test]
fn empty() {
    check!(r#"4x3, alive [], 2 steps"#, { let mut l = Life::new(4, 3, &[]); for _ in 0..2 { l.step(); } l.alive() }, vec![]);
}

#[test]
fn one_by_one() {
    check!(r#"1x1, alive [(0, 0)], 1 steps"#, { let mut l = Life::new(1, 1, &[(0, 0)]); for _ in 0..1 { l.step(); } l.alive() }, vec![]);
}

#[test]
fn corner_birth() {
    check!(r#"2x2, alive [(0, 0), (1, 0), (0, 1)], 1 steps"#, { let mut l = Life::new(2, 2, &[(0, 0), (1, 0), (0, 1)]); for _ in 0..1 { l.step(); } l.alive() }, vec![(0, 0), (1, 0), (0, 1), (1, 1)]);
}

#[test]
fn full_3x3() {
    check!(r#"3x3, alive [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)], 1 steps"#, { let mut l = Life::new(3, 3, &[(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2)]); for _ in 0..1 { l.step(); } l.alive() }, vec![(0, 0), (2, 0), (0, 2), (2, 2)]);
}

#[test]
fn glider_hits_wall() {
    check!(r#"5x5, alive [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)], 12 steps"#, { let mut l = Life::new(5, 5, &[(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]); for _ in 0..12 { l.step(); } l.alive() }, vec![(3, 3), (4, 3), (3, 4), (4, 4)]);
}

#[test]
fn toad() {
    check!(r#"6x6, alive [(2, 2), (3, 2), (4, 2), (1, 3), (2, 3), (3, 3)], 1 steps"#, { let mut l = Life::new(6, 6, &[(2, 2), (3, 2), (4, 2), (1, 3), (2, 3), (3, 3)]); for _ in 0..1 { l.step(); } l.alive() }, vec![(3, 1), (1, 2), (4, 2), (1, 3), (4, 3), (2, 4)]);
}

#[test]
fn wide_row() {
    check!(r#"7x2, alive [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)], 2 steps"#, { let mut l = Life::new(7, 2, &[(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)]); for _ in 0..2 { l.step(); } l.alive() }, vec![(1, 0), (5, 0), (1, 1), (5, 1)]);
}

#[test]
fn tall() {
    check!(r#"1x5, alive [(0, 1), (0, 2), (0, 3)], 1 steps"#, { let mut l = Life::new(1, 5, &[(0, 1), (0, 2), (0, 3)]); for _ in 0..1 { l.step(); } l.alive() }, vec![(0, 2)]);
}

fn model(w: usize, h: usize, cells: &[bool]) -> Vec<bool> {
    let mut out = vec![false; w * h];
    for y in 0..h {
        for x in 0..w {
            let mut n = 0;
            for dy in -1i64..=1 {
                for dx in -1i64..=1 {
                    let (nx, ny) = (x as i64 + dx, y as i64 + dy);
                    if (dx, dy) != (0, 0) && nx >= 0 && ny >= 0 && (nx as usize) < w && (ny as usize) < h && cells[ny as usize * w + nx as usize] {
                        n += 1;
                    }
                }
            }
            out[y * w + x] = n == 3 || (cells[y * w + x] && n == 2);
        }
    }
    out
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6221);
    for _ in 0..200 {
        let (w, h) = (1 + rng.below(6), 1 + rng.below(6));
        let alive: Vec<(usize, usize)> = (0..w * h).filter(|_| rng.below(3) == 0).map(|i| (i % w, i / w)).collect();
        let mut cells = vec![false; w * h];
        for &(x, y) in &alive {
            cells[y * w + x] = true;
        }
        let mut l = Life::new(w, h, &alive);
        for s in 1..=3 {
            cells = model(w, h, &cells);
            l.step();
            let want: Vec<(usize, usize)> = (0..w * h).filter(|&i| cells[i]).map(|i| (i % w, i / w)).collect();
            check!(format!("{w}x{h}, alive {alive:?}, {s} steps"), l.alive(), want);
        }
    }
}

#[test]
fn step_does_not_allocate() {
    let alive: Vec<(usize, usize)> = (0..300).flat_map(|y| (0..300).filter(move |x| (x * 7 + y * 13) % 5 < 2).map(move |x| (x, y))).collect();
    let mut l = Life::new(300, 300, &alive);
    let (_, n) = allocs(|| {
        for _ in 0..4 {
            l.step();
        }
    });
    check!("300x300 grid, 4 steps: allocations", n, 0);
    let mut cells = vec![false; 300 * 300];
    for &(x, y) in &alive {
        cells[y * 300 + x] = true;
    }
    for _ in 0..4 {
        cells = model(300, 300, &cells);
    }
    check!("300x300 grid, 4 steps: live cells", l.alive().len(), cells.iter().filter(|&&c| c).count());
}
