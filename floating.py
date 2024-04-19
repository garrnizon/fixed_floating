import sys


def floating(is_half, rounding, args: list[str]):
    class Constants:
        exp_len = 8
        man_len = 23

        if is_half:
            exp_len = 5
            man_len = 10

        total_len = exp_len + man_len + 1
        shift = 2 ** (exp_len - 1) - 1
        max_exp = shift
        min_exp = - max_exp + 1

        accuracy = exp_len - 2  # 3 for h, 6 for f - digits to print

        nan = "1" * total_len
        zero_pos = '0' * total_len
        zero_neg = '1' + '0' * (total_len - 1)
        inf_pos = '0' + '1' * exp_len + '0' * man_len
        inf_neg = '1' * (exp_len + 1) + '0' * man_len
        min_pos = '0' * (total_len - 1) + '1'
        min_neg = '1' + '0' * (total_len - 2) + '1'
        max_pos = '0' + '1' * (exp_len - 1) + '0' + '1' * man_len
        max_neg = '1' * exp_len + '0' + '1' * man_len
        min_norm_neg = '1' + '0' * (exp_len - 1) + '1' + '0' * man_len
        min_norm_pos = '0' * exp_len + '1' + '0' * man_len

    consts = Constants()

    def is_zero(bin_repr: str) -> bool:
        return bin_repr == consts.zero_neg or bin_repr == consts.zero_pos

    def is_inf(bin_repr: str) -> bool:
        return bin_repr == consts.inf_neg or bin_repr == consts.inf_pos

    def is_nan(bin_repr: str) -> bool:
        return (not is_inf(bin_repr)) and (bin_repr[1:1 + consts.exp_len] == '1' * consts.exp_len)

    def is_denorm(bin_repr: str) -> bool:
        return (not is_zero(bin_repr)) and (bin_repr[1:1 + consts.exp_len] == '0' * consts.exp_len)

    class Floating:
        def __init__(self, repr):
            self.sign = 0
            self.exp = 0
            self.man_val = 0
            self.is_norm = False
            self.is_zero = False
            self.is_inf = False
            self.is_denorm = False
            self.is_nan = False
            self.bin_repr = '0' * (consts.total_len - len(repr)) + repr
            self.sign = int(self.bin_repr[0])

            if is_zero(self.bin_repr):
                self.is_zero = True
                return

            if is_inf(self.bin_repr):
                self.is_inf = True
                return

            if is_nan(self.bin_repr):
                self.is_nan = True
                return

            if is_denorm(self.bin_repr):
                self.is_denorm = True
                self.exp = consts.min_exp
                self.exp -= self.bin_repr[-consts.man_len:].index('1') + 1
                self.man_val = int(self.bin_repr[-consts.man_len:], base=2)
                return

            # norm
            self.is_norm = True
            self.exp = int(self.bin_repr[1:1 + consts.exp_len], base=2) - consts.shift
            self.man_val = int(f"1{self.bin_repr[-consts.man_len:]}", base=2)

        def __str__(self):
            if self.is_inf:
                return f"{'-' * self.sign}inf"
            if self.is_zero:
                return f"{'-' * self.sign}0x0.{'0' * consts.accuracy}p+0"
            if self.is_nan:
                return 'nan'

            res = []
            bin_man = bin(self.man_val)[3:]
            bin_man = bin_man + '0' * (4 * consts.accuracy - len(bin_man))

            res.append('-' * self.sign)
            res.append('0x1.')
            for i in range(0, len(bin_man), 4):
                res.append(hex(int(bin_man[i:i + 4], base=2))[-1])

            res.append('p')

            if self.exp >= 0:
                res.append('+')
            res.append(str(self.exp))

            return ''.join(res)

        def __next__(self, bin_man: str):
            res = bin_man[:consts.man_len]

            if '1' not in bin_man[consts.man_len:]:
                return res, 0

            if '0' in res:
                bin_res = bin(int(res, base=2) + 1)[2:]
                return f"{'0' * (consts.man_len - len(bin_res))}{bin_res}", 0

            return '0' * consts.man_len, 1

        def __prev__(self, bin_man: str):
            res = bin_man[:consts.man_len]
            if '1' in bin_man[consts.man_len:]:
                return res, 0

            if '1' in res:
                bin_res = bin(int(res, base=2) - 1)[2:]
                return f"{'0' * (consts.man_len - len(bin_res))}{bin_res}", 0

            return '1' * consts.man_len, -1

        def __round__(self, b, sign):
            if '1' not in b[consts.man_len:]:
                return b[:consts.man_len], 0
            if rounding == 0:
                return b[:consts.man_len], 0

            if rounding == 1:
                if b[consts.man_len] == '0':
                    return self.__prev__(b)
                if '1' in b[consts.man_len + 1:]:
                    return self.__next__(b)
                if b[consts.man_len - 1] == '0':
                    return self.__prev__(b)
                return self.__next__(b)

            if rounding == 2:
                if sign:
                    return self.__prev__(b)

                return self.__next__(b)

            if rounding == 3:
                if sign:
                    return self.__next__(b)

                return self.__prev__(b)

        def __transform__(self, man, bin_man, sgn, exp):
            if exp > consts.max_exp:  # больше наибольшего
                if rounding == 0:
                    if sgn:
                        return Floating(consts.max_neg)
                    return Floating(consts.max_pos)

                if rounding == 1:
                    if sgn:
                        return Floating(consts.inf_neg)
                    return Floating(consts.inf_pos)

                if rounding == 2:
                    if sgn:
                        return Floating(consts.max_neg)
                    return Floating(consts.inf_pos)

                if sgn:
                    return Floating(consts.inf_neg)
                return Floating(consts.max_pos)

            if exp < consts.min_exp - consts.man_len:  # меньше наименьшего
                if rounding < 2:
                    if sgn:
                        return Floating(consts.zero_neg)
                    return Floating(consts.zero_pos)

                if rounding == 2:
                    if sgn:
                        return Floating(consts.zero_neg)
                    return Floating(consts.min_pos)

                if sgn:
                    return Floating(consts.min_neg)
                return Floating(consts.zero_pos)

            if exp < consts.min_exp:  # denorm
                d = consts.min_exp - exp - 1
                man += 2 ** (len(bin_man) + d)
                bin_man = bin(man)
                bin_man, exp_rounding_change = self.__round__(bin_man[3:], sgn)
                if exp_rounding_change == 1:
                    return Floating(f"{sgn}{'0' * (consts.exp_len - 1)}1{'0' * consts.man_len}")
                return Floating(f"{sgn}{'0' * consts.exp_len}{'0' * (consts.man_len - len(bin_man))}{bin_man}")

            # norm
            bin_man, exp_rounding_change = self.__round__(bin_man[1:], sgn)
            if exp_rounding_change == 1 and exp == consts.max_exp:
                if sgn:
                    return Floating(consts.inf_neg)
                return Floating(consts.inf_pos)
            if exp_rounding_change == -1 and exp == consts.min_exp:
                return Floating(f"{sgn}{'0' * consts.exp_len}{'0' * (consts.man_len - 1)}1")

            bin_exp = bin(exp + consts.shift + exp_rounding_change)[2:]
            return Floating(f"{sgn}{'0' * (consts.exp_len - len(bin_exp))}{bin_exp}{bin_man}")

        def __mul__(self, other):
            if self.is_inf:
                if other.is_zero:
                    return Floating(consts.nan)
                self.sign = self.sign ^ other.sign
                return self

            if self.is_zero:
                if other.is_inf:
                    return Floating(consts.nan)
                return self

            if other.is_inf:
                other.sign = self.sign ^ other.sign
                return other

            if other.is_zero:
                return other

            sgn = self.sign ^ other.sign

            if self.is_denorm and other.is_denorm:  # меньше наименьшего
                if rounding < 2:
                    if sgn:
                        return Floating(consts.zero_neg)
                    return Floating(consts.zero_pos)

                if rounding == 2:
                    if sgn:
                        return Floating(consts.zero_neg)
                    return Floating(consts.min_pos)

                if sgn:
                    return Floating(consts.min_neg)
                return Floating(consts.zero_pos)

            man = self.man_val * other.man_val
            bin_man = bin(man)[2:]

            to_add = len(bin_man) - 2 * consts.man_len - 1

            if self.is_denorm:
                to_add += (consts.min_exp - self.exp)
            elif other.is_denorm:
                to_add += (consts.min_exp - other.exp)

            exp = self.exp + other.exp + to_add
            return self.__transform__(man, bin_man, sgn, exp)

        def __truediv__(self, other):
            sgn = self.sign ^ other.sign

            if other.is_zero:
                if self.is_zero:
                    return Floating(consts.nan)
                if sgn:
                    return Floating(consts.inf_neg)
                return Floating(consts.inf_pos)

            if self.is_zero:
                if sgn:
                    return Floating(consts.zero_neg)
                return Floating(consts.zero_pos)

            if other.is_inf:
                if self.is_inf:
                    return Floating(consts.nan)
                if sgn:
                    return Floating(consts.zero_neg)
                return Floating(consts.zero_pos)

            if self.is_inf:
                if sgn:
                    return Floating(consts.inf_neg)
                return Floating(consts.inf_pos)

            if self.man_val < other.man_val:
                self.man_val *= 2
                self.exp -= 1

            while self.man_val > other.man_val * 2:
                other.man_val *= 2
                other.exp -= 1

            man = (self.man_val * 2 ** (consts.man_len * 3)) // other.man_val
            exp = self.exp - other.exp
            bin_man = bin(man)[2:]
            return self.__transform__(man, bin_man, sgn, exp)

        def __eq__(self, other):
            return self.bin_repr == other.bin_repr

        def __neg__(self):  # взятие противоположного
            return Floating(f"{1 - self.sign}{self.bin_repr[1:]}")

        def __add__(self, other):
            if self.is_inf:
                if other.is_inf and self != other:
                    return Floating(consts.nan)

                return self

            if other.is_inf:
                return other

            if self.is_zero:
                if self == Floating(consts.zero_pos) and other == Floating(consts.zero_neg):
                    return self
                return other

            if other.is_zero:
                return self

            if other == self.__neg__():
                return Floating(consts.zero_pos)

            diff = self.exp - other.exp

            if diff < 0 or (diff == 0 and self.man_val < other.man_val):
                return other + self
            # |self| >= |other|
            if self.is_denorm:
                while self.man_val < 2 ** consts.man_len:
                    self.man_val *= 2
            if other.is_denorm:
                while other.man_val < 2 ** consts.man_len:
                    other.man_val *= 2

            sgn = self.sign
            man = self.man_val * 2 ** diff
            to_add = - len(bin(man))
            if other.sign == self.sign:
                man += other.man_val
            else:
                man -= other.man_val  # > 0 because self >= other

            to_add += len(bin(man))
            exp = self.exp + to_add

            while man < 2 ** consts.man_len:
                man *= 2
            bin_man = bin(man)[2:]
            return self.__transform__(man, bin_man, sgn, exp)

        def __sub__(self, other):
            return self + other.__neg__()
            # if self.sign != other.sign:
            #     return self.__neg__() + other

    def get_res(n1: Floating, n2: Floating, op):
        if n1.is_nan or n2.is_nan:
            return Floating(consts.nan)
        if op == '*':
            return n1 * n2

        if op == '+':
            return n1 + n2

        if op == '-':
            return n1 - n2

        if op == '/':
            return n1 / n2

        sys.exit(f'Unknown operation: {op}')

    def is_valid_number_format(repr: str):
        try:
            return bin(int(repr, base=16))[2:]
        except ValueError:
            sys.exit(f"Invalid number format: {repr}")

    number = Floating(is_valid_number_format(args[0]))
    if len(args) == 3:
        second_number = Floating(is_valid_number_format(args[2]))
        number = get_res(number, second_number, args[1])

    print(number)
