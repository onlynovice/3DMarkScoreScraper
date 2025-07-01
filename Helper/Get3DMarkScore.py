import requests
from requests import Response
from typing import Dict, Tuple, List, Literal, Union
from enum import Enum
from tenacity import retry, stop_after_attempt, RetryCallState


class CPU_TESTSCENE(Enum):
    SingleCore = ("crc P", "singleCoreScore", "3DMark CPU Profile 1 thread")
    TwoCores = ("crc P", "twoCoresScore", "3DMark CPU Profile 2 threads")
    FourCores = ("crc P", "fourCoresScore", "3DMark CPU Profile 4 threads")
    EightCores = ("crc P", "eightCoresScore", "3DMark CPU Profile 8 threads")
    SixteenCores = ("crc P", "sixteenCoresScore", "3DMark CPU Profile 16 threads")
    AllCores = ("crc P", "allCoresScore", "3DMark CPU Profile Max threads")


class GPU_TESTSCENE(Enum):
    TimeSpy = ("spy P", "graphicsScore", "3DMark Time Spy")
    TimeSpyExtreme = ("spy X", "graphicsScore", "3DMark Time Spy Extreme")
    PortRoyal = ("pr P", "graphicsScore", "3DMark Port Royal")
    SpeedWay = ("sw P", "graphicsScore", "3DMark Speed Way")
    SteelNomadDX12 = ("sw DX", "graphicsScore", "3DMark Steel Nomad DX12")
    SteelNomadVulkan = ("sw B", "graphicsScore", "3DMark Steel Nomad Vulkan")
    SteelNomadLightDX12 = ("sw DXLT", "graphicsScore", "3DMark Steel Nomad Light DX12")
    SteelNomadLightVulkan = (
        "sw VKLT",
        "graphicsScore",
        "3DMark Steel Nomad Light Vulkan",
    )
    SolarBay = ("sb P", "graphicsScore", "3DMark Solar Bay")
    FireStrike = ("fs P", "graphicsScore", "3DMark Fire Strike")
    FireStrikeExtreme = ("fs X", "graphicsScore", "3DMark Fire Strike Extreme")
    FireStrikeUltra = ("fs R", "graphicsScore", "3DMark Fire Strike Ultra")
    WildLife = ("wl P", "graphicsScore", "3DMark Fire Wild Life")
    WildLifeExtreme = ("wl X", "graphicsScore", "3DMark Fire Wild Life Extreme")
    NightRaid = ("nr P", "graphicsScore", "3DMark Night Raid")


TESTSCENE_TYPE = Literal[
    CPU_TESTSCENE.SingleCore,
    CPU_TESTSCENE.TwoCores,
    CPU_TESTSCENE.FourCores,
    CPU_TESTSCENE.EightCores,
    CPU_TESTSCENE.SixteenCores,
    CPU_TESTSCENE.AllCores,
    GPU_TESTSCENE.TimeSpy,
    GPU_TESTSCENE.TimeSpyExtreme,
    GPU_TESTSCENE.PortRoyal,
    GPU_TESTSCENE.SpeedWay,
    GPU_TESTSCENE.SteelNomadDX12,
    GPU_TESTSCENE.SteelNomadVulkan,
    GPU_TESTSCENE.SteelNomadLightDX12,
    GPU_TESTSCENE.SteelNomadLightVulkan,
    GPU_TESTSCENE.SolarBay,
    GPU_TESTSCENE.FireStrike,
    GPU_TESTSCENE.FireStrikeExtreme,
    GPU_TESTSCENE.FireStrikeUltra,
    GPU_TESTSCENE.WildLife,
    GPU_TESTSCENE.WildLifeExtreme,
    GPU_TESTSCENE.NightRaid,
]


def ErrorCallback(CallState: RetryCallState) -> None:
    print(
        f"Original function arguments: args={CallState.args}, kwargs={CallState.kwargs}"
    )
    Outcome = CallState.outcome
    if Outcome and Outcome.failed:
        raise Outcome.exception()


@retry(
    stop=stop_after_attempt(max_attempt_number=5), retry_error_callback=ErrorCallback
)
def Get(Url: str) -> Response:
    return requests.get(Url, headers={"Accept": "application/json"}, timeout=10)


def Get3DMarkUrlParameters(
    TestScene: TESTSCENE_TYPE,
    Id: int,
) -> str:
    IsCpu: bool = "CPU" in TestScene.__class__.__name__
    test = TestScene.value[0]
    cpuId = Id if IsCpu else ""
    gpuId = Id if not IsCpu else ""
    gpuCount = 1 if not IsCpu else 0
    scoreType = TestScene.value[1]
    UrlParametersList: List[str] = [
        f"test={test}",
        f"cpuId={cpuId}",
        f"gpuId={gpuId}",
        f"gpuCount={gpuCount}",
        "gpuType=ALL",
        "deviceType=ALL",
        "storageModel=ALL",
        "memoryChannels=0",
        "country=",
        f"scoreType={scoreType}",
        "hofMode=false",
        "showInvalidResults=false",
        "freeParams=",
        "minGpuCoreClock=",
        "maxGpuCoreClock=",
        "minGpuMemClock=",
        "maxGpuMemClock=",
        "minCpuClock=",
        "maxCpuClock=",
    ]
    return "&".join(UrlParametersList)


def GetMedianScoreFromId(
    TestScene: TESTSCENE_TYPE,
    Id: int,
) -> Tuple[int, int]:
    UrlParameters: str = Get3DMarkUrlParameters(TestScene, Id)
    Url: str = f"https://www.3dmark.com/proxycon/ajax/medianscore?{UrlParameters}"
    Response = Get(Url)
    try:
        return Id, int(Response.json()["median"])
    except:
        return Id, 0


def GetNameFromId(Id: int, IsCpu: bool) -> Tuple[int, str]:
    Device: str = "cpu" if IsCpu else "gpu"
    Url: str = f"https://www.3dmark.com/proxycon/ajax/search/{Device}id?id={Id}"
    Response = Get(Url)
    return Id, Response.json()[f"{Device}Name"]


def Test():
    # 4090 TimeSpy
    UrlParameters: str = Get3DMarkUrlParameters(GPU_TESTSCENE.TimeSpy, 1509)
    Url: str = f"https://www.3dmark.com/proxycon/ajax/medianscore?{UrlParameters}"
    Response = Get(Url)
    try:
        return int(Response.json()["median"])
    except:
        return 0


if __name__ == "__main__":
    print(Test())
