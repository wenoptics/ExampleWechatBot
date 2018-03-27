def is_wordlist_in_txt(word_list, s: str) -> bool:
    """
    e.g.
        ['a', 'b'], 'bcdef' -> True
        ['a', 'b'], 'cdefg' -> False
    """
    for i in word_list:
        if i in s: return True
    return False