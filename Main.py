import json, time, os, questionary
import pandas as pd

from copy import deepcopy
from typing import Dict, Tuple, List, Union
from concurrent.futures import (
    ThreadPoolExecutor,
    Future,
    as_completed,
)
from tqdm import tqdm, trange


from Helper.File import ChoseAFileToSave, ChoseFilesToOpen
from Helper.ProcessDeviceName import CPUName, GPUName
from Helper.Get3DMarkScore import (
    GetNameFromId,
    GetMedianScoreFromId,
    CPU_TESTSCENE,
    GPU_TESTSCENE,
    TESTSCENE_TYPE,
)


DATA_TYPE = Dict[int, Dict[str, Union[int, str]]]


def GetAllDeviceInfo(
    IsCpu: bool, TestSceneList: List[TESTSCENE_TYPE], *Args: int
) -> DATA_TYPE:
    IdToDeviceInfo: DATA_TYPE
    DEVICE: str = "CPU" if IsCpu else "GPU"
    MinId: int = 1
    MaxId: int = 4000 if IsCpu else 2000
    if len(Args) > 0:
        MinId = Args[0]
    if len(Args) > 1:
        MaxId = Args[1]

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as ThreadPool:
        # 从id获取型号
        print("------------------------------------------")
        print(f"Get {DEVICE} Name From ID ({MinId} To {MaxId})")
        Threads: List[Future] = []
        Threads.extend(
            ThreadPool.submit(GetNameFromId, i, IsCpu)
            for i in trange(MinId, MaxId + 1, desc="Tasks Submitting...", unit="tasks")
        )

        IdToDeviceInfo = {}
        with tqdm(
            as_completed(Threads),
            total=MaxId - MinId + 1,
            desc="Tasks Executing...",
            unit="tasks",
        ) as ProgressBar:
            for Thread in ProgressBar:
                try:
                    Result: Tuple[int, str] = Thread.result()
                    if Result[1] != "":
                        Id: int = Result[0]
                        Name: str = Result[1]

                        Item = {
                            f"{DEVICE} ID": Id,
                            f"{DEVICE} Name": Name,
                        }
                        for TestScene in TestSceneList:
                            Item[TestScene.value[2]] = -1

                        IdToDeviceInfo[Id] = Item

                        ProgressBar.set_description_str(
                            f"Tasks Executing... Current {DEVICE}:{Name:^35}"
                        )
                except Exception as e:
                    print(f"====== An Exception Raised! ======\n{e}")

        def GetScore(TestScene: TESTSCENE_TYPE) -> None:
            Threads.clear()
            Threads.extend(
                ThreadPool.submit(GetMedianScoreFromId, TestScene, i)
                for i in tqdm(
                    IdToDeviceInfo.keys(), desc="Tasks Submitting...", unit="tasks"
                )
            )

            with tqdm(
                as_completed(Threads),
                total=len(Threads),
                desc="Tasks Executing...",
                unit="tasks",
            ) as ProgressBar:
                for Thread in ProgressBar:
                    try:
                        Result: Tuple[int, int] = Thread.result()
                        Id: int = Result[0]
                        MedianScore: int = Result[1]

                        IdToDeviceInfo[Id][TestScene.value[2]] = MedianScore

                        CurrentDeviceName = IdToDeviceInfo[Result[0]][f"{DEVICE} Name"]
                        ProgressBar.set_description_str(
                            f"Tasks Executing... Current {DEVICE}:{CurrentDeviceName:^35}, Current Score:{MedianScore:^10}"
                        )
                    except Exception as e:
                        print(f"====== An Exception Raised! ======\n{e}")

        # 从id获取分数
        for TestScene in TestSceneList:
            print("------------------------------------------")
            print(f"Get {TestScene.value[2]}")
            GetScore(TestScene)

    return IdToDeviceInfo


