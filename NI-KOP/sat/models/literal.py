from utils.helpers import subscript_map


class Literal:
    def __init__(self, id: int, sign: int):
        """
        :param id: literal identifier
        :param sign: represents negation
        """
        self.id = id
        self.sign = sign

    def __str__(self):
        suffix_symbol = '' if self.sign > 0 else '\''
        return f"{'' if self.sign > 0 else '¬'}x{self.subscript_id}{suffix_symbol}"

    @property
    def subscript_id(self):
        return ''.join([subscript_map[char] for char in str(self.id)])
