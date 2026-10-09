# Release-mode workloads behind the courses' "Measure it" numbers

Needs the reference crate (kept out of the public repo). Run: `cd tools/perf-workloads && cargo run --release` (all) or with a name
(`watermark`, `skiplist`, `robin`, `robin_random`, `trie`, `mvcc`).

Flamegraph on macOS (no `perf`): `cargo run --release flame_mvcc & sleep 2; sample $! 4 -file out.txt`, then
`inferno-collapse-sample out.txt | inferno-flamegraph > flame.svg` (`cargo install inferno`). On Linux: `perf record -F 999 -g` and
`perf script | inferno-collapse-perf | inferno-flamegraph`.
