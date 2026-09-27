from author import T, write_track

P = []

# ---------------------------------------------------------------- first greedy

P.append(dict(
    slug="assign-cookies", title="Assign cookies", level="easy", stage="first-greedy", tags=["greedy", "sorting", "two pointers"],
    companies=["Amazon"],
    teaches=["Sort both sides, then match the smallest cookie that still works.", "`to_vec()` plus `sort_unstable()` when the caller's slice must stay untouched."],
    statement="""
        Child `i` is happy with any cookie of size at least `greed[i]`. Each child gets at most one cookie and
        each cookie goes to at most one child. Return the largest number of children you can make happy.
    """,
    examples=[("greed = [1, 2, 3], cookies = [1, 1]", "1"), ("greed = [1, 2], cookies = [1, 2, 3]", "2")],
    constraints=["0 ≤ greed.len(), cookies.len() ≤ 2·10⁵", "1 ≤ greed[i], cookies[j] ≤ 2³² − 1"],
    starter="""
        pub fn find_content_children(greed: &[u32], cookies: &[u32]) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn find_content_children(greed: &[u32], cookies: &[u32]) -> usize {
            let mut greed = greed.to_vec();
            let mut cookies = cookies.to_vec();
            greed.sort_unstable();
            cookies.sort_unstable();
            let mut happy = 0;
            for &size in &cookies {
                if happy < greed.len() && size >= greed[happy] {
                    happy += 1;
                }
            }
            happy
        }
    """,
    visible=[
        T("leetcode_one_fits", "greed = [1, 2, 3], cookies = [1, 1]", "find_content_children(&[1, 2, 3], &[1, 1])", "1"),
        T("leetcode_all_fit", "greed = [1, 2], cookies = [1, 2, 3]", "find_content_children(&[1, 2], &[1, 2, 3])", "2"),
        T("no_cookies", "greed = [1, 2], cookies = []", "find_content_children(&[1, 2], &[])", "0"),
        T("no_children", "greed = [], cookies = [4]", "find_content_children(&[], &[4])", "0"),
        T("equal_size_is_enough", "greed = [5], cookies = [5]", "find_content_children(&[5], &[5])", "1"),
        T("one_cookie_per_child", "greed = [1], cookies = [1, 1, 1]", "find_content_children(&[1], &[1, 1, 1])", "1"),
        T("inputs_unsorted", "greed = [3, 1, 2], cookies = [3, 1]", "find_content_children(&[3, 1, 2], &[3, 1])", "2"),
    ],
    hidden=[
        T("too_small", "greed = [2], cookies = [1]", "find_content_children(&[2], &[1])", "0"),
        T("both_empty", "greed = [], cookies = []", "find_content_children(&[], &[])", "0"),
        T("duplicates", "greed = [2, 2, 2], cookies = [2, 2]", "find_content_children(&[2, 2, 2], &[2, 2])", "2"),
        T("max_values", "greed = [4294967295, 1], cookies = [4294967295]", "find_content_children(&[u32::MAX, 1], &[u32::MAX])", "1"),
        T("big_cookie_not_wasted", "greed = [1, 3], cookies = [3, 1]", "find_content_children(&[1, 3], &[3, 1])", "2"),
        T("all_cookies_too_small", "greed = [10, 20], cookies = [1, 2, 3]", "find_content_children(&[10, 20], &[1, 2, 3])", "0"),
        T("more_cookies_than_children", "greed = [2, 1], cookies = [1, 1, 2, 2, 3]", "find_content_children(&[2, 1], &[1, 1, 2, 2, 3])", "2"),
        T("greedy_child_skipped", "greed = [1, 2, 100], cookies = [1, 2, 3]", "find_content_children(&[1, 2, 100], &[1, 2, 3])", "2"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn best(greed: &[u32], cookies: &[u32], used: &mut Vec<bool>) -> usize {
                let Some((&g, rest)) = greed.split_first() else { return 0 };
                let mut out = best(rest, cookies, used);
                for j in 0..cookies.len() {
                    if !used[j] && cookies[j] >= g {
                        used[j] = true;
                        out = out.max(1 + best(rest, cookies, used));
                        used[j] = false;
                    }
                }
                out
            }
            let mut rng = anneal_prelude::Rng::new(801);
            for _ in 0..300 {
                let n = rng.below(6);
                let m = rng.below(6);
                let greed: Vec<u32> = rng.vec(n, 1, 8);
                let cookies: Vec<u32> = rng.vec(m, 1, 8);
                let want = best(&greed, &cookies, &mut vec![false; m]);
                check!(format!("greed = {greed:?}, cookies = {cookies:?}"), find_content_children(&greed, &cookies), want);
            }
        }

        #[test]
        fn scale_200k() {
            let greed: Vec<u32> = (1..=200_000).collect();
            let cookies: Vec<u32> = (1..=200_000).rev().collect();
            check!("greed = 1..=200000, cookies = 200000 down to 1", find_content_children(&greed, &cookies), 200_000);
        }
        """,
    ],
    wrong=dict(
        quadratic_search="""
            pub fn find_content_children(greed: &[u32], cookies: &[u32]) -> usize {
                let mut greed = greed.to_vec();
                let mut cookies = cookies.to_vec();
                greed.sort_unstable();
                cookies.sort_unstable();
                let mut used = vec![false; cookies.len()];
                let mut happy = 0;
                for &g in &greed {
                    if let Some(j) = (0..cookies.len()).find(|&j| !used[j] && cookies[j] >= g) {
                        used[j] = true;
                        happy += 1;
                    }
                }
                happy
            }
        """,
        first_fit_unsorted="""
            pub fn find_content_children(greed: &[u32], cookies: &[u32]) -> usize {
                let mut used = vec![false; cookies.len()];
                let mut happy = 0;
                for &g in greed {
                    if let Some(j) = (0..cookies.len()).find(|&j| !used[j] && cookies[j] >= g) {
                        used[j] = true;
                        happy += 1;
                    }
                }
                happy
            }
        """,
    ),
    hints=[("approach", "The least greedy child is the easiest to please. Give each cookie, smallest first, to the least greedy child it satisfies."),
           ("rust", "Copy each slice with `to_vec()`, `sort_unstable()` both, then walk the cookies with one index into the children.")],
    notes=("After sorting, a cookie too small for the least greedy waiting child is too small for everyone, so skip it; otherwise using it on that child never hurts (exchange argument).", "O(n log n + m log m)", "O(n + m) for the sorted copies"),
    follow_up="If each child could take several cookies whose sizes add up to their greed, is greedy still optimal?",
    related=["D2", "S3"],
))

P.append(dict(
    slug="lemonade-change", title="Lemonade change", level="easy", stage="first-greedy", tags=["greedy", "simulation"],
    companies=["Amazon"],
    teaches=["Greedy means spending the least flexible resource first.", "Early `return false` from inside a `for` loop."],
    statement="""
        Lemonade costs 5. Customers arrive in the order of `bills`, each paying with one 5, 10 or 20 bill, and
        you must hand back exact change straight away using only bills taken earlier. You start with no money.
        Return `true` if every customer gets correct change.
    """,
    examples=[("bills = [5, 5, 5, 10, 20]", "true"), ("bills = [5, 5, 10, 10, 20]", "false")],
    constraints=["0 ≤ bills.len() ≤ 2·10⁵", "bills[i] ∈ {5, 10, 20}"],
    starter="""
        pub fn lemonade_change(bills: &[u32]) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn lemonade_change(bills: &[u32]) -> bool {
            let (mut fives, mut tens) = (0u32, 0u32);
            for &bill in bills {
                match bill {
                    5 => fives += 1,
                    10 => {
                        if fives == 0 {
                            return false;
                        }
                        fives -= 1;
                        tens += 1;
                    }
                    _ => {
                        if tens > 0 && fives > 0 {
                            tens -= 1;
                            fives -= 1;
                        } else if fives >= 3 {
                            fives -= 3;
                        } else {
                            return false;
                        }
                    }
                }
            }
            true
        }
    """,
    visible=[
        T("leetcode_yes", "bills = [5, 5, 5, 10, 20]", "lemonade_change(&[5, 5, 5, 10, 20])", "true"),
        T("leetcode_no", "bills = [5, 5, 10, 10, 20]", "lemonade_change(&[5, 5, 10, 10, 20])", "false"),
        T("no_customers", "bills = []", "lemonade_change(&[])", "true"),
        T("first_pays_ten", "bills = [10]", "lemonade_change(&[10])", "false"),
        T("three_fives_for_twenty", "bills = [5, 5, 5, 20]", "lemonade_change(&[5, 5, 5, 20])", "true"),
        T("give_the_ten_first", "bills = [5, 5, 5, 5, 10, 20, 10, 10]", "lemonade_change(&[5, 5, 5, 5, 10, 20, 10, 10])", "true"),
    ],
    hidden=[
        T("single_five", "bills = [5]", "lemonade_change(&[5])", "true"),
        T("first_pays_twenty", "bills = [20]", "lemonade_change(&[20])", "false"),
        T("ten_but_no_five", "bills = [5, 10, 20]", "lemonade_change(&[5, 10, 20])", "false"),
        T("ten_and_five", "bills = [5, 5, 10, 20]", "lemonade_change(&[5, 5, 10, 20])", "true"),
        T("fives_run_out", "bills = [5, 5, 5, 20, 20]", "lemonade_change(&[5, 5, 5, 20, 20])", "false"),
        T("later_five_too_late", "bills = [10, 5]", "lemonade_change(&[10, 5])", "false"),
        T("twenties_are_not_change", "bills = [5, 5, 5, 20, 10]", "lemonade_change(&[5, 5, 5, 20, 10])", "false"),
        T("many_fives", "bills = [5; 1000]", "lemonade_change(&vec![5; 1000])", "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            // Tries both ways of changing every 20.
            fn ok(bills: &[u32], fives: i32, tens: i32) -> bool {
                let Some((&b, rest)) = bills.split_first() else { return true };
                match b {
                    5 => ok(rest, fives + 1, tens),
                    10 => fives > 0 && ok(rest, fives - 1, tens + 1),
                    _ => (tens > 0 && fives > 0 && ok(rest, fives - 1, tens - 1)) || (fives >= 3 && ok(rest, fives - 3, tens)),
                }
            }
            let mut rng = anneal_prelude::Rng::new(802);
            for _ in 0..400 {
                let n = rng.below(13);
                let bills: Vec<u32> = (0..n).map(|_| *rng.pick(&[5, 5, 5, 10, 10, 20])).collect();
                check!(format!("bills = {bills:?}"), lemonade_change(&bills), ok(&bills, 0, 0));
            }
        }

        #[test]
        fn scale_200k() {
            let bills: Vec<u32> = [5, 5, 5, 10, 20].repeat(40_000);
            let mut late_ten = bills.clone();
            late_ten.insert(0, 10);
            check!("bills = [5, 5, 5, 10, 20] × 40000, then with a 10 in front", (lemonade_change(&bills), lemonade_change(&late_ten)), (true, false));
        }
        """,
    ],
    wrong=dict(
        fives_first="""
            pub fn lemonade_change(bills: &[u32]) -> bool {
                let (mut fives, mut tens) = (0u32, 0u32);
                for &bill in bills {
                    match bill {
                        5 => fives += 1,
                        10 => {
                            if fives == 0 {
                                return false;
                            }
                            fives -= 1;
                            tens += 1;
                        }
                        _ => {
                            if fives >= 3 {
                                fives -= 3;
                            } else if tens > 0 && fives > 0 {
                                tens -= 1;
                                fives -= 1;
                            } else {
                                return false;
                            }
                        }
                    }
                }
                true
            }
        """,
        checks_only_at_end="""
            pub fn lemonade_change(bills: &[u32]) -> bool {
                let (mut fives, mut tens) = (0i32, 0i32);
                for &bill in bills {
                    match bill {
                        5 => fives += 1,
                        10 => {
                            fives -= 1;
                            tens += 1;
                        }
                        _ => {
                            if tens > 0 {
                                tens -= 1;
                                fives -= 1;
                            } else {
                                fives -= 3;
                            }
                        }
                    }
                }
                fives >= 0 && tens >= 0
            }
        """,
    ),
    hints=[("approach", "Only the count of 5s and 10s in the till matters. A 20 can never be given back as change."),
           ("edge case", "For a 20, give a 10 and a 5 when you can: a 10 only helps with 20s, while 5s help with everyone.")],
    notes=("Keep two counters. Paying 15 with 10 + 5 keeps more 5s than 5 + 5 + 5, and 5s are strictly more useful, so that choice is always safe.", "O(n)", "O(1)"),
    follow_up="If lemonade cost 5 and bills could be any of 5, 10, 20, 50, would the same greedy rule still work?",
    related=["S1"],
))

