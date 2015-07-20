__author__ = 'fernando'

sift3_offset = xrange(1, 3)


def sift3(s1, s2):
    s1L = len(s1)
    s2L = len(s2)
    c1 = 0
    c2 = 0
    lcs = 0
    while c1 < s1L and c2 < s2L:
        if s1[c1] == s2[c2]:
            lcs += 1
        else:
            for i in sift3_offset:
                if c1 + i < s1L and s1[c1 + i] == s2[c2]:
                    c1 += i
                    break
                if c2 + i < s2L and s1[c1] == s2[c2 + i]:
                    c2 += i
                    break
        c1 += 1
        c2 += 1
    return (s1L+s2L)/2 - lcs