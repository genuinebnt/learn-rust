A search box suggests products while you type `search_word`. After **each** typed letter, suggest up to three
products that start with what's typed so far, the three smallest in alphabetical order.

Return one list per typed letter: `result[i]` is the suggestions after typing `search_word[..=i]`.
Once a prefix matches nothing, every later list is empty too.

Products are distinct lowercase words.
