"""

"""

from argparse import ArgumentParser
from control import Interpreter

def main():

    parser = ArgumentParser(description='Generate some compositions')
    parser.add_argument('--verbose', '-v',  action='store_true', default=False, help='Forces us to be verbose in our ouput')
    parser.add_argument('--output', '-o',   nargs=1, default='.', help='Forces us to place output files in a specific directory. Default is the current directory')
    parser.add_argument('--version',        action='version', version='1.0')

    args = parser.parse_args()
    args.output = str(args.output[0])

    interpreter = Interpreter(args)
    command = iter(interpreter)

    try:
        while True:
            next(command)
    except StopIteration:
        interpreter.exit('Exiting')
    except KeyboardInterrupt:
        interpreter.exit('Force Quitting')


# Call main if this is the main call
if __name__ == '__main__':
    main()

