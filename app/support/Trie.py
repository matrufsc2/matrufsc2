from app.support.sort import sort

__author__ = 'fernando'


class Trie(dict):
    __slots__ = ["editable"]

    def __init__(self):
        super(Trie, self).__init__()
        self.editable = True

    def __getstate__(self):
        s = {
            "data": self.copy(),
        }
        if self.editable is True:
            s["editable"] = self.editable
        return s

    def __setstate__(self, state):
        self.editable = state.pop("editable", False)
        self.update(state.pop("data", {}))

    def get_words(self):
        return sorted(self.iterkeys())

    def get(self, key, d=None):
        editable = self.editable
        if editable is True:
            self.editable = False
        try:
            val = self[key]
            if editable is True:
                self.editable = editable
            return val
        except KeyError:
            if editable is True:
                self.editable = editable
            return d

    def get_list(self, item):
        item_length = len(item)
        words = (word for word in self.iterkeys() if word[:item_length] == item)
        queue = [self[word] for word in words]
        while len(queue) > 1:
            item_old = None
            temp = []
            for item in queue:
                if item_old is None:
                    item_old = item
                else:
                    temp.append(sort(item, item_old))
                    item_old = None
            if item_old is not None:
                temp[-1] = sort(item_old, temp[-1])
            queue = temp
        if queue:
            return list(queue[0])
        return []

    def __getitem__(self, item):
        try:
            value = super(Trie, self).__getitem__(item)
        except KeyError:
            if self.editable:
                self[item] = value = []
            else:
                value = []
        return value
