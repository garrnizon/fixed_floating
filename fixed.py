import sys


def fixed(a, b, r, args):
    denom = 2 ** b

    class Fixed:
        def __init__(self, rep=None):
            self.value = 0
            if rep is None:
                self.value = None
                return
            try:
                self.value = int(rep, base=16)
            except:
                sys.exit(f"Invalid number format: {rep}")

            bin_repr = bin(self.value)
            if len(bin_repr) - 2 == a + b and bin_repr[2] == '1':
                self.value -= 2 ** (a + b)

        def __upd__(self):
            sign = 1
            if self.value < 0:
                self.value = - self.value
                sign = -1

            if len(bin(self.value)) - 2 > a + b:
                self.value = int(f"0b{bin(self.value)[-a - b:]}", base=2)

            bin_repr = bin(self.value)
            if len(bin_repr) - 2 == a + b and bin_repr[2] == '1':
                self.value -= 2 ** (a + b)

            self.value *= sign

        def __add__(self, other):
            res = Fixed()
            res.value = self.value + other.value
            return res

        def __sub__(self, other):
            res = Fixed()
            res.value = self.value - other.value
            return res

        def __div__(self, quot):
            res = Fixed()
            res.value = self.value
            sign = 1
            if r == '0':
                if res.value < 0:
                    sign = -1
                    res.value = -res.value
                res.value = sign * ((res.value * denom) // quot)

            elif r == '3':
                res.value = (res.value * denom) // quot

            elif r == '2':
                res.value = - ((- res.value * denom) // quot)
                return res

            elif r == '1':
                sign = 1
                if self.value < 0:
                    self.value = - self.value
                    sign = -1
                res.value = self.value * 2 * denom // quot

                if (self.value * denom) % quot != 0 and (self.value * 2 * denom) % quot == 0:
                    res.value += 1
                    if res.value % 4 != 0:
                        res.value -= 2

                elif res.value % 2 >= 1:
                    res.value += 2

                res.value //= 2
                res.value *= sign
            return res

        def __truediv__(self, other):
            if other.value == 0:
                if self.value == 0:
                    return Fixed()
                else:
                    sys.exit("Error: division by zero")

            res = Fixed()
            if other.value > 0:
                res.value = self.value
                quot = other.value
            else:
                res.value = -self.value
                quot = -other.value

            return res.__div__(quot)

        def __mul__(self, other):
            self.value *= other.value
            x = self.__div__(denom ** 2)
            return x

        def __str__(self) -> str:
            def div_by_1000(n: str) -> str:
                ans = []
                if n[0] == '-':
                    ans.append('-')
                    n = n[1:]
                if len(n) < 4:
                    n = f"{'0' * (4 - len(n))}{n}"
                ans.extend([n[:-3], '.', n[-3:]])
                return ''.join(ans)

            if len(args) == 3:
                self.__upd__()

            if r == '0':
                if self.value < 0:
                    res = - ((-self.value) * 1000 // denom)
                else:
                    res = self.value * 1000 // denom

                return div_by_1000(str(res))

            if r == '3':
                res = self.value * 1000 // denom
                return div_by_1000(str(res))

            if r == '2':
                res = - ((- self.value) * 1000 // denom)
                return div_by_1000(str(res))

            sign = 1
            if self.value < 0:
                self.value = - self.value
                sign = -1
            res = self.value * 10000 // denom

            if (self.value * 1000) % denom != 0 and (self.value * 1000 * 2) % denom == 0:
                res += 5
                if res % 20 != 0:
                    res -= 10
            elif res % 10 >= 5:
                res += 10
            res //= 10
            return div_by_1000(str(sign * res))

    def get_res(n1: Fixed, n2: Fixed, op):
        if op == '*':
            return n1 * n2

        if op == '+':
            return n1 + n2

        if op == '-':
            return n1 - n2

        if op == '/':
            return n1 / n2

        sys.exit(f'Unknown operation: {op}')

    if len(args) == 3:
        first = Fixed(args[0])
        second = Fixed(args[2])
        print(get_res(first, second, args[1]))
        return

    print(str(Fixed(args[0])))
