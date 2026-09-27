`Box` lists can't have cycles, so this list lives in an arena: node `i`'s successor is `next[i]`. Return
the index where the cycle starts, or `None`. O(1) extra space.
