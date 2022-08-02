import sys
from importlib import reload

import run
from common import __STDOUT__

def main():
    global __STDOUT__

    try:
        f_stdout = open(__STDOUT__, "w")
        sys.stdout = f_stdout
    except:
        f_stdout = None

    while (True):
        reset = run.iteration()

        if reset:
            reload(run)
            print("Resetted.", flush=True)


if __name__ == "__main__":
    main()


__all__ : list = []
