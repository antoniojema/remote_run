import time, json, sys, os
from subprocess import Popen
from pathlib import Path
from typing import Tuple, Optional, TextIO


__STDOUT__   : Path = Path(__file__).parent / "stdout.txt"
__RUN_PATH__ : Path = Path(__file__).parent / "run.json"
__RUN_LIST__ : list = []
__CURRENT_ID__ : int = 0


def printFlush(*args, **kwargs) -> None:
    print(*args, **kwargs, flush=True)


def setup() -> None:
    global __STDOUT__

    try:
        f_stdout = open(__STDOUT__, "w")
        sys.stdout = f_stdout
    except:
        f_stdout = None


def readJSON() -> Tuple[list, bool]:
    global __RUN_PATH__
    try:
        with open(__RUN_PATH__, "r") as fin:
            data = json.load(fin)
        if not type(data) is list:
            return list(), False
        else:
            return data, True
    except KeyboardInterrupt:
        printFlush("Keyboard interrupt.")
        exit(1)
    except Exception as e:
        printFlush(f"Exception reading JSON:\n{e}")
        return list(), False


def getRandomStdout(folder : Optional[Path] = None) -> Path:
    if folder is None:
        file_folder = Path(__file__).parent / "default_stdouts"
    elif not folder.is_dir():
        file_folder = Path(__file__).parent / "default_stdouts"
    else:
        file_folder = folder
    
    os.makedirs(file_folder, exist_ok=True)
    
    i = 0
    while (True):
        file_path = file_folder / f"stdout_{i}.txt"
        if not file_path.exists():
            break
        else:
            i += 1
    
    file_path.touch()
    return file_path


def getStdout(file_str : str) -> Path:
    file_path = Path(file_str).absolute()
    if file_path.is_dir():
        return getRandomStdout()
    else:
        file_folder = file_path.parent
        if file_folder == file_path:
            return getRandomStdout()
        elif file_path.exists():
            return getRandomStdout(file_folder)
        else:
            os.makedirs(file_folder, exist_ok=True)
            file_path.touch()
            return file_path


def appendRun(comm : list, cwd : Path, stdout : Path) -> None:
    global __RUN_LIST__, __CURRENT_ID__

    f_stdout = open(stdout, "w")
    proc = Popen(
        comm,
        cwd=cwd,
        stdout=f_stdout,
        stderr=f_stdout
    )
    pid = proc.pid
    
    __RUN_LIST__.append({
        "command" : comm,
        "cwd" : cwd,
        "process": proc,
        "stdout" : stdout,
        "pid" : pid,
        "id" : __CURRENT_ID__,
    })

    print("New process:")
    print(f"    - Command: {comm}")
    print(f"    - CWD: {cwd}")
    print(f"    - PID: {pid}")
    print(f"    - ID : {__CURRENT_ID__}", flush=True)
    
    __CURRENT_ID__ += 1


def runCommands(data : list) -> None:
    for c in data:
        try:
            if "internal_command" in c:
                pass
            else:
                comm = c["command"]
                cwd = Path(c["cwd"]).absolute() if "cwd" in c else Path(__file__).parent
                stdout = getStdout(c["stdout"] if "stdout" in c else None)
                appendRun(comm, cwd, stdout)
        except KeyboardInterrupt:
            printFlush("Keyboard interrupt.")
            exit(1)
        except Exception as e:
            printFlush(f"Error reading command:\n{e}")


def main():
    global __RUN_PATH__

    setup()

    while (True):
        data, all_good = readJSON()

        if all_good:
            runCommands(data)
        
        # Dump empty json
        with open(__RUN_PATH__, 'w') as fout:
            json.dump(list(), fout, indent=4)
        
        time.sleep(60)


if __name__ == "__main__":
    main()


__all__ : list = []