P.append(dict(
    slug="can-place-flowers", title="Can place flowers", level="easy", stage="first-greedy", tags=["greedy", "slices"],
    companies=["Meta", "Amazon", "Google", "LinkedIn"],
    teaches=["`slice.get(i + 1)` reads a neighbour that might be past the end without panicking.", "Planting as early as possible never blocks a better plan."],
    statement="""
        A flowerbed is a row of plots; `bed[i]` is `true` when plot `i` already has a flower. No two flowers may
        sit in adjacent plots. Return `true` if you can plant `n` more flowers without breaking that rule.
        Plots past either end count as empty.
    """,
    examples=[("bed = [1, 0, 0, 0, 1], n = 1", "true"), ("bed = [1, 0, 0, 0, 1], n = 2", "false")],
    constraints=["0 ≤ bed.len() ≤ 2·10⁵", "bed never has two adjacent flowers", "0 ≤ n ≤ bed.len() + 1"],
    starter="""
        pub fn can_place_flowers(bed: &[bool], n: usize) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn can_place_flowers(bed: &[bool], n: usize) -> bool {
            let mut planted = 0;
            let mut left_full = false;
            for i in 0..bed.len() {
                if bed[i] {
                    left_full = true;
                    continue;
                }
                let right_full = bed.get(i + 1).copied().unwrap_or(false);
                if !left_full && !right_full {
                    planted += 1;
                    left_full = true;
                } else {
                    left_full = false;
                }
            }
            planted >= n
        }
    """,
    visible=[
        """
        /// "10001" → [true, false, false, false, true]
        fn bed(s: &str) -> Vec<bool> {
            s.bytes().map(|b| b == b'1').collect()
        }
        """,
        T("leetcode_one", "bed = [1, 0, 0, 0, 1], n = 1", 'can_place_flowers(&bed("10001"), 1)', "true"),
        T("leetcode_two", "bed = [1, 0, 0, 0, 1], n = 2", 'can_place_flowers(&bed("10001"), 2)', "false"),
        T("empty_bed_zero", "bed = [], n = 0", "can_place_flowers(&[], 0)", "true"),
        T("empty_bed_one", "bed = [], n = 1", "can_place_flowers(&[], 1)", "false"),
        T("single_empty_plot", "bed = [0], n = 1", 'can_place_flowers(&bed("0"), 1)', "true"),
        T("ends_count_as_empty", "bed = [0, 0, 1, 0, 0], n = 2", 'can_place_flowers(&bed("00100"), 2)', "true"),
        T("zero_flowers_always_fit", "bed = [1], n = 0", 'can_place_flowers(&bed("1"), 0)', "true"),
    ],
    hidden=[
        """
        fn bed(s: &str) -> Vec<bool> {
            s.bytes().map(|b| b == b'1').collect()
        }
        """,
        T("three_empty", "bed = [0, 0, 0], n = 2", 'can_place_flowers(&bed("000"), 2)', "true"),
        T("two_empty", "bed = [0, 0], n = 2", 'can_place_flowers(&bed("00"), 2)', "false"),
        T("left_edge", "bed = [0, 0, 1], n = 1", 'can_place_flowers(&bed("001"), 1)', "true"),
        T("right_edge", "bed = [1, 0, 0], n = 1", 'can_place_flowers(&bed("100"), 1)', "true"),
        T("gap_of_one", "bed = [1, 0, 1], n = 1", 'can_place_flowers(&bed("101"), 1)', "false"),
        T("between_is_blocked", "bed = [0, 1, 0], n = 1", 'can_place_flowers(&bed("010"), 1)', "false"),
        T("five_empty", "bed = [0, 0, 0, 0, 0], n = 3", 'can_place_flowers(&bed("00000"), 3)', "true"),
        T("four_inside", "bed = [1, 0, 0, 0, 0, 1], n = 2", 'can_place_flowers(&bed("100001"), 2)', "false"),
        T("exactly_enough", "bed = [0, 0, 0, 1, 0, 0, 0, 0], n = 3", 'can_place_flowers(&bed("00010000"), 3)', "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(803);
            for _ in 0..300 {
                let len = rng.below(13);
                let mut plots = vec![false; len];
                for i in 0..len {
                    if rng.below(3) == 0 && (i == 0 || !plots[i - 1]) {
                        plots[i] = true;
                    }
                }
                // The most flowers any set of empty plots can take.
                let mut most = 0;
                for mask in 0u32..1 << len {
                    let ok = (0..len).all(|i| mask >> i & 1 == 0 || !plots[i])
                        && (0..len).all(|i| {
                            let full = |j: usize| plots[j] || mask >> j & 1 == 1;
                            !(i + 1 < len && full(i) && full(i + 1))
                        });
                    if ok {
                        most = most.max(mask.count_ones() as usize);
                    }
                }
                let n = rng.below(len + 2);
                let shown: String = plots.iter().map(|&p| if p { '1' } else { '0' }).collect();
                check!(format!("bed = {shown}, n = {n}"), can_place_flowers(&plots, n), n <= most);
            }
        }

        #[test]
        fn scale_200k() {
            let plots = vec![false; 200_000];
            check!("bed = 200000 empty plots, n = 100000 and 100001", (can_place_flowers(&plots, 100_000), can_place_flowers(&plots, 100_001)), (true, false));
        }
        """,
    ],
    wrong=dict(
        rescan_per_flower="""
            pub fn can_place_flowers(bed: &[bool], n: usize) -> bool {
                let mut bed = bed.to_vec();
                for _ in 0..n {
                    let spot = (0..bed.len()).find(|&i| {
                        !bed[i] && (i == 0 || !bed[i - 1]) && (i + 1 == bed.len() || !bed[i + 1])
                    });
                    match spot {
                        Some(i) => bed[i] = true,
                        None => return false,
                    }
                }
                true
            }
        """,
        edges_count_as_full="""
            pub fn can_place_flowers(bed: &[bool], n: usize) -> bool {
                let mut bed = bed.to_vec();
                let mut planted = 0;
                for i in 0..bed.len() {
                    let left = i > 0 && !bed[i - 1];
                    let right = i + 1 < bed.len() && !bed[i + 1];
                    if !bed[i] && left && right {
                        bed[i] = true;
                        planted += 1;
                    }
                }
                planted >= n
            }
        """,
        strictly_more="""
            pub fn can_place_flowers(bed: &[bool], n: usize) -> bool {
                let mut bed = bed.to_vec();
                let mut planted = 0;
                for i in 0..bed.len() {
                    let left = i == 0 || !bed[i - 1];
                    let right = i + 1 == bed.len() || !bed[i + 1];
                    if !bed[i] && left && right {
                        bed[i] = true;
                        planted += 1;
                    }
                }
                planted > n || n == 0
            }
        """,
    ),
    hints=[("approach", "Walk left to right and plant in every empty plot whose neighbours are both empty. Planting early never costs you a spot later."),
           ("rust", "`bed.get(i + 1).copied().unwrap_or(false)` treats the plot past the end as empty; keep a flag for the left neighbour so you don't need to mutate the input."),
           ("edge case", "The first and last plots only have one neighbour, and `n = 0` is always possible.")],
    notes=("Planting at the leftmost legal plot leaves at least as much room to the right as any other choice, so one greedy pass finds the maximum.", "O(n)", "O(1)"),
    follow_up="How would you answer many queries of different `n` on the same bed without rescanning?",
    related=["S3"],
))

P.append(dict(
    slug="meeting-rooms", title="Meeting rooms", level="easy", stage="first-greedy", tags=["intervals", "sorting", "Blind 75"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "Bloomberg"],
    teaches=["`sort_unstable_by_key(|m| m.0)` orders tuples by one field.", "`windows(2)` compares each pair of neighbours."],
    statement="""
        Each meeting is `(start, end)` with `start < end`, and it covers the time from `start` up to but not
        including `end`, so one meeting may start the moment another ends. Return `true` if one person can
        attend every meeting, that is, no two meetings overlap.
    """,
    examples=[("meetings = [(0, 30), (5, 10), (15, 20)]", "false"), ("meetings = [(7, 10), (2, 4)]", "true")],
    constraints=["0 ≤ meetings.len() ≤ 2·10⁵", "start < end, both any i32"],
    starter="""
        pub fn can_attend_all(meetings: &[(i32, i32)]) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn can_attend_all(meetings: &[(i32, i32)]) -> bool {
            let mut sorted = meetings.to_vec();
            sorted.sort_unstable_by_key(|m| m.0);
            sorted.windows(2).all(|w| w[0].1 <= w[1].0)
        }
    """,
    visible=[
        T("leetcode_clash", "meetings = [(0, 30), (5, 10), (15, 20)]", "can_attend_all(&[(0, 30), (5, 10), (15, 20)])", "false"),
        T("leetcode_fine", "meetings = [(7, 10), (2, 4)]", "can_attend_all(&[(7, 10), (2, 4)])", "true"),
        T("no_meetings", "meetings = []", "can_attend_all(&[])", "true"),
        T("one_meeting", "meetings = [(1, 2)]", "can_attend_all(&[(1, 2)])", "true"),
        T("back_to_back_is_fine", "meetings = [(1, 5), (5, 8)]", "can_attend_all(&[(1, 5), (5, 8)])", "true"),
        T("unsorted_overlap", "meetings = [(10, 20), (1, 11)]", "can_attend_all(&[(10, 20), (1, 11)])", "false"),
    ],
    hidden=[
        T("nested", "meetings = [(1, 10), (2, 3)]", "can_attend_all(&[(1, 10), (2, 3)])", "false"),
        T("same_start", "meetings = [(1, 2), (1, 3)]", "can_attend_all(&[(1, 2), (1, 3)])", "false"),
        T("identical", "meetings = [(1, 2), (1, 2)]", "can_attend_all(&[(1, 2), (1, 2)])", "false"),
        T("negative_times", "meetings = [(-5, -1), (-1, 3)]", "can_attend_all(&[(-5, -1), (-1, 3)])", "true"),
        T("i32_extremes_touch", "meetings = [(i32::MIN, 0), (0, i32::MAX)]", "can_attend_all(&[(i32::MIN, 0), (0, i32::MAX)])", "true"),
        T("everything_covered", "meetings = [(i32::MIN, i32::MAX), (0, 1)]", "can_attend_all(&[(i32::MIN, i32::MAX), (0, 1)])", "false"),
        T("clash_not_adjacent_in_input", "meetings = [(1, 5), (10, 12), (3, 4)]", "can_attend_all(&[(1, 5), (10, 12), (3, 4)])", "false"),
        T("many_back_to_back", "meetings = [(4, 6), (0, 2), (2, 4), (6, 9)]", "can_attend_all(&[(4, 6), (0, 2), (2, 4), (6, 9)])", "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(804);
            for _ in 0..400 {
                let n = rng.below(7);
                let meetings: Vec<(i32, i32)> = (0..n)
                    .map(|_| {
                        let s = rng.int(-5, 20) as i32;
                        let len = rng.int(1, 6) as i32;
                        (s, s + len)
                    })
                    .collect();
                let want = (0..n).all(|i| (i + 1..n).all(|j| meetings[i].1 <= meetings[j].0 || meetings[j].1 <= meetings[i].0));
                check!(format!("meetings = {meetings:?}"), can_attend_all(&meetings), want);
            }
        }

        #[test]
        fn scale_200k() {
            let fine: Vec<(i32, i32)> = (0..200_000).rev().map(|i| (2 * i, 2 * i + 2)).collect();
            let mut clash = fine.clone();
            clash[0].0 -= 1;
            check!("200000 back-to-back meetings in reverse order; then the last one starts 1 early", (can_attend_all(&fine), can_attend_all(&clash)), (true, false));
        }
        """,
    ],
    wrong=dict(
        every_pair="""
            pub fn can_attend_all(meetings: &[(i32, i32)]) -> bool {
                let n = meetings.len();
                (0..n).all(|i| (i + 1..n).all(|j| meetings[i].1 <= meetings[j].0 || meetings[j].1 <= meetings[i].0))
            }
        """,
        touching_overlaps="""
            pub fn can_attend_all(meetings: &[(i32, i32)]) -> bool {
                let mut sorted = meetings.to_vec();
                sorted.sort_unstable_by_key(|m| m.0);
                sorted.windows(2).all(|w| w[0].1 < w[1].0)
            }
        """,
        input_order="""
            pub fn can_attend_all(meetings: &[(i32, i32)]) -> bool {
                meetings.windows(2).all(|w| w[0].1 <= w[1].0 || w[1].1 <= w[0].0)
            }
        """,
    ),
    hints=[("approach", "Sort by start time. Then only neighbours can clash: check each meeting ends by the time the next one starts."),
           ("rust", "Copy with `to_vec()`, `sort_unstable_by_key(|m| m.0)`, then `windows(2).all(|w| w[0].1 <= w[1].0)`."),
           ("edge case", "`end == next start` is not an overlap.")],
    notes=("After sorting by start, if any two meetings overlap then some adjacent pair does, so one pass over neighbours decides it.", "O(n log n)", "O(n) for the sorted copy"),
    follow_up="If they do overlap, how many rooms would you need? (That's Meeting rooms II.)",
    related=["S3", "D7"],
))

