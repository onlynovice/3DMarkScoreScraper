import re
from typing import Set, List, Literal, Tuple


def IsInt(Str: str) -> bool:
    try:
        int(Str)
        return True
    except ValueError:
        return False


class CPUName:
    @staticmethod
    def RemoveInfo(TokenList: List[str], PatternStr: str) -> List[str]:
        # 去除满足特定正则表达式的项
        Pattern = re.compile(PatternStr)

        IndexToDelete: List[int] = []
        for i, Token in enumerate(TokenList):
            if Pattern.search(Token):
                IndexToDelete.append(i)
        for i in reversed(IndexToDelete):
            del TokenList[i]

        return TokenList

    @staticmethod
    def GetModel(TokenList: List[str]) -> Tuple[List[str], str]:
        Model: str = "Unknown"
        ModelIndex: int = -1
        Pattern = re.compile(r"\d{2,}")
        for i, Token in enumerate(TokenList):
            if Pattern.search(Token):
                Model = Token
                ModelIndex = i
                break

        if "-" in Model:
            TempList = Model.split("-")
            TokenList[ModelIndex] = TempList[0]
            Model = TempList[1]
        return TokenList, Model

    def __init__(self, Name: str) -> None:
        self.Vendor: str = "Unknown"
        self.Model: str = "Unknown"
        self.Features: Set[str] = set()

        # 规范化，将一些不规则内容去除
        # 全部大写
        Name = Name.upper()
        # 去掉(R), (TM)
        Name = Name.replace("(R)", "").replace("(TM)", "")
        # 去掉其他特殊符号，(), * 等
        Name = re.sub(r"[^a-zA-Z0-9- ]+", "", Name)
        TokenList = Name.split(" ")

        # 去掉 Processor, xx-cores, for 13th gen cpu等标识
        TokenList = CPUName.RemoveInfo(
            TokenList, r"^CPU$|^FOR$|^\d+TH$|^GEN$|^PROCESSOR|\d+-CORES$"
        )

        # 取得生产商, 并移除
        if len(TokenList) != 0:
            self.Vendor = TokenList[0]
            TokenList = CPUName.RemoveInfo(TokenList, self.Vendor)

        # 取得型号, 并移除
        TokenList, self.Model = CPUName.GetModel(TokenList)
        if self.Model != "Unknown":
            TokenList = CPUName.RemoveInfo(TokenList, self.Model)

        # 剩下的 Token 全部视为 Feature
        self.Features.update(TokenList)

    def __hash__(self) -> int:
        if isinstance(self.Features, set):
            self.Features = frozenset(self.Features)
        return hash((self.Vendor, self.Model, self.Features))

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, self.__class__):
            return (
                self.Vendor == __value.Vendor
                and self.Model == __value.Model
                and self.Features == __value.Features
            )
        return False

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.Vendor}, {self.Model}, {self.Features})"
        )


