"""

"""
from traceback import print_exc
from argparse import ArgumentParser
from src.control import Manager

import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'


class UserInterface(ArgumentParser):

    """ User Interface

    Currently a commandline intepreter

    """

    def __init__(self, args):
        """ Initialize user interface """

        super().__init__()

        self.manager = Manager(args)

        self.add_argument('command', help='The command to run')
        self.add_argument('arguments', nargs='*', help='Arguments to pass to the function')

    def __iter__(self):
        """ Simply return self, as we will handle the action in __next__ """
        return self

    def __next__(self):
        """ Get next command from user and call the appropriate method with the given arguments """

        print('\n> ', end='')

        try:
            command = [ c.strip() for c in input().split(',') ]
            for c in command:
                user_input = self.parse_args(c.split(' '))
                getattr(self.manager, user_input.command)(*user_input.arguments)

        except (KeyboardInterrupt, EOFError):
            self.manager.exit('Force quitting')

        except FileExistsError:
            self.manager.error('We already created that file. Doing so again will delete all our saved data')

        except StopIteration:
            print_exc()
            self.manager.exit('Closing Mugen')
            raise

        except Exception:
            print_exc()



def main():

    """ Main function; called from bottom of file.

    Parse command line arguments. Create a user interface which can parse arguments.
    While the user inputs command do it. Handle some errors.
    """

    parser = ArgumentParser(description='Generate some compositions')
    parser.add_argument('--verbose', '-v',  action='store_true', default=False, help='Forces us to be verbose in our ouput')
    parser.add_argument('--output', '-o',   nargs=1, default='.', help='Forces us to place output files in a specific directory. Default is the current directory')
    parser.add_argument('--version',        action='version', version='1.0')

    args = parser.parse_args()
    args.output = str(args.output[0])

    ui = UserInterface(args)

    for command in ui:
        pass

