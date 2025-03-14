import requests
from requests import Response
from typing import Dict, Tuple, List, Literal, Union
from enum import Enum
from tenacity import retry, stop_after_attempt, RetryCallState
from datetime import date, timedelta


class TESTSCENE(Enum):
    CPU_SINGLECORE = ("crc P", "singleCoreScore", "Single Core Score")
    CPU_ALLCORES = ("crc P", "allCoresScore", "Multi Cores Score")
    GPU_GRAPHICS = ("spy P", "graphicsScore", "Timespy Score")
    GPU_GRAPHICS_X = ("spy X", "graphicsScore", "Timespy Extreme Score")
    GPU_RAYTRACING = ("pr P", "graphicsScore", "RayTracing Score")
    GPU_STEELNOMAD_DX = ("sw DX", "graphicsScore", "Steel Nomad DX12 Score")
    GPU_STEELNOMAD_VK = ("sw B", "graphicsScore", "Steel Nomad Vulkan Score")


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
    TestScene: Literal[
        TESTSCENE.CPU_SINGLECORE,
        TESTSCENE.CPU_ALLCORES,
        TESTSCENE.GPU_GRAPHICS,
        TESTSCENE.GPU_GRAPHICS_X,
        TESTSCENE.GPU_RAYTRACING,
        TESTSCENE.GPU_STEELNOMAD_DX,
        TESTSCENE.GPU_STEELNOMAD_VK,
    ],
    Id: int,
    time_range: int,
) -> str:
    test = TestScene.value[0]
    cpuId = Id if "CPU" in TestScene.name else ""
    gpuId = Id if "GPU" in TestScene.name else ""
    gpuCount = 1 if "GPU" in TestScene.name else 0
    scoreType = TestScene.value[1]
    if time_range > 0:
        startDate = f"{date.today()-timedelta(days=time_range)}"
        endDate = f"{date.today()}"
    else:
        startDate = ""
        endDate = ""
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
        f"startDate={startDate}",
        f"endDate={endDate}",
        "minGpuCoreClock=",
        "maxGpuCoreClock=",
        "minGpuMemClock=",
        "maxGpuMemClock=",
        "minCpuClock=",
        "maxCpuClock=",
    ]
    return "&".join(UrlParametersList)


def GetMedianScoreFromId(
    TestScene: Literal[
        TESTSCENE.CPU_SINGLECORE,
        TESTSCENE.CPU_ALLCORES,
        TESTSCENE.GPU_GRAPHICS,
        TESTSCENE.GPU_RAYTRACING,
    ],
    Id: int,
    time_range: int,
) -> Tuple[int, int]:
    UrlParameters: str = Get3DMarkUrlParameters(TestScene, Id, time_range)
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
