pub fn quicksort(mut v: &mut [i32]) {
    while v.len() > 1 {
        let p = partition(v);
        // `take` moves the slice out of `v` so its halves can be stored back into `v`.
        let (left, right) = std::mem::take(&mut v).split_at_mut(p + 1);
        // Recurse on the smaller half and loop on the larger: O(log n) stack.
        if left.len() < right.len() {
            quicksort(left);
            v = right;
        } else {
            quicksort(right);
            v = left;
        }
    }
}

/// Hoare partition. Returns j with v[..=j] ≤ pivot ≤ v[j+1..]; both sides are non-empty.
fn partition(v: &mut [i32]) -> usize {
    let pivot = v[(v.len() - 1) / 2];
    let (mut i, mut j) = (0, v.len() - 1);
    loop {
        while v[i] < pivot {
            i += 1;
        }
        while v[j] > pivot {
            j -= 1;
        }
        if i >= j {
            return j;
        }
        v.swap(i, j);
        i += 1;
        j -= 1;
    }
}
