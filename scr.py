from calendar import c
from dataclasses import asdict, dataclass
from time import sleep
from typing import Dict, List

import numpy as np
from pyvisa.resources import TCPIPInstrument


@dataclass
class SampleParameters():

    name: str


@dataclass
class PulseParameters():

    amplitude: float
    pulsewidth: float
    risetime: float
    falltime: float


class WaveForm():

    maxVal: int = 2**16  # Maximum value storable in an INT16
    channels: List = []
    rawData: Dict = {}
    format: Dict = {}  # This should be 1, since we"re specifying INT16 output
    type: Dict = {}
    points: Dict = {}
    count: Dict = {}
    xIncrement: Dict = {}  # in seconds
    xOrigin: Dict = {}  # in seconds
    xReference: Dict = {}
    yIncrement: Dict = {}  # V
    yOrigin: Dict = {}
    yReference: Dict = {}

    def voltsPerDiv(self, channelID: int):
        return (self.maxVal * self.yIncrement[channelID] / 8)  # V

    def offset(self, channelID: int):
        # V
        return (self.maxVal / 2 - self.yReference[channelID]) * \
            self.yIncrement[channelID] + self.yOrigin[channelID]

    def secPerDiv(self, channelID: int):
        # seconds
        return self.points[channelID] * self.xIncrement[channelID] / 10

    def delay(self, channelID: int):
        # seconds
        return (self.points[channelID] / 2 - self.xReference[channelID]) * \
            self.xIncrement[channelID] + self.xOrigin[channelID]

    def addChannel(self, channelID: int, preambleBlock: List, rawData: bytes):
        self.rawData[channelID] = rawData
        self.format[channelID] = float(preambleBlock[0])
        self.type[channelID] = float(preambleBlock[1])
        self.points[channelID] = float(preambleBlock[2])
        self.count[channelID] = int(preambleBlock[3])
        self.xIncrement[channelID] = float(preambleBlock[4])
        self.xOrigin[channelID] = float(preambleBlock[5])
        self.xReference[channelID] = float(preambleBlock[6])
        self.yIncrement[channelID] = float(preambleBlock[7])
        self.yOrigin[channelID] = float(preambleBlock[8])
        self.yReference[channelID] = float(preambleBlock[9])
        self.channels.append(channelID)

    def time(self, channelID: int):
        return self.xIncrement[channelID] * \
            np.arange(len(self.rawData[channelID]))

    def ch(self, channelID: int):
        return self.yIncrement[channelID] * \
            (np.array(self.rawData[channelID]) -
                self.yReference[channelID]) + self.yOrigin[channelID]

    def asdict(self):
        out = dict(maxVal=self.maxVal, channels=self.channels)
        for i in self.channels:
            out[f"rawData{i}"] = self.rawData[i]
            out[f"format{i}"] = self.format[i]
            out[f"type{i}"] = self.type[i]
            out[f"points{i}"] = self.points[i]
            out[f"count{i}"] = self.count[i]
            out[f"xIncrement{i}"] = self.xIncrement[i]
            out[f"xOrigin{i}"] = self.xOrigin[i]
            out[f"xReference{i}"] = self.xReference[i]
            out[f"yIncrement{i}"] = self.yIncrement[i]
            out[f"yOrigin{i}"] = self.yOrigin[i]
            out[f"yReference{i}"] = self.yReference[i]
            out[f"time{i}"] = self.time(i)
            out[f"ch{i}"] = self.ch(i)
        return out