class GPUName:
    @staticmethod
    def RemoveSpecialInfo(
        TokenList: List[str], Unit: Literal["GB", "MHZ"]
    ) -> List[str]:
        # 去除特殊信息（如 8 GB/ 2000 MHz 此类， 数据 + 单位）
        # 这种信息主要有三种不同的写法
        IndexToDelete: List[int] = []
        for i, Token in enumerate(TokenList):
            if Unit not in Token:
                continue

            # a) 1060-3GB -> 去除后缀，1060
            HyphenIndex = Token.find("-")
            if HyphenIndex != -1:
                TokenList[i] = Token[:HyphenIndex]
                continue

            # b) 20 GB -> 删除 20 和 GB
            if Token == Unit:
                assert i > 1
                Value = TokenList[i - 1]
                assert IsInt(Value)
                # assert int(Value) < 100
                IndexToDelete.extend([i - 1, i])

            # c) 20GB -> 直接删除
            else:
                Value = Token[: Token.find(Unit)]
                assert IsInt(Value)
                # assert int(Value) < 100
                IndexToDelete.append(i)

        for i in reversed(IndexToDelete):
            del TokenList[i]

        return TokenList

    @staticmethod
    def RemoveInfo(TokenList: List[str], PatternStr: str) -> List[str]:
        # 去除满足特定正则表达式的项
        Pattern = re.compile(PatternStr)

        IndexToDelete: List[int] = []
        for i, Token in enumerate(TokenList):
            if Pattern.search(Token):
                IndexToDelete.append(i)
        for i in reversed(IndexToDelete):
            del TokenList[i]

        return TokenList

    @staticmethod
    def GetModel(TokenList: List[str]) -> str:
        Pattern = re.compile(r"^(?!R)\D*\d|TITAN|VEGA|FURY|^V.*")
        for Token in TokenList:
            if Pattern.search(Token):
                return Token
        return "Unknown"

    def __init__(self, Name: str) -> None:
        self.Vendor: str = "Unknown"
        self.Model: str = "Unknown"
        self.Features: Set[str] = set()
        self.DisplayName: str = Name

        # 直接将一部分标识去除，作为显示用的名称
        if "(notebook)" in self.DisplayName:
            self.DisplayName = self.DisplayName.replace("(notebook)", "")
        if "(Notebook)" in self.DisplayName:
            self.DisplayName = self.DisplayName.replace("(Notebook)", "")
        if "(Laptop)" in self.DisplayName:
            self.DisplayName = self.DisplayName.replace("(Laptop)", "")
        if "AMD" in self.DisplayName:
            self.DisplayName = self.DisplayName.replace("AMD", "")
        if "Radeon" in self.DisplayName:
            self.DisplayName = self.DisplayName.replace("Radeon", "")
        if "NVIDIA" in self.DisplayName:
            self.DisplayName = self.DisplayName.replace("NVIDIA", "")
        if "GeForce" in self.DisplayName:
            self.DisplayName = self.DisplayName.replace("GeForce", "")
        if "Intel" in self.DisplayName:
            self.DisplayName = self.DisplayName.replace("Intel", "")
        if "Arc" in self.DisplayName:
            self.DisplayName = self.DisplayName.replace("Arc", "")
        self.DisplayName = self.DisplayName.strip()

        # 规范化，将一些不规则内容去除
        # 全部大写
        Name = Name.upper()
        # 去掉(R), (TM)
        Name = Name.replace("(R)", "").replace("(TM)", "")
        # 去掉其他特殊符号，(), * 等
        Name = re.sub(r"[^a-zA-Z0-9- ]+", "", Name)

        TokenList = Name.split(" ")

        # 去掉显存, 频率
        TokenList = GPUName.RemoveSpecialInfo(TokenList, "GB")
        TokenList = GPUName.RemoveSpecialInfo(TokenList, "MHZ")

        # 去掉Laptop标识
        BeforeLen = len(TokenList)
        TokenList = GPUName.RemoveInfo(TokenList, r"^MOBILE$|^LAPTOP$|^NOTEBOOK$")
        IsLaptop: bool = bool(BeforeLen - len(TokenList))
        if IsLaptop:
            self.Features.add("LAPTOP")

        # 去掉Max-Q标识
        BeforeLen = len(TokenList)
        TokenList = GPUName.RemoveInfo(TokenList, r"^MAX-?Q$")
        IsMAXQ: bool = bool(BeforeLen - len(TokenList))
        if IsMAXQ:
            self.Features.add("MAX-Q")
            self.Features.add("LAPTOP")
        
        # 辨别移动端MX标识以及后缀M
        Pattern_laptop = re.compile(r"\d+M$|MX|^\d+S$|^\d+T")
        for Token in TokenList:
            if Pattern_laptop.search(Token):
                self.Features.add("LAPTOP")

        # 去掉功耗
        TokenList = GPUName.RemoveInfo(TokenList, r"^\d+(\.\d+)?W$")
        # 去掉Desktop, Graphics, GA10x, GPU标识
        TokenList = GPUName.RemoveInfo(TokenList, r"^GRAPHICS$|^GA\d+$|^GPU$")
        BeforeLen = len(TokenList)
        TokenList = GPUName.RemoveInfo(TokenList, r"^DESKTOP$")
        IsDesktop: bool = bool(BeforeLen - len(TokenList))
        if IsDesktop and "LAPTOP" in self.Features:
            self.Features.remove("LAPTOP")
        # 去掉如 for 13th gen Processors/ 50th Anniversary 类型的标识
        TokenList = GPUName.RemoveInfo(
            TokenList, r"^FOR$|^\d+TH$|^GEN$|^PROCESSOR|^ANNIVERSARY$"
        )
                
        # 辨别专业卡型号
        Pattern_professional = re.compile(r"^T\d+|^A\d+00|^P\d+|^T\d+|^TITAN$")
        for Token in TokenList:
            if Pattern_professional.search(Token):
                self.Features.add("PROFESSIONAL")

        # 取得生产商, 并移除
        if len(TokenList) != 0:
            self.Vendor = TokenList[0]
            TokenList = GPUName.RemoveInfo(TokenList, self.Vendor)

        # 取得型号, 并移除
        self.Model = GPUName.GetModel(TokenList)
        if self.Model != "Unknown":
            TokenList = GPUName.RemoveInfo(TokenList, self.Model)

        # 剩下的 Token 全部视为 Feature
        self.Features.update(TokenList)

    def __hash__(self) -> int:
        if isinstance(self.Features, set):
            self.Features = frozenset(self.Features)
        return hash((self.Vendor, self.Model, self.Features))

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, self.__class__):
            return (
                self.Vendor == __value.Vendor
                and self.Model == __value.Model
                and self.Features == __value.Features
            )
        return False

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.Vendor}, {self.Model}, {self.Features})"
        )
