import difflib as dl
import dash_html_components as html

PUNCTUATION_SIGNS = (" ", ",", ".", ":", ";", "!", "?")

V1 = "-"  # change in text 1
V2 = "+"  # change in text 2
Q = "?"  # change explanation

CLASS_DELETED = "deleted"
CLASS_INSERTED = "inserted"


def isolate_word(s, idx_start):
    """Find the indexes corresponding to a full word starting from a given position within a string

    :param s: a string
    :param idx_start: an index within the string
    :return:
    """

    if idx_start < 0:
        raise ValueError("String index cannot be lower than 0!")

    if idx_start > len(s):
        raise ValueError("String index cannot be larger than string length")

    if s[idx_start] in PUNCTUATION_SIGNS:
        answer = [idx_start]
    else:
        idx = idx_start
        while s[idx] not in PUNCTUATION_SIGNS:
            idx = idx + 1
        upper_idx = idx

        idx = idx_start
        while s[idx - 1] not in PUNCTUATION_SIGNS:
            idx = idx - 1
        lower_idx = idx

        answer = [j for j in range(lower_idx, upper_idx, 1)]
    return answer


def extract_chars(s, mask, class_name=None, debug=False):
    """Provided a mask on a string, highlight the groups defined by the mask

    :param s: a string
    :param mask: a list of index of the string
    :param class_name: used for highlighting purposes
    :return: a list with groups of the mask highlighted
    """

    chars = ""
    seq = []
    for j, el in enumerate(mask):
        if j == 0 and el > 0:
            seq.append(s[:el])
        chars += s[el]
        if el+1 not in mask:
            if debug is True:
                seq.append("<{}>".format(chars))
            else:
                seq.append(html.Span(children="{}".format(chars), className=class_name))
            try:
                seq.append(s[el+1:mask[j+1]])
            except IndexError:
                seq.append(s[el+1:])
            chars = ""
    return seq


def highlight_diff(s, diff_info, diff_char, **kwargs):
    """

    :param s: a string
    :param diff_info: diff of the string provided as output of difflib.Differ.compare()
    :param diff_char: the diff char (either + or -)
    :return:
    """


    idx = [i for i in range(len(diff_info)) if diff_info.startswith(diff_char, i) or diff_info.startswith("^", i)]

    idx_set = set()
    for i in idx:
        # find the word at index i
        word = isolate_word(s, i)
        # keep the index of the word first letter
        min_idx = word[0]
        word = set(word)
        # look for consecutive words with modifications
        if idx_set.isdisjoint(word) and min_idx - 2 in idx_set :
            word = word.union((min_idx - 1,))
        idx_set = idx_set.union(word)

    mask = sorted(list(idx_set))
    return extract_chars(s, mask, **kwargs)


def aggregate_multi_line_diff(diff_lines):
    return "\n".join([l for l in diff_lines])


class DiffObj:
    v1 = None
    v2 = None
    deleted = None
    inserted = None

    def __init__(self, stored_diff=None, debug=False):
        self.debug = debug
        if stored_diff is not None:
            self.assign(stored_diff)

    def __str__(self):
        return "\n".join(
            ["Deleted: {}".format(self.deleted), "inserted: {}".format(self.inserted)])

    def assign(self, stored_diff):
        n = len(stored_diff)
        if n == 2:
            self.v1 = aggregate_multi_line_diff(stored_diff[0])
            self.v2 = aggregate_multi_line_diff(stored_diff[1])
            self.deleted = html.Span(children=self.v1, className=CLASS_DELETED)
            self.inserted = html.Span(children=self.v2, className=CLASS_INSERTED)
        elif n == 3:
            del_info, ins_info = stored_diff[2]
            self.v1 = stored_diff[0]
            self.v2 = stored_diff[1]

            if del_info is not None:  # and ins_info is None:
                self.deleted = highlight_diff(self.v1, del_info, V1, class_name=CLASS_DELETED,
                                              debug=self.debug)
            if ins_info is not None:  # and del_info is None:
                self.inserted = highlight_diff(self.v2, ins_info, V2, class_name=CLASS_INSERTED, debug=self.debug)


def store_a_diff(diff_info, diff_storage):
    """Manage diffs for a group of lines

    :param diff_info: a dict with information about - + and ? lines from difflib output
    :param diff_storage: a list of tuples grouping information about each line diff
    :return: nothing, it updates the list diff_storage
    """
    if diff_info:
        if diff_info[Q] is None:
            diff_storage.append(tuple([diff_info[k] for k in [V1, V2]]))
        else:
            diff_storage.append(
                tuple([diff_info[k][0] if k in [V1, V2] else diff_info[k] for k in [V1, V2, Q]]))


def group_diffs(text1_lines, text2_lines):
    d = dl.Differ()
    diff = d.compare(text1_lines, text2_lines)

    stored_diff = []

    line_diff = {}
    previous_sign = None
    current_sign = None

    for i, l in enumerate(diff):
        current_sign = l[0]
        if current_sign == " ":
            print(i)
        # line before is not a -
        if current_sign == V1 and previous_sign != V1:
            store_a_diff(line_diff, stored_diff)
            line_diff[Q] = None
            line_diff[current_sign] = [l[2:]]
        # line before is a -
        elif current_sign == V1 and current_sign == previous_sign:
            line_diff[current_sign].append(l[2:])
            line_diff[Q] = None

        # line before is not a +
        if current_sign == V2 and previous_sign != V2:
            line_diff[current_sign] = [l[2:]]
        # line before is a +
        elif current_sign == V2 and current_sign == previous_sign:
            line_diff[current_sign].append(l[2:])
            line_diff[Q] = None

        if current_sign == Q and previous_sign == V1:
            line_diff[current_sign] = [l[2:], None]

        if current_sign == Q and previous_sign == V2:
            if line_diff[current_sign] is None:
                line_diff[current_sign] = [None, l[2:]]
            else:
                line_diff[current_sign][1] = l[2:]
        previous_sign = current_sign

    store_a_diff(line_diff, stored_diff)
    return stored_diff