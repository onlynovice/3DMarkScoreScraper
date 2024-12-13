import tkinter as tk
from tkinter import filedialog
from typing import Iterable, Tuple, Union, Literal


def ChoseAFileToOpen(
    FileTypes: Iterable[Tuple[str, str]] = [("All Files", "*")],
    bForce: bool = True,
) -> str:
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()

    FilePath = ""
    while True:
        FilePath = filedialog.askopenfilename(filetypes=FileTypes)
        if FilePath or not bForce:
            break

    root.destroy()
    return FilePath


def ChoseFilesToOpen(
    FileTypes: Iterable[Tuple[str, str]] = [("All Files", "*")],
    bForce: bool = True,
) -> Union[Tuple[str], str]:
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()

    FilePath: Union[Tuple[str], str]
    while True:
        FilePath = filedialog.askopenfilenames(filetypes=FileTypes)
        if FilePath or not bForce:
            break

    root.destroy()
    return FilePath


def ChoseAFileToSave(
    FileTypes: Iterable[Tuple[str, str]] = [("Excel", ".xlsx .xls")],
    DefaultExtension: str = ".xlsx",
    InitialDir:str = None,
    InitialFile: str = None,
    bForce: bool = True,
) -> str:
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()

    FilePath = ""
    while True:
        FilePath = filedialog.asksaveasfilename(
            defaultextension=DefaultExtension,
            filetypes=FileTypes,
            initialdir=InitialDir,
            initialfile=InitialFile,
        )
        if FilePath or not bForce:
            break

    root.destroy()
    return FilePath


def ChoseDirectory(bForce: bool = True) -> str:
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()

    DirPath = ""
    while True:
        DirPath = filedialog.askdirectory(mustexist=True)
        if DirPath or not bForce:
            break

    root.destroy()
    return DirPath
