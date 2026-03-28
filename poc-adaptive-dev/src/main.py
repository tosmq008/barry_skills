import argparse
import sys

def say_hello(name: str) -> str:
    return f"Hello, {name}"

def main():
    parser = argparse.ArgumentParser(description="A simple Hello World CLI")
    parser.add_argument("--name", type=str, default="World", help="Name to greet")
    args = parser.parse_args()
    
    greeting = say_hello(args.name)
    print(greeting)
    sys.exit(0)

if __name__ == "__main__":
    main()
