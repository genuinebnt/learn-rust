BusTub's `ORSetDriver` tests: a driver holds several replicas; each can `save` its state to a shared place and `load` the copies the others saved; `sync` has everyone save and then everyone load. The tests add, remove, sync and check that replicas agree, including a case where two replicas exchange states and a third is cut off.

## The task

The driver (`ORSetDriver`) is given; it only needs your `ORSet`. Make the stage's tests pass: `cargo test --test stages_0d s0d_08`.

## Tests

- `s0d_08_add_remove_and_sync_across_three_nodes`: an element added on one node is invisible elsewhere until `sync`, then visible everywhere; the same for removes.
- `s0d_08_merge_test_two_nodes_agree_after_sync`.
- `s0d_08_removing_everything_and_adding_it_back`.
- `s0d_08_adds_win_a_lot`: every node adds every element; each element is removed on one node; after `sync` all nodes still have every element.
- `s0d_08_a_lost_network_still_converges_later`: nodes 0 and 1 exchange state, node 2 is cut off, and a later `sync` brings everyone together with node 0's fresh adds beating node 2's removes.

## Notes

**How the driver works.** `save(node)` copies the node's state to the shared slot and bumps a version; `load(node)` merges every other node's saved copy that is newer than the last one it read. Because merging is idempotent, re-reading is harmless, and because it is commutative and associative the order in which nodes load does not matter.

**Failures are modelled by skipping steps.** A lost network is a `save` or `load` that is simply not called. The set converges whenever the missing steps happen later: that is the CRDT guarantee.

**If a test fails.** Compare the two replicas' `to_string()`: a missing element means a remove was applied to a pair it had not seen (check `remove`); an element that should be gone means `merge` dropped a removed pair.

## In BusTub

`test/primer/orset_test.cpp`: `ORSetDriverTest.AddRemoveTest`, `MergeTest`, `AddBackAgainTest`, `AddWinsALotTest`, `NetworkLostTest`; the driver is `orset_driver.cpp`: "`Saves changes in all nodes and then load all the changes.`".

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `driver[i % 3]->Add(i)` | `driver.add(i % 3, &i)` |
| `ORSetNode` holding a pointer back to its driver | the driver owns the replicas; nodes are indexes |

**Port rule:** objects that need their owner's services become indexes into the owner.

## Learn more
- [Jepsen: consistency models](https://jepsen.io/consistency) · [Convergence in CRDTs](https://crdt.tech/)

## Performance

These tests are tiny. The cost model to remember: each `sync` merges every pair of replicas' states, `O(n² × state)`; real systems gossip deltas.

**Measure it.** Sync 20 replicas with 10 000 elements each.

## Hints

### Print the sets

`d.set(i).to_string()` for each node shows immediately which replica disagrees.

### Idempotence

If a second `sync` changes anything, `merge` is not a pure union.
