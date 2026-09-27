`eval` evaluates reverse Polish notation, but panics on bad input. Make it return an `RpnError` instead.
It must never panic, including on division by zero.