P.append(dict(
    slug="maximum-subarray", title="Maximum subarray", level="easy", stage="first-greedy", tags=["Kadane", "greedy", "Blind 75"],
    companies=["Meta", "Apple", "Amazon", "Google", "Microsoft", "LinkedIn", "Bloomberg"],
    teaches=["Kadane's rule: drop a running sum the moment it would only drag the next element down.", "`split_first()?` returns `None` for an empty slice in one step."],
    statement="""
        Return the largest sum of a non-empty contiguous run of `nums`, or `None` when `nums` is empty.
        The sum can be larger than an `i32` holds.
    """,
    examples=[("nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]", "Some(6)"), ("nums = [5, 4, -1, 7, 8]", "Some(23)")],
    constraints=["0 ≤ nums.len() ≤ 2·10⁵", "nums[i] is any i32"],
    starter="""
        pub fn max_subarray(nums: &[i32]) -> Option<i64> {
            todo!()
        }
    """,
    solution="""
        pub fn max_subarray(nums: &[i32]) -> Option<i64> {
            let (&first, rest) = nums.split_first()?;
            let mut best = first as i64;
            let mut current = first as i64;
            for &x in rest {
                let x = x as i64;
                current = (current + x).max(x);
                best = best.max(current);
            }
            Some(best)
        }
    """,
    visible=[
        T("leetcode_mixed", "nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]", "max_subarray(&[-2, 1, -3, 4, -1, 2, 1, -5, 4])", "Some(6)"),
        T("leetcode_single", "nums = [1]", "max_subarray(&[1])", "Some(1)"),
        T("leetcode_whole", "nums = [5, 4, -1, 7, 8]", "max_subarray(&[5, 4, -1, 7, 8])", "Some(23)"),
        T("empty", "nums = []", "max_subarray(&[])", "None"),
        T("all_negative", "nums = [-3, -1, -2]", "max_subarray(&[-3, -1, -2])", "Some(-1)"),
        T("wider_than_i32", "nums = [2147483647, 2147483647]", "max_subarray(&[i32::MAX, i32::MAX])", "Some(4_294_967_294)"),
    ],
    hidden=[
        T("single_negative", "nums = [-7]", "max_subarray(&[-7])", "Some(-7)"),
        T("i32_min", "nums = [-2147483648]", "max_subarray(&[i32::MIN])", "Some(-2_147_483_648)"),
        T("zeros", "nums = [0, 0]", "max_subarray(&[0, 0])", "Some(0)"),
        T("zero_among_negatives", "nums = [-1, 0, -2]", "max_subarray(&[-1, 0, -2])", "Some(0)"),
        T("dip_worth_keeping", "nums = [3, -2, 5]", "max_subarray(&[3, -2, 5])", "Some(6)"),
        T("dip_not_worth_keeping", "nums = [2, -5, 3]", "max_subarray(&[2, -5, 3])", "Some(3)"),
        T("best_at_end", "nums = [8, -19, 5, -4, 20]", "max_subarray(&[8, -19, 5, -4, 20])", "Some(21)"),
        T("min_values", "nums = [i32::MIN; 3]", "max_subarray(&[i32::MIN; 3])", "Some(-2_147_483_648)"),
        T("big_total", "nums = [100000; 200000]", "max_subarray(&vec![100_000; 200_000])", "Some(20_000_000_000)"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(805);
            for _ in 0..400 {
                let n = rng.below(16);
                let nums: Vec<i32> = rng.vec(n, -20, 20);
                let mut want: Option<i64> = None;
                for i in 0..n {
                    for j in i..n {
                        let s: i64 = nums[i..=j].iter().map(|&x| x as i64).sum();
                        want = Some(want.map_or(s, |w| w.max(s)));
                    }
                }
                check!(format!("nums = {nums:?}"), max_subarray(&nums), want);
            }
        }

        #[test]
        fn scale_200k() {
            let nums: Vec<i32> = (0..200_000).map(|i| if i % 2 == 0 { 1_000_000_000 } else { -999_999_999 }).collect();
            check!("nums = [10⁹, -(10⁹ - 1), …] (200000 values)", max_subarray(&nums), Some(1_000_099_999));
        }
        """,
    ],
    wrong=dict(
        every_start="""
            pub fn max_subarray(nums: &[i32]) -> Option<i64> {
                let mut best: Option<i64> = None;
                for i in 0..nums.len() {
                    let mut s = 0i64;
                    for &x in &nums[i..] {
                        s += x as i64;
                        best = Some(best.map_or(s, |b| b.max(s)));
                    }
                }
                best
            }
        """,
        floor_at_zero="""
            pub fn max_subarray(nums: &[i32]) -> Option<i64> {
                if nums.is_empty() {
                    return None;
                }
                let (mut best, mut current) = (0i64, 0i64);
                for &x in nums {
                    current = (current + x as i64).max(0);
                    best = best.max(current);
                }
                Some(best)
            }
        """,
        i32_sum="""
            pub fn max_subarray(nums: &[i32]) -> Option<i64> {
                let (&first, rest) = nums.split_first()?;
                let (mut best, mut current) = (first, first);
                for &x in rest {
                    current = current.wrapping_add(x).max(x);
                    best = best.max(current);
                }
                Some(best as i64)
            }
        """,
    ),
    hints=[("approach", "At each element decide: extend the best run ending just before it, or start fresh here. Start fresh when the previous run's sum is negative."),
           ("rust", "Work in `i64` so the sum can't overflow; `let (&first, rest) = nums.split_first()?;` handles the empty slice."),
           ("edge case", "When every number is negative the answer is the largest single number, not 0.")],
    notes=("`current` is the best sum of a run ending at this element: either the element alone or the element plus the best run ending just before it. The answer is the best `current` seen.", "O(n)", "O(1)"),
    follow_up="How would you also return the start and end indices of the best run?",
    related=["D12", "D2"],
))

P.append(dict(
    slug="best-time-to-buy-and-sell-stock-ii", title="Best time to buy and sell stock II", level="easy", stage="first-greedy", tags=["greedy", "windows"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "Bloomberg"],
    teaches=["A total of many trades equals the sum of every single-day rise.", "Widen to `u64` before summing `u32` values."],
    statement="""
        `prices[i]` is a stock's price on day `i`. You may hold at most one share at a time, but you can buy and
        sell as often as you like, even selling and buying again on the same day. Return the largest total profit.
    """,
    examples=[("prices = [7, 1, 5, 3, 6, 4]", "7"), ("prices = [1, 2, 3, 4, 5]", "4")],
    constraints=["0 ≤ prices.len() ≤ 2·10⁵", "prices[i] is any u32"],
    starter="""
        pub fn max_profit(prices: &[u32]) -> u64 {
            todo!()
        }
    """,
    solution="""
        pub fn max_profit(prices: &[u32]) -> u64 {
            prices.windows(2).map(|w| w[1].saturating_sub(w[0]) as u64).sum()
        }
    """,
    visible=[
        T("leetcode_two_trades", "prices = [7, 1, 5, 3, 6, 4]", "max_profit(&[7, 1, 5, 3, 6, 4])", "7"),
        T("leetcode_rising", "prices = [1, 2, 3, 4, 5]", "max_profit(&[1, 2, 3, 4, 5])", "4"),
        T("leetcode_falling", "prices = [7, 6, 4, 3, 1]", "max_profit(&[7, 6, 4, 3, 1])", "0"),
        T("no_days", "prices = []", "max_profit(&[])", "0"),
        T("one_day", "prices = [5]", "max_profit(&[5])", "0"),
        T("trade_every_rise", "prices = [1, 5, 1, 5]", "max_profit(&[1, 5, 1, 5])", "8"),
    ],
    hidden=[
        T("flat", "prices = [3, 3, 3]", "max_profit(&[3, 3, 3])", "0"),
        T("two_days_up", "prices = [1, 2]", "max_profit(&[1, 2])", "1"),
        T("two_days_down", "prices = [2, 1]", "max_profit(&[2, 1])", "0"),
        T("zigzag", "prices = [2, 1, 2, 0, 1]", "max_profit(&[2, 1, 2, 0, 1])", "2"),
        T("drop_between_rises", "prices = [3, 2, 6, 5, 0, 3]", "max_profit(&[3, 2, 6, 5, 0, 3])", "7"),
        T("zero_to_max", "prices = [0, 4294967295]", "max_profit(&[0, u32::MAX])", "4_294_967_295"),
        T("past_u32", "prices = [0, 4294967295, 0, 4294967295]", "max_profit(&[0, u32::MAX, 0, u32::MAX])", "8_589_934_590"),
        T("plateau_then_rise", "prices = [1, 1, 1, 9]", "max_profit(&[1, 1, 1, 9])", "8"),
        """
        #[test]
        fn random_vs_brute_force() {
            // Every choice of buy/sell/wait on every day.
            fn best(prices: &[u32], holding: Option<u32>) -> i64 {
                let Some((&p, rest)) = prices.split_first() else { return 0 };
                let wait = best(rest, holding);
                let act = match holding {
                    None => best(rest, Some(p)),
                    Some(bought) => p as i64 - bought as i64 + best(rest, None),
                };
                wait.max(act)
            }
            let mut rng = anneal_prelude::Rng::new(806);
            for _ in 0..300 {
                let n = rng.below(10);
                let prices: Vec<u32> = rng.vec(n, 0, 12);
                check!(format!("prices = {prices:?}"), max_profit(&prices), best(&prices, None) as u64);
            }
        }

        #[test]
        fn scale_200k() {
            let prices: Vec<u32> = (0..200_000).map(|i| if i % 2 == 0 { 0 } else { u32::MAX }).collect();
            check!("prices = [0, 4294967295, …] (200000 days)", max_profit(&prices), 429_496_729_500_000);
        }
        """,
    ],
    wrong=dict(
        one_trade="""
            pub fn max_profit(prices: &[u32]) -> u64 {
                let mut low = u32::MAX;
                let mut best = 0u64;
                for &p in prices {
                    low = low.min(p);
                    best = best.max((p - low) as u64);
                }
                best
            }
        """,
        u32_total="""
            pub fn max_profit(prices: &[u32]) -> u64 {
                let mut total = 0u32;
                for w in prices.windows(2) {
                    total = total.wrapping_add(w[1].saturating_sub(w[0]));
                }
                total as u64
            }
        """,
    ),
    hints=[("approach", "Any trade from day i to day j earns the same as the sum of the day-to-day changes between them. Keep only the rises."),
           ("rust", "`prices.windows(2).map(|w| w[1].saturating_sub(w[0]) as u64).sum()` is the whole solution.")],
    notes=("Summing every positive day-to-day change collects each upward move exactly once, which is the most any set of non-overlapping trades can collect.", "O(n)", "O(1)"),
    follow_up="What changes if each sale costs a fixed fee? (Hint: the greedy stops working; a two-state DP does.)",
    related=["D12", "D2"],
))

# ---------------------------------------------------------------- intervals

# Merges closed intervals on a small grid by marking 2·start..=2·end, so touching intervals join and
# (1, 2), (3, 4) stay apart. Used as the brute force in several hidden tests.
GRID_MERGE = """
    fn grid_merge(intervals: &[(i32, i32)]) -> Vec<(i32, i32)> {
        let mut marked = vec![false; 64];
        for &(s, e) in intervals {
            for x in 2 * s..=2 * e {
                marked[x as usize] = true;
            }
        }
        let mut out = Vec::new();
        let mut x = 0;
        while x < marked.len() {
            if marked[x] {
                let start = x;
                while x + 1 < marked.len() && marked[x + 1] {
                    x += 1;
                }
                out.push((start as i32 / 2, x as i32 / 2));
            }
            x += 1;
        }
        out
    }
"""

P.append(dict(
    slug="merge-intervals", title="Merge intervals", level="medium", stage="intervals", tags=["intervals", "sorting", "Blind 75"],
    companies=["Meta", "Apple", "Amazon", "Google", "Microsoft", "Bloomberg"],
    teaches=["Sort tuples, then fold into the output with `last_mut()`.", "A match guard `Some(last) if start <= last.1` merges in place."],
    statement="""
        Each `(start, end)` is a closed interval with `start ≤ end`. Merge every group of overlapping intervals
        and return the result sorted by start. Intervals that share an endpoint, like `(1, 4)` and `(4, 5)`, overlap.
    """,
    examples=[("intervals = [(1, 3), (2, 6), (8, 10), (15, 18)]", "[(1, 6), (8, 10), (15, 18)]"), ("intervals = [(1, 4), (4, 5)]", "[(1, 5)]")],
    constraints=["0 ≤ intervals.len() ≤ 2·10⁵", "start ≤ end, both any i32"],
    starter="""
        pub fn merge(intervals: &[(i32, i32)]) -> Vec<(i32, i32)> {
            todo!()
        }
    """,
    solution="""
        pub fn merge(intervals: &[(i32, i32)]) -> Vec<(i32, i32)> {
            let mut sorted = intervals.to_vec();
            sorted.sort_unstable();
            let mut out: Vec<(i32, i32)> = Vec::with_capacity(sorted.len());
            for (start, end) in sorted {
                match out.last_mut() {
                    Some(last) if start <= last.1 => last.1 = last.1.max(end),
                    _ => out.push((start, end)),
                }
            }
            out
        }
    """,
    visible=[
        T("leetcode_four", "intervals = [(1, 3), (2, 6), (8, 10), (15, 18)]", "merge(&[(1, 3), (2, 6), (8, 10), (15, 18)])", "vec![(1, 6), (8, 10), (15, 18)]"),
        T("leetcode_touching", "intervals = [(1, 4), (4, 5)]", "merge(&[(1, 4), (4, 5)])", "vec![(1, 5)]"),
        T("leetcode_unsorted", "intervals = [(4, 7), (1, 4)]", "merge(&[(4, 7), (1, 4)])", "vec![(1, 7)]"),
        T("empty", "intervals = []", "merge(&[])", "Vec::<(i32, i32)>::new()"),
        T("single", "intervals = [(2, 3)]", "merge(&[(2, 3)])", "vec![(2, 3)]"),
        T("contained", "intervals = [(1, 10), (2, 3)]", "merge(&[(1, 10), (2, 3)])", "vec![(1, 10)]"),
        T("output_sorted", "intervals = [(8, 10), (1, 3), (2, 6)]", "merge(&[(8, 10), (1, 3), (2, 6)])", "vec![(1, 6), (8, 10)]"),
    ],
    hidden=[
        T("points", "intervals = [(5, 5), (5, 5)]", "merge(&[(5, 5), (5, 5)])", "vec![(5, 5)]"),
        T("gap_of_one_stays_apart", "intervals = [(1, 2), (3, 4)]", "merge(&[(1, 2), (3, 4)])", "vec![(1, 2), (3, 4)]"),
        T("negatives", "intervals = [(-3, -1), (-2, 0)]", "merge(&[(-3, -1), (-2, 0)])", "vec![(-3, 0)]"),
        T("i32_extremes", "intervals = [(i32::MIN, 0), (0, i32::MAX)]", "merge(&[(i32::MIN, 0), (0, i32::MAX)])", "vec![(i32::MIN, i32::MAX)]"),
        T("contained_then_longer", "intervals = [(1, 10), (2, 3), (4, 11)]", "merge(&[(1, 10), (2, 3), (4, 11)])", "vec![(1, 11)]"),
        T("chain", "intervals = [(3, 4), (1, 2), (2, 3)]", "merge(&[(3, 4), (1, 2), (2, 3)])", "vec![(1, 4)]"),
        T("duplicates", "intervals = [(1, 3), (1, 3)]", "merge(&[(1, 3), (1, 3)])", "vec![(1, 3)]"),
        T("long_one_last", "intervals = [(2, 3), (5, 6), (1, 10)]", "merge(&[(2, 3), (5, 6), (1, 10)])", "vec![(1, 10)]"),
        GRID_MERGE,
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(807);
            for _ in 0..400 {
                let n = rng.below(8);
                let intervals: Vec<(i32, i32)> = (0..n)
                    .map(|_| {
                        let s = rng.int(0, 25) as i32;
                        let len = rng.int(0, 5) as i32;
                        (s, s + len)
                    })
                    .collect();
                check!(format!("intervals = {intervals:?}"), merge(&intervals), grid_merge(&intervals));
            }
        }

        #[test]
        fn scale_200k() {
            // 199999 separate intervals in reverse order, plus one that joins the first two.
            let mut intervals: Vec<(i32, i32)> = (0..199_999).rev().map(|i| (3 * i, 3 * i + 1)).collect();
            intervals.push((1, 3));
            let out = merge(&intervals);
            check!("(3i, 3i + 1) for i in 0..199999, reversed, plus (1, 3)", (out.len(), out[0], out[1], out[out.len() - 1]), (199_998, (0, 4), (6, 7), (599_994, 599_995)));
        }
        """,
    ],
    wrong=dict(
        scan_all_output="""
            pub fn merge(intervals: &[(i32, i32)]) -> Vec<(i32, i32)> {
                let mut sorted = intervals.to_vec();
                sorted.sort_unstable();
                let mut out: Vec<(i32, i32)> = Vec::new();
                for (start, end) in sorted {
                    match out.iter_mut().find(|m| start <= m.1 && m.0 <= end) {
                        Some(m) => m.1 = m.1.max(end),
                        None => out.push((start, end)),
                    }
                }
                out
            }
        """,
        end_not_max="""
            pub fn merge(intervals: &[(i32, i32)]) -> Vec<(i32, i32)> {
                let mut sorted = intervals.to_vec();
                sorted.sort_unstable();
                let mut out: Vec<(i32, i32)> = Vec::new();
                for (start, end) in sorted {
                    match out.last_mut() {
                        Some(last) if start <= last.1 => last.1 = end,
                        _ => out.push((start, end)),
                    }
                }
                out
            }
        """,
        touching_apart="""
            pub fn merge(intervals: &[(i32, i32)]) -> Vec<(i32, i32)> {
                let mut sorted = intervals.to_vec();
                sorted.sort_unstable();
                let mut out: Vec<(i32, i32)> = Vec::new();
                for (start, end) in sorted {
                    match out.last_mut() {
                        Some(last) if start < last.1 => last.1 = last.1.max(end),
                        _ => out.push((start, end)),
                    }
                }
                out
            }
        """,
    ),
    hints=[("approach", "Sort by start. Each interval either overlaps the last merged one (extend it) or starts a new one."),
           ("rust", "`match out.last_mut() { Some(last) if start <= last.1 => last.1 = last.1.max(end), _ => out.push((start, end)) }`"),
           ("edge case", "Take the max of the ends: an interval can sit entirely inside the last merged one.")],
    notes=("After sorting by start, an interval can only overlap the most recent merged interval, so one pass with `last_mut()` merges everything.", "O(n log n)", "O(n)"),
    follow_up="How would you merge intervals arriving one at a time from a stream, keeping the merged set queryable? (Think `BTreeMap`.)",
    related=["S3", "S4"],
))

