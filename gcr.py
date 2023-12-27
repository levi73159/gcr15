
import argparse
from compiler.parser import Parser
from compiler import command

def main():
    parser = argparse.ArgumentParser(description="Simple assembler and virtual machine")
    parser.add_argument("action", choices=["help", "compile", 'cr', "run"], help="Action to perform")

    # Arguments for the 'compile' action
    parser.add_argument("--out_file", help="Output file for compiled bytecode")
    parser.add_argument("--in_file", help="Input assembly file")
    parser.add_argument("--size", type=int, default=1000, help="Size of the memory")
    parser.add_argument('--author', type=str, default=None, help='author of the progrma')

    # Arguments for the 'run' action
    parser.add_argument("--file", help="File to run")
    parser.add_argument("--entry_point", type=int, help="Entry point in the file")

    args = parser.parse_args()

    if args.action == "help":
        print('usage: gcr.py [help, compile, run]')
        print('compile\t|\t[--in_file] [--out_file] [--size=1000] [--author(optional)] \t|   Compile the src code')
        print('CR\t|\t[--in_file] [--out_file] [--entry_point:int] [--author(optional)] [--size=1000] \t|   Compile the src code and run it')
        print('run\t|\t[--file] \t  [--entry_point:int] \t\t|   Runs the compiled file')
    elif args.action == "compile":
        print("Compiling...")
        parser = Parser(args.out_file, args.in_file, args.size)
        parser.parse(args.author)
        print("Compilation complete.")
    elif args.action == "cr":
        print("Compiling...")
        parser = Parser(args.out_file, args.in_file, args.size)
        parser.parse(args.author)
        print("Compilation complete.")
        runner = command.Runner(args.out_file, args.entry_point)
        memory = runner.load()
        runner.run(memory)
    elif args.action == "run":
        runner = command.Runner(args.file, args.entry_point)
        memory = runner.load()
        runner.run(memory)


if __name__ == "__main__":
    main()
