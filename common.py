from pathlib import Path

__STDOUT__   : Path = Path(__file__).parent / "stdout.txt"
__RUN_PATH__ : Path = Path(__file__).parent / "run.json"
__RUN_LIST__ : list = []
__CURRENT_ID__ : int = 0