P.append(dict(
    slug="insert-interval", title="Insert interval", level="medium", stage="intervals", tags=["intervals", "Blind 75"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "LinkedIn"],
    teaches=["Three phases in one pass: copy what ends before, absorb what overlaps, copy the rest.", "`extend_from_slice(&intervals[i..])` copies the tail at once."],
    statement="""
        `intervals` holds closed intervals sorted by start with no two overlapping or touching. Insert `new`,
        merging it with every interval it overlaps or touches, and return the list, still sorted and non-overlapping.
    """,
    examples=[("intervals = [(1, 3), (6, 9)], new = (2, 5)", "[(1, 5), (6, 9)]")],
    constraints=["0 ≤ intervals.len() ≤ 2·10⁵", "start ≤ end, both any i32"],
    starter="""
        pub fn insert(intervals: &[(i32, i32)], new: (i32, i32)) -> Vec<(i32, i32)> {
            todo!()
        }
    """,
    solution="""
        pub fn insert(intervals: &[(i32, i32)], new: (i32, i32)) -> Vec<(i32, i32)> {
            let mut out = Vec::with_capacity(intervals.len() + 1);
            let (mut lo, mut hi) = new;
            let mut i = 0;
            while i < intervals.len() && intervals[i].1 < lo {
                out.push(intervals[i]);
                i += 1;
            }
            while i < intervals.len() && intervals[i].0 <= hi {
                lo = lo.min(intervals[i].0);
                hi = hi.max(intervals[i].1);
                i += 1;
            }
            out.push((lo, hi));
            out.extend_from_slice(&intervals[i..]);
            out
        }
    """,
    visible=[
        T("leetcode_one_overlap", "intervals = [(1, 3), (6, 9)], new = (2, 5)", "insert(&[(1, 3), (6, 9)], (2, 5))", "vec![(1, 5), (6, 9)]"),
        T("leetcode_three_overlaps", "intervals = [(1, 2), (3, 5), (6, 7), (8, 10), (12, 16)], new = (4, 8)", "insert(&[(1, 2), (3, 5), (6, 7), (8, 10), (12, 16)], (4, 8))", "vec![(1, 2), (3, 10), (12, 16)]"),
        T("into_empty", "intervals = [], new = (5, 7)", "insert(&[], (5, 7))", "vec![(5, 7)]"),
        T("goes_last", "intervals = [(1, 2)], new = (5, 6)", "insert(&[(1, 2)], (5, 6))", "vec![(1, 2), (5, 6)]"),
        T("goes_first", "intervals = [(5, 6)], new = (1, 2)", "insert(&[(5, 6)], (1, 2))", "vec![(1, 2), (5, 6)]"),
        T("touching_merges", "intervals = [(1, 3)], new = (3, 4)", "insert(&[(1, 3)], (3, 4))", "vec![(1, 4)]"),
    ],
    hidden=[
        T("covers_all", "intervals = [(1, 2), (4, 5), (7, 8)], new = (0, 10)", "insert(&[(1, 2), (4, 5), (7, 8)], (0, 10))", "vec![(0, 10)]"),
        T("inside_one", "intervals = [(1, 10)], new = (3, 4)", "insert(&[(1, 10)], (3, 4))", "vec![(1, 10)]"),
        T("in_a_gap", "intervals = [(1, 2), (8, 9)], new = (4, 5)", "insert(&[(1, 2), (8, 9)], (4, 5))", "vec![(1, 2), (4, 5), (8, 9)]"),
        T("touches_both_sides", "intervals = [(1, 3), (5, 7)], new = (3, 5)", "insert(&[(1, 3), (5, 7)], (3, 5))", "vec![(1, 7)]"),
        T("point_in_gap", "intervals = [(1, 3), (5, 7)], new = (4, 4)", "insert(&[(1, 3), (5, 7)], (4, 4))", "vec![(1, 3), (4, 4), (5, 7)]"),
        T("touches_left_neighbour", "intervals = [(1, 3), (8, 9)], new = (3, 5)", "insert(&[(1, 3), (8, 9)], (3, 5))", "vec![(1, 5), (8, 9)]"),
        T("i32_extremes_apart", "intervals = [(i32::MIN, -1), (1, i32::MAX)], new = (0, 0)", "insert(&[(i32::MIN, -1), (1, i32::MAX)], (0, 0))", "vec![(i32::MIN, -1), (0, 0), (1, i32::MAX)]"),
        T("i32_extremes_join", "intervals = [(i32::MIN, -1), (1, i32::MAX)], new = (-1, 1)", "insert(&[(i32::MIN, -1), (1, i32::MAX)], (-1, 1))", "vec![(i32::MIN, i32::MAX)]"),
        T("same_as_existing", "intervals = [(2, 4)], new = (2, 4)", "insert(&[(2, 4)], (2, 4))", "vec![(2, 4)]"),
        GRID_MERGE,
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(808);
            for _ in 0..400 {
                let n = rng.below(7);
                let raw: Vec<(i32, i32)> = (0..n)
                    .map(|_| {
                        let s = rng.int(0, 25) as i32;
                        let len = rng.int(0, 3) as i32;
                        (s, s + len)
                    })
                    .collect();
                let intervals = grid_merge(&raw);
                let s = rng.int(0, 25) as i32;
                let len = rng.int(0, 5) as i32;
                let new = (s, s + len);
                let mut all = intervals.clone();
                all.push(new);
                check!(format!("intervals = {intervals:?}, new = {new:?}"), insert(&intervals, new), grid_merge(&all));
            }
        }

        #[test]
        fn scale_200k() {
            let intervals: Vec<(i32, i32)> = (0..200_000).map(|i| (3 * i, 3 * i + 1)).collect();
            let out = insert(&intervals, (1, 300_000));
            check!("(3i, 3i + 1) for i in 0..200000, new = (1, 300000)", (out.len(), out[0], out[1]), (100_000, (0, 300_001), (300_003, 300_004)));
        }
        """,
    ],
    wrong=dict(
        touching_stays_apart="""
            pub fn insert(intervals: &[(i32, i32)], new: (i32, i32)) -> Vec<(i32, i32)> {
                let mut out = Vec::new();
                let (mut lo, mut hi) = new;
                let mut i = 0;
                while i < intervals.len() && intervals[i].1 <= lo {
                    out.push(intervals[i]);
                    i += 1;
                }
                while i < intervals.len() && intervals[i].0 < hi {
                    lo = lo.min(intervals[i].0);
                    hi = hi.max(intervals[i].1);
                    i += 1;
                }
                out.push((lo, hi));
                out.extend_from_slice(&intervals[i..]);
                out
            }
        """,
        end_not_max="""
            pub fn insert(intervals: &[(i32, i32)], new: (i32, i32)) -> Vec<(i32, i32)> {
                let mut out = Vec::new();
                let (mut lo, mut hi) = new;
                let mut i = 0;
                while i < intervals.len() && intervals[i].1 < lo {
                    out.push(intervals[i]);
                    i += 1;
                }
                while i < intervals.len() && intervals[i].0 <= hi {
                    lo = lo.min(intervals[i].0);
                    hi = intervals[i].1;
                    i += 1;
                }
                out.push((lo, hi));
                out.extend_from_slice(&intervals[i..]);
                out
            }
        """,
    ),
    hints=[("approach", "The list is already sorted: copy intervals that end before `new` starts, absorb every interval that starts before `new` ends, then copy the rest."),
           ("rust", "Two `while` loops over one index `i`, then `out.extend_from_slice(&intervals[i..])`."),
           ("edge case", "Touching counts: `(1, 3)` and `(3, 4)` merge, so compare with `<` and `<=` carefully.")],
    notes=("Because the input is sorted and disjoint, the intervals that overlap `new` form one contiguous run; everything before and after is copied unchanged.", "O(n)", "O(n) for the output"),
    follow_up="If you had to insert many intervals one after another, what structure would keep each insert fast?",
    related=["S3", "D4"],
))

P.append(dict(
    slug="non-overlapping-intervals", title="Non-overlapping intervals", level="medium", stage="intervals", tags=["intervals", "greedy", "Blind 75"],
    companies=["Meta", "Amazon", "Google"],
    teaches=["Sort by end time: finishing early leaves the most room (the activity-selection argument).", "`Option<i32>` as \"nothing kept yet\" instead of a magic minimum."],
    statement="""
        Each `(start, end)` has `start < end` and covers the time from `start` up to but not including `end`, so
        intervals that only touch don't overlap. Return the fewest intervals to remove so the rest don't overlap.
    """,
    examples=[("intervals = [(1, 2), (2, 3), (3, 4), (1, 3)]", "1"), ("intervals = [(1, 2), (1, 2), (1, 2)]", "2")],
    constraints=["0 ≤ intervals.len() ≤ 2·10⁵", "start < end, both any i32"],
    starter="""
        pub fn erase_overlap_intervals(intervals: &[(i32, i32)]) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn erase_overlap_intervals(intervals: &[(i32, i32)]) -> usize {
            let mut sorted = intervals.to_vec();
            sorted.sort_unstable_by_key(|iv| iv.1);
            let mut kept = 0;
            let mut last_end: Option<i32> = None;
            for (start, end) in sorted {
                if last_end.map_or(true, |e| start >= e) {
                    kept += 1;
                    last_end = Some(end);
                }
            }
            intervals.len() - kept
        }
    """,
    visible=[
        T("leetcode_one", "intervals = [(1, 2), (2, 3), (3, 4), (1, 3)]", "erase_overlap_intervals(&[(1, 2), (2, 3), (3, 4), (1, 3)])", "1"),
        T("leetcode_copies", "intervals = [(1, 2), (1, 2), (1, 2)]", "erase_overlap_intervals(&[(1, 2), (1, 2), (1, 2)])", "2"),
        T("leetcode_touching", "intervals = [(1, 2), (2, 3)]", "erase_overlap_intervals(&[(1, 2), (2, 3)])", "0"),
        T("empty", "intervals = []", "erase_overlap_intervals(&[])", "0"),
        T("single", "intervals = [(4, 9)]", "erase_overlap_intervals(&[(4, 9)])", "0"),
        T("drop_the_long_one", "intervals = [(1, 100), (1, 2), (3, 4), (5, 6)]", "erase_overlap_intervals(&[(1, 100), (1, 2), (3, 4), (5, 6)])", "1"),
    ],
    hidden=[
        T("nested", "intervals = [(1, 10), (2, 3)]", "erase_overlap_intervals(&[(1, 10), (2, 3)])", "1"),
        T("staircase", "intervals = [(0, 2), (1, 3), (2, 4), (3, 5)]", "erase_overlap_intervals(&[(0, 2), (1, 3), (2, 4), (3, 5)])", "2"),
        T("negatives", "intervals = [(-3, -1), (-2, 0), (-1, 1)]", "erase_overlap_intervals(&[(-3, -1), (-2, 0), (-1, 1)])", "1"),
        T("i32_extremes", "intervals = [(MIN, MAX), (MIN, 0), (0, MAX)]", "erase_overlap_intervals(&[(i32::MIN, i32::MAX), (i32::MIN, 0), (0, i32::MAX)])", "1"),
        T("earliest_start_is_a_trap", "intervals = [(1, 10), (2, 3), (4, 5)]", "erase_overlap_intervals(&[(1, 10), (2, 3), (4, 5)])", "1"),
        T("same_end", "intervals = [(1, 3), (2, 3), (0, 3)]", "erase_overlap_intervals(&[(1, 3), (2, 3), (0, 3)])", "2"),
        T("disjoint_unsorted", "intervals = [(5, 6), (1, 2), (3, 4)]", "erase_overlap_intervals(&[(5, 6), (1, 2), (3, 4)])", "0"),
        T("leetcode_mixed", "intervals = [(-52, 31), (-73, -26), (82, 97), (-65, -11), (-62, -49), (95, 99), (58, 95), (-31, 49), (66, 98), (-63, 2), (30, 47), (-40, -26)]", "erase_overlap_intervals(&[(-52, 31), (-73, -26), (82, 97), (-65, -11), (-62, -49), (95, 99), (58, 95), (-31, 49), (66, 98), (-63, 2), (30, 47), (-40, -26)])", "7"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(809);
            for _ in 0..300 {
                let n = rng.below(9);
                let intervals: Vec<(i32, i32)> = (0..n)
                    .map(|_| {
                        let s = rng.int(-5, 15) as i32;
                        let len = rng.int(1, 6) as i32;
                        (s, s + len)
                    })
                    .collect();
                let mut most = 0;
                for mask in 0u32..1 << n {
                    let kept: Vec<(i32, i32)> = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| intervals[i]).collect();
                    let ok = (0..kept.len()).all(|i| (i + 1..kept.len()).all(|j| kept[i].1 <= kept[j].0 || kept[j].1 <= kept[i].0));
                    if ok {
                        most = most.max(kept.len());
                    }
                }
                check!(format!("intervals = {intervals:?}"), erase_overlap_intervals(&intervals), n - most);
            }
        }

        #[test]
        fn scale_200k() {
            // Pairs (2i, 2i + 2) and (2i + 1, 2i + 3): the (2i, 2i + 2) ones can all be kept.
            let intervals: Vec<(i32, i32)> = (0..100_000).rev().flat_map(|i| [(2 * i + 1, 2 * i + 3), (2 * i, 2 * i + 2)]).collect();
            check!("(2i, 2i + 2) and (2i + 1, 2i + 3) for i in 0..100000", erase_overlap_intervals(&intervals), 100_000);
        }
        """,
    ],
    wrong=dict(
        quadratic_dp="""
            pub fn erase_overlap_intervals(intervals: &[(i32, i32)]) -> usize {
                let mut sorted = intervals.to_vec();
                sorted.sort_unstable();
                let n = sorted.len();
                // best[i]: most intervals kept among 0..=i when interval i is kept.
                let mut best = vec![1usize; n];
                for i in 0..n {
                    for j in 0..i {
                        if sorted[j].1 <= sorted[i].0 {
                            best[i] = best[i].max(best[j] + 1);
                        }
                    }
                }
                n - best.into_iter().max().unwrap_or(0)
            }
        """,
        keep_earliest_start="""
            pub fn erase_overlap_intervals(intervals: &[(i32, i32)]) -> usize {
                let mut sorted = intervals.to_vec();
                sorted.sort_unstable();
                let mut kept = 0;
                let mut last_end: Option<i32> = None;
                for (start, end) in sorted {
                    if last_end.map_or(true, |e| start >= e) {
                        kept += 1;
                        last_end = Some(end);
                    }
                }
                intervals.len() - kept
            }
        """,
        touching_overlaps="""
            pub fn erase_overlap_intervals(intervals: &[(i32, i32)]) -> usize {
                let mut sorted = intervals.to_vec();
                sorted.sort_unstable_by_key(|iv| iv.1);
                let mut kept = 0;
                let mut last_end: Option<i32> = None;
                for (start, end) in sorted {
                    if last_end.map_or(true, |e| start > e) {
                        kept += 1;
                        last_end = Some(end);
                    }
                }
                intervals.len() - kept
            }
        """,
    ),
    hints=[("approach", "Flip it: keep as many intervals as possible. Of all intervals that could come first, keep the one that ends earliest."),
           ("rust", "`sort_unstable_by_key(|iv| iv.1)`, then keep an interval when its start is `>=` the last kept end."),
           ("edge case", "Sorting by start and keeping the first one fails on `[(1, 10), (2, 3), (4, 5)]`.")],
    notes=("Exchange argument: in any best solution, swapping the first kept interval for the one with the earliest end keeps it valid. So sort by end and keep greedily; the answer is n minus the number kept.", "O(n log n)", "O(n) for the sorted copy"),
    follow_up="If each interval had a weight and you wanted to keep the most total weight, does greedy still work? (No: weighted interval scheduling is a DP with binary search.)",
    related=["D12", "D4"],
))

