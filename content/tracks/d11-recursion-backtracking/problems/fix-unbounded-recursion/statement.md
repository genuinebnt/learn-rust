`split_sum` should add up `nums` by splitting the slice in half and summing each half. It works for an empty
slice, but anything else overflows the stack. Fix the base case; keep the recursion.
