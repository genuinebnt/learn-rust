`average` takes comma-separated numbers like `"1, 2, 3"`. It panics on anything unexpected.
Return `Err("no numbers")` for blank input and `Err("not a number: <item>")` for a bad item.