P.append(dict(
    slug="minimum-number-of-arrows-to-burst-balloons", title="Minimum number of arrows to burst balloons", level="medium", stage="intervals", tags=["intervals", "greedy"],
    companies=["Meta", "Amazon"],
    teaches=["Sort by end and shoot at the end: the same activity-selection idea as non-overlapping intervals.", "Compare with `cmp`/`sort_by_key`, never by subtracting `i32`s (overflow)."],
    statement="""
        Each balloon spans the closed range `(start, end)` on the x-axis, `start ≤ end`. An arrow shot at `x`
        bursts every balloon with `start ≤ x ≤ end`. Return the fewest arrows that burst every balloon.
    """,
    examples=[("points = [(10, 16), (2, 8), (1, 6), (7, 12)]", "2"), ("points = [(1, 2), (2, 3), (3, 4), (4, 5)]", "2")],
    constraints=["0 ≤ points.len() ≤ 2·10⁵", "start ≤ end, both any i32"],
    starter="""
        pub fn find_min_arrow_shots(points: &[(i32, i32)]) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn find_min_arrow_shots(points: &[(i32, i32)]) -> usize {
            let mut sorted = points.to_vec();
            sorted.sort_unstable_by_key(|p| p.1);
            let mut arrows = 0;
            let mut last: Option<i32> = None;
            for (start, end) in sorted {
                if last.map_or(true, |x| start > x) {
                    arrows += 1;
                    last = Some(end);
                }
            }
            arrows
        }
    """,
    visible=[
        T("leetcode_two", "points = [(10, 16), (2, 8), (1, 6), (7, 12)]", "find_min_arrow_shots(&[(10, 16), (2, 8), (1, 6), (7, 12)])", "2"),
        T("leetcode_apart", "points = [(1, 2), (3, 4), (5, 6), (7, 8)]", "find_min_arrow_shots(&[(1, 2), (3, 4), (5, 6), (7, 8)])", "4"),
        T("leetcode_touching", "points = [(1, 2), (2, 3), (3, 4), (4, 5)]", "find_min_arrow_shots(&[(1, 2), (2, 3), (3, 4), (4, 5)])", "2"),
        T("no_balloons", "points = []", "find_min_arrow_shots(&[])", "0"),
        T("one_balloon", "points = [(3, 7)]", "find_min_arrow_shots(&[(3, 7)])", "1"),
        T("nested", "points = [(1, 10), (3, 4)]", "find_min_arrow_shots(&[(1, 10), (3, 4)])", "1"),
    ],
    hidden=[
        T("touch_once", "points = [(1, 2), (2, 3)]", "find_min_arrow_shots(&[(1, 2), (2, 3)])", "1"),
        T("points_only", "points = [(5, 5), (5, 5)]", "find_min_arrow_shots(&[(5, 5), (5, 5)])", "1"),
        T("i32_whole_line", "points = [(MIN, MAX), (MAX, MAX)]", "find_min_arrow_shots(&[(i32::MIN, i32::MAX), (i32::MAX, i32::MAX)])", "1"),
        T("i32_far_ends", "points = [(MIN, MIN), (MAX, MAX)]", "find_min_arrow_shots(&[(i32::MIN, i32::MIN), (i32::MAX, i32::MAX)])", "2"),
        T("leetcode_overflow", "points = [(-2147483646, -2147483645), (2147483646, 2147483647)]", "find_min_arrow_shots(&[(-2147483646, -2147483645), (2147483646, 2147483647)])", "2"),
        T("start_sort_trap", "points = [(1, 10), (2, 3), (4, 5)]", "find_min_arrow_shots(&[(1, 10), (2, 3), (4, 5)])", "2"),
        T("negatives", "points = [(-5, -3), (-4, 0), (1, 2)]", "find_min_arrow_shots(&[(-5, -3), (-4, 0), (1, 2)])", "2"),
        T("duplicates", "points = [(1, 3), (1, 3), (1, 3), (4, 4)]", "find_min_arrow_shots(&[(1, 3), (1, 3), (1, 3), (4, 4)])", "2"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(810);
            for _ in 0..300 {
                let n = rng.below(8);
                let points: Vec<(i32, i32)> = (0..n)
                    .map(|_| {
                        let s = rng.int(-5, 15) as i32;
                        let len = rng.int(0, 5) as i32;
                        (s, s + len)
                    })
                    .collect();
                // Some best set of arrows sits at balloon ends: try every subset of ends.
                let mut want = n;
                for mask in 0u32..1 << n {
                    let shots: Vec<i32> = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| points[i].1).collect();
                    if points.iter().all(|&(s, e)| shots.iter().any(|&x| s <= x && x <= e)) {
                        want = want.min(shots.len());
                    }
                }
                check!(format!("points = {points:?}"), find_min_arrow_shots(&points), want);
            }
        }

        #[test]
        fn scale_200k() {
            let points: Vec<(i32, i32)> = (0..200_000).rev().map(|i| (2 * i, 2 * i + 1)).collect();
            check!("(2i, 2i + 1) for i in 0..200000, reversed", find_min_arrow_shots(&points), 200_000);
        }
        """,
    ],
    wrong=dict(
        retain_per_arrow="""
            pub fn find_min_arrow_shots(points: &[(i32, i32)]) -> usize {
                let mut left = points.to_vec();
                left.sort_unstable_by_key(|p| p.1);
                let mut arrows = 0;
                while let Some(&(_, x)) = left.first() {
                    arrows += 1;
                    left.retain(|&(s, _)| s > x);
                }
                arrows
            }
        """,
        start_sort_no_shrink="""
            pub fn find_min_arrow_shots(points: &[(i32, i32)]) -> usize {
                let mut sorted = points.to_vec();
                sorted.sort_unstable();
                let mut arrows = 0;
                let mut last: Option<i32> = None;
                for (start, end) in sorted {
                    if last.map_or(true, |x| start > x) {
                        arrows += 1;
                        last = Some(end);
                    }
                }
                arrows
            }
        """,
        touching_needs_two="""
            pub fn find_min_arrow_shots(points: &[(i32, i32)]) -> usize {
                let mut sorted = points.to_vec();
                sorted.sort_unstable_by_key(|p| p.1);
                let mut arrows = 0;
                let mut last: Option<i32> = None;
                for (start, end) in sorted {
                    if last.map_or(true, |x| start >= x) {
                        arrows += 1;
                        last = Some(end);
                    }
                }
                arrows
            }
        """,
    ),
    hints=[("approach", "The balloon that ends first must be hit by some arrow; shooting at its end hits as many others as possible."),
           ("rust", "`sort_unstable_by_key(|p| p.1)` compares safely; a comparator like `a.1 - b.1` overflows at the `i32` extremes."),
           ("edge case", "Balloons are closed: one arrow at 2 bursts both `(1, 2)` and `(2, 3)`.")],
    notes=("Sorted by end, shoot at the first unburst balloon's end; every balloon starting at or before that point is burst too. It's the same greedy as non-overlapping intervals with closed ends.", "O(n log n)", "O(n) for the sorted copy"),
    follow_up="How does this relate to Non-overlapping intervals? Can you get one answer from the other?",
    related=["D12"],
))

P.append(dict(
    slug="meeting-rooms-ii", title="Meeting rooms II", level="medium", stage="intervals", tags=["intervals", "sweep line", "Blind 75"],
    companies=["Meta", "Amazon", "Google", "Microsoft", "Bloomberg", "Uber"],
    teaches=["Sweep line: sort the starts and the ends separately and walk them together.", "A min-heap of end times (`BinaryHeap<Reverse<i32>>`) is the other classic way."],
    statement="""
        Each meeting is `(start, end)` with `start < end`, covering the time from `start` up to but not including
        `end`. Return the fewest rooms needed to hold every meeting. A room freed at time `t` can host a meeting
        starting at `t`.
    """,
    examples=[("meetings = [(0, 30), (5, 10), (15, 20)]", "2"), ("meetings = [(7, 10), (2, 4)]", "1")],
    constraints=["0 ≤ meetings.len() ≤ 2·10⁵", "start < end, both any i32"],
    starter="""
        pub fn min_meeting_rooms(meetings: &[(i32, i32)]) -> usize {
            todo!()
        }
    """,
    solution="""
        pub fn min_meeting_rooms(meetings: &[(i32, i32)]) -> usize {
            let mut starts: Vec<i32> = meetings.iter().map(|m| m.0).collect();
            let mut ends: Vec<i32> = meetings.iter().map(|m| m.1).collect();
            starts.sort_unstable();
            ends.sort_unstable();
            let (mut in_use, mut most, mut j) = (0usize, 0usize, 0usize);
            for &s in &starts {
                // Every meeting that ended by `s` has freed its room.
                while ends[j] <= s {
                    in_use -= 1;
                    j += 1;
                }
                in_use += 1;
                most = most.max(in_use);
            }
            most
        }
    """,
    visible=[
        T("leetcode_two", "meetings = [(0, 30), (5, 10), (15, 20)]", "min_meeting_rooms(&[(0, 30), (5, 10), (15, 20)])", "2"),
        T("leetcode_one", "meetings = [(7, 10), (2, 4)]", "min_meeting_rooms(&[(7, 10), (2, 4)])", "1"),
        T("no_meetings", "meetings = []", "min_meeting_rooms(&[])", "0"),
        T("single", "meetings = [(1, 2)]", "min_meeting_rooms(&[(1, 2)])", "1"),
        T("back_to_back_share", "meetings = [(1, 5), (5, 10)]", "min_meeting_rooms(&[(1, 5), (5, 10)])", "1"),
        T("all_at_once", "meetings = [(1, 5), (1, 5), (1, 5)]", "min_meeting_rooms(&[(1, 5), (1, 5), (1, 5)])", "3"),
    ],
    hidden=[
        T("nested", "meetings = [(1, 10), (2, 9), (3, 8)]", "min_meeting_rooms(&[(1, 10), (2, 9), (3, 8)])", "3"),
        T("chain", "meetings = [(1, 3), (2, 4), (3, 5)]", "min_meeting_rooms(&[(1, 3), (2, 4), (3, 5)])", "2"),
        T("negatives", "meetings = [(-10, -5), (-6, 0), (-5, 1)]", "min_meeting_rooms(&[(-10, -5), (-6, 0), (-5, 1)])", "2"),
        T("i32_extremes", "meetings = [(MIN, MAX), (0, 1), (1, 2)]", "min_meeting_rooms(&[(i32::MIN, i32::MAX), (0, 1), (1, 2)])", "2"),
        T("i32_touching", "meetings = [(MIN, 0), (0, MAX)]", "min_meeting_rooms(&[(i32::MIN, 0), (0, i32::MAX)])", "1"),
        T("leetcode_unsorted", "meetings = [(9, 10), (4, 9), (4, 17)]", "min_meeting_rooms(&[(9, 10), (4, 9), (4, 17)])", "2"),
        T("leetcode_shared_end", "meetings = [(2, 11), (6, 16), (11, 16)]", "min_meeting_rooms(&[(2, 11), (6, 16), (11, 16)])", "2"),
        T("classic_six", "meetings = [(1, 10), (2, 7), (3, 19), (8, 12), (10, 20), (11, 30)]", "min_meeting_rooms(&[(1, 10), (2, 7), (3, 19), (8, 12), (10, 20), (11, 30)])", "4"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(811);
            for _ in 0..400 {
                let n = rng.below(9);
                let meetings: Vec<(i32, i32)> = (0..n)
                    .map(|_| {
                        let s = rng.int(-5, 15) as i32;
                        let len = rng.int(1, 6) as i32;
                        (s, s + len)
                    })
                    .collect();
                // The busiest moment is always some meeting's start.
                let want = meetings.iter().map(|&(t, _)| meetings.iter().filter(|&&(s, e)| s <= t && t < e).count()).max().unwrap_or(0);
                check!(format!("meetings = {meetings:?}"), min_meeting_rooms(&meetings), want);
            }
        }

        #[test]
        fn scale_200k() {
            let meetings: Vec<(i32, i32)> = (0..200_000).rev().map(|i| (i, i + 1000)).collect();
            check!("(i, i + 1000) for i in 0..200000", min_meeting_rooms(&meetings), 1000);
        }
        """,
    ],
    wrong=dict(
        count_at_each_start="""
            pub fn min_meeting_rooms(meetings: &[(i32, i32)]) -> usize {
                meetings.iter().map(|&(t, _)| meetings.iter().filter(|&&(s, e)| s <= t && t < e).count()).max().unwrap_or(0)
            }
        """,
        touching_needs_new_room="""
            pub fn min_meeting_rooms(meetings: &[(i32, i32)]) -> usize {
                let mut starts: Vec<i32> = meetings.iter().map(|m| m.0).collect();
                let mut ends: Vec<i32> = meetings.iter().map(|m| m.1).collect();
                starts.sort_unstable();
                ends.sort_unstable();
                let (mut in_use, mut most, mut j) = (0usize, 0usize, 0usize);
                for &s in &starts {
                    while ends[j] < s {
                        in_use -= 1;
                        j += 1;
                    }
                    in_use += 1;
                    most = most.max(in_use);
                }
                most
            }
        """,
    ),
    hints=[("approach", "Only the number of meetings running at once matters. Walk the start times in order and free a room for every meeting that has ended by then."),
           ("rust", "Collect and sort `starts` and `ends` separately; one index into `ends` follows the loop over `starts`. Or keep a `BinaryHeap<Reverse<i32>>` of end times."),
           ("edge case", "Free rooms with `end <= start`, so a meeting ending at 5 frees its room for one starting at 5.")],
    notes=("The rooms needed equal the most meetings running at any moment. Sorting starts and ends separately and sweeping counts that without tracking which meeting is in which room.", "O(n log n)", "O(n)"),
    follow_up="How would you also report which room each meeting goes to?",
    related=["D7", "S5"],
))

