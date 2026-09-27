A frog starts on stone 0 and wants to reach the last stone. From stone `i` it can jump to
any of the next `k` stones; jumping from `i` to `j` costs `|heights[i] - heights[j]|`.
`min_cost` returns the cheapest total and gives the right answers, but it recurses once
per stone and overflows the stack on 200 000 stones. Rewrite it bottom-up, without recursion.
