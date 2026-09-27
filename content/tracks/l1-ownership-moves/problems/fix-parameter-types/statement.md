The tests call `count_long`, then `shout_all`, then `into_sentence` on the same `words`. It doesn't
compile, because every function takes `Vec<String>` by value. Give each the parameter type that fits what it does.
