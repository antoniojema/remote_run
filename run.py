import time, json, os
from subprocess import Popen
from pathlib import Path
from typing import Tuple, Optional

from common import __CURRENT_ID__, __RUN_LIST__, __RUN_PATH__


def printFlush(*args, **kwargs) -> None:
    print(*args, **kwargs, flush=True)


def readJSON() -> Tuple[list, bool]:
    global __RUN_PATH__
    try:
        with open(__RUN_PATH__, "r") as fin:
            data = json.load(fin)
        if not type(data) is list:
            return list(), False
        else:
            return data, True
    except KeyboardInterrupt as e:
        printFlush(e)
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


def getStdout(file_str : Optional[str]) -> Path:
    if file_str is None:
        return getRandomStdout()
    else:
        file_path = Path(file_str).absolute()
        if file_path.is_dir():
            return getRandomStdout(file_path)
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
    print(f"    - stdout: {stdout}")
    print(f"    - PID: {pid}")
    print(f"    - ID : {__CURRENT_ID__}", flush=True)

    __CURRENT_ID__ += 1


def getRunByPID(pid : int) -> int:
    global __RUN_LIST__
    for i, run in enumerate(__RUN_LIST__):
        if run["pid"] == pid:
            return i
    return -1


def getRunByID(id : int):
    global __RUN_LIST__
    for i, run in enumerate(__RUN_LIST__):
        if run["id"] == id:
            return i
    return -1


def killProcess(c : dict) -> None:
    global __RUN_LIST__
    
    if "pid" in c:
        which = "pid"
        value = c[which]
        index = getRunByPID(value)
    elif "id" in c:
        which = "id"
        value = c[which]
        index = getRunByID(value)
    else:
        printFlush("Error killing process: Need to specify PID or ID")
        return
    
    if index == -1:
        printFlush(f"Error: Could not find process with {which} {value}")
        return
    
    try:
        print("Killing process:")
        print(f"    - Command: {__RUN_LIST__[index]['command']}")
        print(f"    - CWD: {__RUN_LIST__[index]['cwd']}")
        print(f"    - stdout: {__RUN_LIST__[index]['stdout']}")
        print(f"    - PID: {__RUN_LIST__[index]['pid']}")
        print(f"    - ID : {__RUN_LIST__[index]['id']}", flush=True)
        __RUN_LIST__[index]["process"].kill()
    except KeyboardInterrupt as e:
        print(e)
        exit(1)
    except Exception as e:
        print(f"Error killing proccess with with {which} {value}:\n{e}")


def showRunningProcesses() -> None:
    global __RUN_LIST__

    cleanRuns()

    print("Show processes: ")

    if len(__RUN_LIST__) == 0:
        printFlush("No processes running.")
    for i, run in enumerate(__RUN_LIST__):
        print(f"Process {i}:")
        print(f"    - Command: {run['command']}")
        print(f"    - CWD: {run['cwd']}")
        print(f"    - stdout: {run['stdout']}")
        print(f"    - PID: {run['pid']}")
        print(f"    - ID : {run['id']}", flush=True)


def runInternalCommand(c : dict) -> bool:
    reset : bool = False
    comm_name = c["internal_command"]
    if not type(comm_name) is str:
        printFlush("Error: Internal command must be a string.")
        return False

    if comm_name == "kill":
        killProcess(c)
    elif comm_name == "show running":
        showRunningProcesses()
    elif comm_name == "reset":
        reset = True
    else:
        printFlush(f"Error: Unknown internal command: {comm_name}")
    return reset


def cleanRuns() -> None:
    i = 0
    while i < len(__RUN_LIST__):
        run = __RUN_LIST__[i]
        if run["process"].poll() is not None:
            __RUN_LIST__.pop(i)
        else:
            i += 1


def runCommands(data : list) -> bool:
    reset : bool = False
    for c in data:
        try:
            if "internal_command" in c:
                reset = runInternalCommand(c)
            else:
                comm = c["command"]
                cwd = Path(c["cwd"]).absolute() if ("cwd" in c) else Path(__file__).parent
                stdout = getStdout(c["stdout"] if ("stdout" in c) else None)
                appendRun(comm, cwd, stdout)
        except KeyboardInterrupt as e:
            printFlush(e)
            exit(1)
        except Exception as e:
            printFlush(f"Error reading command:\n{e}")
    return reset


def iteration() -> bool:
    global __RUN_PATH__
    
    cleanRuns()

    data, all_good = readJSON()

    # Dump empty json
    with open(__RUN_PATH__, 'w') as fout:
        json.dump(list(), fout, indent=4)

    reset : bool = False
    if all_good:
        reset = runCommands(data)
    
    time.sleep(10)

    return reset
    
__all__ = "iteration"