P.append(dict(
    slug="interval-list-intersections", title="Interval list intersections", level="medium", stage="intervals", tags=["intervals", "two pointers"],
    companies=["Meta", "Amazon", "Google"],
    teaches=["Two pointers over two sorted lists: always advance the interval that ends first.", "The overlap of two closed intervals is `(max of starts, min of ends)` when that's non-empty."],
    statement="""
        `a` and `b` are lists of closed intervals, each sorted by start with no two intervals in the same list
        overlapping. Return every intersection of an interval from `a` with one from `b`, sorted by start.
        A single shared point, like `(5, 5)`, counts.
    """,
    examples=[("a = [(0, 2), (5, 10), (13, 23), (24, 25)], b = [(1, 5), (8, 12), (15, 24), (25, 26)]", "[(1, 2), (5, 5), (8, 10), (15, 23), (24, 24), (25, 25)]")],
    constraints=["0 ≤ a.len(), b.len() ≤ 10⁵", "start ≤ end, both any i32"],
    starter="""
        pub fn interval_intersection(a: &[(i32, i32)], b: &[(i32, i32)]) -> Vec<(i32, i32)> {
            todo!()
        }
    """,
    solution="""
        pub fn interval_intersection(a: &[(i32, i32)], b: &[(i32, i32)]) -> Vec<(i32, i32)> {
            let mut out = Vec::new();
            let (mut i, mut j) = (0, 0);
            while i < a.len() && j < b.len() {
                let lo = a[i].0.max(b[j].0);
                let hi = a[i].1.min(b[j].1);
                if lo <= hi {
                    out.push((lo, hi));
                }
                if a[i].1 < b[j].1 {
                    i += 1;
                } else {
                    j += 1;
                }
            }
            out
        }
    """,
    visible=[
        T("leetcode_mixed", "a = [(0, 2), (5, 10), (13, 23), (24, 25)], b = [(1, 5), (8, 12), (15, 24), (25, 26)]", "interval_intersection(&[(0, 2), (5, 10), (13, 23), (24, 25)], &[(1, 5), (8, 12), (15, 24), (25, 26)])", "vec![(1, 2), (5, 5), (8, 10), (15, 23), (24, 24), (25, 25)]"),
        T("leetcode_one_empty", "a = [(1, 3), (5, 9)], b = []", "interval_intersection(&[(1, 3), (5, 9)], &[])", "Vec::<(i32, i32)>::new()"),
        T("both_empty", "a = [], b = []", "interval_intersection(&[], &[])", "Vec::<(i32, i32)>::new()"),
        T("shared_point", "a = [(1, 5)], b = [(5, 8)]", "interval_intersection(&[(1, 5)], &[(5, 8)])", "vec![(5, 5)]"),
        T("one_covers_many", "a = [(0, 10)], b = [(1, 2), (4, 5)]", "interval_intersection(&[(0, 10)], &[(1, 2), (4, 5)])", "vec![(1, 2), (4, 5)]"),
        T("no_overlap", "a = [(1, 2)], b = [(3, 4)]", "interval_intersection(&[(1, 2)], &[(3, 4)])", "Vec::<(i32, i32)>::new()"),
    ],
    hidden=[
        T("identical", "a = [(1, 2), (4, 6)], b = [(1, 2), (4, 6)]", "interval_intersection(&[(1, 2), (4, 6)], &[(1, 2), (4, 6)])", "vec![(1, 2), (4, 6)]"),
        T("negatives", "a = [(-5, -2), (0, 3)], b = [(-3, 1)]", "interval_intersection(&[(-5, -2), (0, 3)], &[(-3, 1)])", "vec![(-3, -2), (0, 1)]"),
        T("i32_extremes", "a = [(MIN, MAX)], b = [(MIN, MIN), (MAX, MAX)]", "interval_intersection(&[(i32::MIN, i32::MAX)], &[(i32::MIN, i32::MIN), (i32::MAX, i32::MAX)])", "vec![(i32::MIN, i32::MIN), (i32::MAX, i32::MAX)]"),
        T("points_meet", "a = [(3, 3)], b = [(3, 3)]", "interval_intersection(&[(3, 3)], &[(3, 3)])", "vec![(3, 3)]"),
        T("interleaved", "a = [(1, 3), (5, 7), (9, 11)], b = [(2, 6), (8, 10)]", "interval_intersection(&[(1, 3), (5, 7), (9, 11)], &[(2, 6), (8, 10)])", "vec![(2, 3), (5, 6), (9, 10)]"),
        T("swapped_arguments", "a = [(2, 6), (8, 10)], b = [(1, 3), (5, 7), (9, 11)]", "interval_intersection(&[(2, 6), (8, 10)], &[(1, 3), (5, 7), (9, 11)])", "vec![(2, 3), (5, 6), (9, 10)]"),
        T("same_end", "a = [(1, 4), (6, 7)], b = [(2, 4), (5, 7)]", "interval_intersection(&[(1, 4), (6, 7)], &[(2, 4), (5, 7)])", "vec![(2, 4), (6, 7)]"),
        T("first_list_empty", "a = [], b = [(1, 2)]", "interval_intersection(&[], &[(1, 2)])", "Vec::<(i32, i32)>::new()"),
        """
        #[test]
        fn random_vs_brute_force() {
            fn list(rng: &mut anneal_prelude::Rng) -> Vec<(i32, i32)> {
                let n = rng.below(6);
                let mut out = Vec::new();
                let mut pos = rng.int(-3, 3) as i32;
                for _ in 0..n {
                    let len = rng.int(0, 4) as i32;
                    out.push((pos, pos + len));
                    let gap = rng.int(1, 4) as i32;
                    pos += len + gap;
                }
                out
            }
            let mut rng = anneal_prelude::Rng::new(812);
            for _ in 0..400 {
                let a = list(&mut rng);
                let b = list(&mut rng);
                let mut want = Vec::new();
                for &(s1, e1) in &a {
                    for &(s2, e2) in &b {
                        if s1.max(s2) <= e1.min(e2) {
                            want.push((s1.max(s2), e1.min(e2)));
                        }
                    }
                }
                want.sort_unstable();
                check!(format!("a = {a:?}, b = {b:?}"), interval_intersection(&a, &b), want);
            }
        }

        #[test]
        fn scale_100k_each() {
            let a: Vec<(i32, i32)> = (0..100_000).map(|i| (4 * i, 4 * i + 2)).collect();
            let b: Vec<(i32, i32)> = (0..100_000).map(|i| (4 * i + 1, 4 * i + 3)).collect();
            let out = interval_intersection(&a, &b);
            check!("a = (4i, 4i + 2), b = (4i + 1, 4i + 3) for i in 0..100000", (out.len(), out[0], out[99_999]), (100_000, (1, 2), (399_997, 399_998)));
        }
        """,
    ],
    wrong=dict(
        all_pairs="""
            pub fn interval_intersection(a: &[(i32, i32)], b: &[(i32, i32)]) -> Vec<(i32, i32)> {
                let mut out = Vec::new();
                for &(s1, e1) in a {
                    for &(s2, e2) in b {
                        if s1.max(s2) <= e1.min(e2) {
                            out.push((s1.max(s2), e1.min(e2)));
                        }
                    }
                }
                out.sort_unstable();
                out
            }
        """,
        drops_points="""
            pub fn interval_intersection(a: &[(i32, i32)], b: &[(i32, i32)]) -> Vec<(i32, i32)> {
                let mut out = Vec::new();
                let (mut i, mut j) = (0, 0);
                while i < a.len() && j < b.len() {
                    let lo = a[i].0.max(b[j].0);
                    let hi = a[i].1.min(b[j].1);
                    if lo < hi {
                        out.push((lo, hi));
                    }
                    if a[i].1 < b[j].1 {
                        i += 1;
                    } else {
                        j += 1;
                    }
                }
                out
            }
        """,
        advance_later_end="""
            pub fn interval_intersection(a: &[(i32, i32)], b: &[(i32, i32)]) -> Vec<(i32, i32)> {
                let mut out = Vec::new();
                let (mut i, mut j) = (0, 0);
                while i < a.len() && j < b.len() {
                    let lo = a[i].0.max(b[j].0);
                    let hi = a[i].1.min(b[j].1);
                    if lo <= hi {
                        out.push((lo, hi));
                    }
                    if a[i].0 < b[j].0 {
                        i += 1;
                    } else {
                        j += 1;
                    }
                }
                out
            }
        """,
    ),
    hints=[("approach", "Keep one index in each list. Record the overlap of the two current intervals, then move past whichever ends first: it can't meet anything later."),
           ("rust", "`let lo = a[i].0.max(b[j].0); let hi = a[i].1.min(b[j].1);` and push `(lo, hi)` when `lo <= hi`."),
           ("edge case", "Closed intervals: `(1, 5)` and `(5, 8)` intersect in `(5, 5)`.")],
    notes=("The interval that ends first can't overlap anything after the other list's current interval, so dropping it is safe. Each step advances one index.", "O(n + m)", "O(1) besides the output"),
    follow_up="How would you intersect k lists at once?",
    related=["D2", "D7"],
))

