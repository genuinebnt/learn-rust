`sale` and `flag_expensive` don't compile: each borrows the shop through one accessor while calling
another. `flag_expensive` lives outside the `shop` module, so it can't touch the private fields. Fix
both without cloning or collecting anything. You may add one method to `Shop`.
