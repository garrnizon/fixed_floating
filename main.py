import sys
from fixed import fixed
from floating import floating


def parse(args: list[str]) -> list:
    length = len(args)
    res = []
    if length != 3 and length != 5:
        sys.exit("Wrong number of arguments")
        
    if args[0] == 'f' or args[0] == 'h':
        res.append([args[0]])
    else:
        args[0] = args[0].split('.')
        if len(args[0]) != 2:
            sys.exit(f"Wrong format of numbers: {'.'.join(args[0])}")
            
        try:
            a = int(args[0][0])
            b = int(args[0][1])
        except Exception:
            sys.exit(f"Wrong format of numbers: {'.'.join(args[0])}")
            
        if a < 1:
            sys.exit('A must be >= 1')
            
        if b < 0:
            sys.exit('B must be >= 0')
            
        if a + b > 32:
            sys.exit('A + B must be <= 32')
            
        res.append(['z', a, b])

    if args[1] not in {str(i) for i in range(4)}:
        sys.exit(f"Invalid rounding format: {args[1]}")
        
    res.append(args[1])

    try:
        int(args[2], base=16)
    except TypeError:
        sys.exit(f"Invalid number format {args[2]}")
    res.append(args[2])

    if length == 3:
        return res

    if args[3] not in {'/', '+', '-', '*'}:
        sys.exit(f"Invalid operation format: {args[3]}")

    res.append(args[3])

    try:
        int(args[4], base=16)
    except TypeError:
        sys.exit(f"Invalid number format {args[4]}")
    res.append(args[4])

    return res


if __name__ == '__main__':
    args = parse([s.lower() for s in sys.argv[1:]])

    if args[0][0] == 'z':
        fixed(args[0][1], args[0][2], args[1], args[2:])
    if args[0][0] == 'h':
        floating(True, int(args[1]), args[2:])
    if args[0][0] == 'f':
        floating(False, int(args[1]), args[2:])