# 将dict转为dataframe，导出excel
def ProcessData(Data: DATA_TYPE, IsCpu: bool) -> None:
    if len(Data) == 0:
        return

    Df = pd.DataFrame(Data.values())

    COL_NAME = "CPU Name" if IsCpu else "GPU Name"
    COL_NAME_GUID = f"{COL_NAME} GUID"
    COL_ID = "CPU ID" if IsCpu else "GPU ID"
    COL_VENDOR = "Vendor"
    COL_MODEL = "Model"
    COL_SCORES = [Column for Column in Df.columns if "3DMark" in Column]
    assert len(COL_SCORES) != 0
    COL_MAINSCORE = COL_SCORES[0]
    SCORE_LIMIT = 1
    GUID_CLASS = CPUName if IsCpu else GPUName

    # 剔除名字为空
    Df = Df[Df[COL_NAME] != ""]
    # 数据转为int
    Df[COL_ID] = Df[COL_ID].astype(int)

    Df[COL_MAINSCORE] = Df[COL_MAINSCORE].astype(int)
    # 剔除分数过低数据
    Df = Df[Df[COL_MAINSCORE] >= SCORE_LIMIT]
    # 根据Name生成GUID
    Df[COL_NAME_GUID] = Df[COL_NAME].apply(GUID_CLASS)
    # 新增 Vendor，Model 列
    VendorSeries = Df[COL_NAME_GUID].apply(lambda Obj: Obj.Vendor)
    Df.insert(Df.columns.get_loc(COL_NAME), COL_VENDOR, VendorSeries)
    ModelSeries = Df[COL_NAME_GUID].apply(lambda Obj: Obj.Model)
    Df.insert(Df.columns.get_loc(COL_NAME), COL_MODEL, ModelSeries)
    # 根据 Score 排序
    Df.sort_values(COL_MAINSCORE, ascending=False, inplace=True)
    Df.reset_index(drop=True, inplace=True)

    # 将dataframe写入excel
    with pd.ExcelWriter(
        ChoseAFileToSave(
            InitialFile=f"3DMark_{'CPU' if IsCpu else 'GPU'}ScoreData.xlsx"
        ),
        engine="openpyxl",
    ) as w:
        Df.to_excel(w, sheet_name="Sheet1", index=False)

    print(Df)


def Main() -> None:
    Mode = questionary.select(
        message="选择模式：\n"
        + "1) 全量更新，从3dmark爬取数据，保存到本地（json格式），然后处理数据导出Excel\n"
        + "2) 从本地的json文件中读取数据，处理数据导出Excel\n",
        choices=[
            "1) 全量更新",
            "2) 处理本地数据",
        ],
        show_selected=True,
    ).ask()

    IsCpu: bool
    Data: DATA_TYPE
    if "1)" in Mode:
        Device: str = questionary.select(
            message="要爬什么数据？\n",
            choices=["1) CPU", "2) GPU"],
            show_selected=True,
        ).ask()
        IsCpu: bool = "CPU" in Device

        TestSceneList: List[TESTSCENE_TYPE] = questionary.checkbox(
            message="选择测试项目（可多选）：\n",
            choices=[
                questionary.Choice(title=Test.value[2], value=Test, checked=Index == 0)
                for Index, Test in enumerate(CPU_TESTSCENE if IsCpu else GPU_TESTSCENE)
            ],
        ).ask()

        if len(TestSceneList) == 0:
            print(f"没有选择任何测试项目")
            return

        print("所选测试项目：")
        for TestScene in TestSceneList:
            print(TestScene.value[2])

        StartTime = time.time()
        Data = GetAllDeviceInfo(IsCpu, TestSceneList)
        print(f"\nTotal time:{time.time() - StartTime:.2f}s")

        InitialJsonFile = f"{'CPU' if IsCpu else 'GPU'}_{'_'.join([TestScene.name for TestScene in TestSceneList])}.json"
        SavePath = ChoseAFileToSave(
            FileTypes=[("Json File", ".json")],
            DefaultExtension=".json",
            InitialFile=InitialJsonFile,
            bForce=False,
        )
        if SavePath:
            with open(SavePath, "w", encoding="utf-8") as File:
                json.dump(Data, File)

    elif "2)" in Mode:
        # 将多个文件读入
        DataList: List[DATA_TYPE] = []
        Files: Tuple[str] = ChoseFilesToOpen(
            FileTypes=[("Json File", ".json")], bForce=False
        )
        if not Files:
            return
        for FilePath in Files:
            with open(FilePath, "r", encoding="utf-8") as File:
                DataList.append(json.load(File))

        # 将数据合并到一个dict中
        Data = dict()
        for TempData in DataList:
            Data.update(TempData)

        Value = next(iter(Data.values()))
        IsCpu = "CPU Name" in Value

    else:
        print("输入错误！\nInvalid input!\n")
        return

    ProcessData(Data, IsCpu)


if __name__ == "__main__":
    Main()
