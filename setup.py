import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["numpy", "PyQt6", "datetime"],
    "include_files": [("./_internal/", "_internal/"), ("./week_schedules/", "week_schedules/"), ("./sound.wav", "sound.wav")],
    #"include_files": [("./_internal/", "_internal/"), ("./week_schedules/", "week_schedules/")],
    "optimize": 1,
}

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="Chrono-Compass",
    version="0.1",
    description="Daily Scheduler",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, icon="_internal/icon.ico", target_name="Chrono-Compass")],
)