P.append(dict(
    slug="car-pooling", title="Car pooling", level="medium", stage="intervals", tags=["sweep line", "sorting"],
    companies=["Amazon", "Google"],
    teaches=["Turn intervals into `(position, change)` events and sort them.", "Sorting tuples puts drop-offs (negative change) before pick-ups at the same stop."],
    statement="""
        A car drives east with room for `capacity` passengers. Trip `(passengers, from, to)` picks up that many
        people at `from` and drops them at `to` (`from < to`). At any stop, passengers get off before new ones
        get on. Return `true` if every trip fits.
    """,
    examples=[("trips = [(2, 1, 5), (3, 3, 7)], capacity = 4", "false"), ("trips = [(2, 1, 5), (3, 3, 7)], capacity = 5", "true")],
    constraints=["0 ≤ trips.len() ≤ 10⁵", "1 ≤ passengers ≤ 1000", "0 ≤ from < to ≤ 2·10⁹", "0 ≤ capacity ≤ 10⁹"],
    starter="""
        pub fn car_pooling(trips: &[(u32, u32, u32)], capacity: u32) -> bool {
            todo!()
        }
    """,
    solution="""
        pub fn car_pooling(trips: &[(u32, u32, u32)], capacity: u32) -> bool {
            let mut events: Vec<(u32, i64)> = Vec::with_capacity(2 * trips.len());
            for &(people, from, to) in trips {
                events.push((from, people as i64));
                events.push((to, -(people as i64)));
            }
            // At the same stop, the negative (drop-off) changes sort first.
            events.sort_unstable();
            let mut load = 0i64;
            for (_, change) in events {
                load += change;
                if load > capacity as i64 {
                    return false;
                }
            }
            true
        }
    """,
    visible=[
        T("leetcode_too_many", "trips = [(2, 1, 5), (3, 3, 7)], capacity = 4", "car_pooling(&[(2, 1, 5), (3, 3, 7)], 4)", "false"),
        T("leetcode_fits", "trips = [(2, 1, 5), (3, 3, 7)], capacity = 5", "car_pooling(&[(2, 1, 5), (3, 3, 7)], 5)", "true"),
        T("leetcode_three", "trips = [(3, 2, 7), (3, 7, 9), (8, 3, 9)], capacity = 11", "car_pooling(&[(3, 2, 7), (3, 7, 9), (8, 3, 9)], 11)", "true"),
        T("no_trips", "trips = [], capacity = 0", "car_pooling(&[], 0)", "true"),
        T("one_trip_too_big", "trips = [(5, 0, 1)], capacity = 4", "car_pooling(&[(5, 0, 1)], 4)", "false"),
        T("drop_off_first", "trips = [(3, 1, 5), (3, 5, 9)], capacity = 3", "car_pooling(&[(3, 1, 5), (3, 5, 9)], 3)", "true"),
    ],
    hidden=[
        T("exactly_full", "trips = [(4, 0, 10)], capacity = 4", "car_pooling(&[(4, 0, 10)], 4)", "true"),
        T("zero_capacity", "trips = [(1, 0, 1)], capacity = 0", "car_pooling(&[(1, 0, 1)], 0)", "false"),
        T("far_stops", "trips = [(1, 0, 1000000000), (1, 999999999, 1000000000)], capacity = 1", "car_pooling(&[(1, 0, 1_000_000_000), (1, 999_999_999, 1_000_000_000)], 1)", "false"),
        T("three_at_one_point", "trips = [(1, 0, 10), (1, 5, 6), (1, 5, 7)], capacity = 2", "car_pooling(&[(1, 0, 10), (1, 5, 6), (1, 5, 7)], 2)", "false"),
        T("relay", "trips = [(2, 0, 3), (2, 3, 6), (2, 6, 9)], capacity = 2", "car_pooling(&[(2, 0, 3), (2, 3, 6), (2, 6, 9)], 2)", "true"),
        T("unsorted_trips", "trips = [(2, 6, 9), (3, 0, 7)], capacity = 4", "car_pooling(&[(2, 6, 9), (3, 0, 7)], 4)", "false"),
        T("same_trip_twice", "trips = [(2, 1, 4), (2, 1, 4)], capacity = 4", "car_pooling(&[(2, 1, 4), (2, 1, 4)], 4)", "true"),
        T("big_capacity", "trips = [(1000, 0, 1); 1000], capacity = 1000000", "car_pooling(&vec![(1000, 0, 1); 1000], 1_000_000)", "true"),
        """
        #[test]
        fn random_vs_brute_force() {
            let mut rng = anneal_prelude::Rng::new(813);
            for _ in 0..400 {
                let n = rng.below(7);
                let trips: Vec<(u32, u32, u32)> = (0..n)
                    .map(|_| {
                        let people = rng.int(1, 5) as u32;
                        let from = rng.int(0, 10) as u32;
                        let len = rng.int(1, 5) as u32;
                        (people, from, from + len)
                    })
                    .collect();
                let capacity = rng.int(0, 12) as u32;
                let want = (0..=15u32).all(|x| trips.iter().filter(|t| t.1 <= x && x < t.2).map(|t| t.0).sum::<u32>() <= capacity);
                check!(format!("trips = {trips:?}, capacity = {capacity}"), car_pooling(&trips, capacity), want);
            }
        }

        #[test]
        fn scale_100k() {
            let trips: Vec<(u32, u32, u32)> = (0..100_000u32).rev().map(|i| (1, i * 10_000, i * 10_000 + 5_000_000)).collect();
            check!("(1, 10000i, 10000i + 5000000) for i in 0..100000, capacity 500 and 499", (car_pooling(&trips, 500), car_pooling(&trips, 499)), (true, false));
        }
        """,
    ],
    wrong=dict(
        check_every_start="""
            pub fn car_pooling(trips: &[(u32, u32, u32)], capacity: u32) -> bool {
                trips.iter().all(|&(_, x, _)| {
                    trips.iter().filter(|t| t.1 <= x && x < t.2).map(|t| t.0 as u64).sum::<u64>() <= capacity as u64
                })
            }
        """,
        pick_up_first="""
            pub fn car_pooling(trips: &[(u32, u32, u32)], capacity: u32) -> bool {
                let mut events: Vec<(u32, i64)> = Vec::new();
                for &(people, from, to) in trips {
                    events.push((from, people as i64));
                    events.push((to, -(people as i64)));
                }
                events.sort_unstable_by_key(|&(at, change)| (at, -change));
                let mut load = 0i64;
                for (_, change) in events {
                    load += change;
                    if load > capacity as i64 {
                        return false;
                    }
                }
                true
            }
        """,
    ),
    hints=[("approach", "Only the load at each stop matters. Make an event `(from, +people)` and `(to, -people)` for each trip, sort them, and keep a running total."),
           ("rust", "A `Vec<(u32, i64)>` sorts by stop, then by change, so at the same stop the drop-offs (negative) come first for free."),
           ("edge case", "Stops go up to 2·10⁹, so a difference array indexed by stop would be too big here; sort the events instead.")],
    notes=("The load only changes at pick-ups and drop-offs. Sorting the 2n events and summing them checks the load at every stop.", "O(n log n)", "O(n)"),
    follow_up="If stops were at most 1000, how would a difference array make this O(n + 1000)?",
    related=["D1", "S3"],
))

STAGES = [
    ("first-greedy", "First greedy", "easy"),
    ("intervals", "Intervals", "medium"),
    ("greedy-choices", "Greedy choices", "medium"),
    ("hard-greedy", "Hard greedy", "hard"),
]

if __name__ == "__main__":
    n = write_track("d8-intervals-greedy", "D8", "Intervals & greedy", "D", "core", 9,
                    "Sort, sweep and choose: merging intervals, sweep lines and greedy exchange arguments, with tuples, sort keys and heaps.",
                    STAGES, P)
    print("D8", n)
