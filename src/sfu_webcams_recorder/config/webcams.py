from enum import StrEnum, auto


class WebcamID(StrEnum):
    AQN = auto()
    AQSW = auto()
    AQSE = auto()
    GAGLARDI = auto()
    TOWERN = auto()
    TOWERS = auto()
    UDN = auto()
    WMCROOF = auto()
    BRH = auto()


WEBCAM_URLS: dict[WebcamID, str] = {
    WebcamID.AQN: "https://ns-webcams.its.sfu.ca/public/images/aqn-current.jpg",
    WebcamID.AQSW: "https://ns-webcams.its.sfu.ca/public/images/aqsw-current.jpg",
    WebcamID.AQSE: "https://ns-webcams.its.sfu.ca/public/images/aqse-current.jpg",
    WebcamID.GAGLARDI: "https://ns-webcams.its.sfu.ca/public/images/gaglardi-current.jpg",
    WebcamID.TOWERN: "https://ns-webcams.its.sfu.ca/public/images/towern-current.jpg",
    WebcamID.TOWERS: "https://ns-webcams.its.sfu.ca/public/images/towers-current.jpg",
    WebcamID.UDN: "https://ns-webcams.its.sfu.ca/public/images/udn-current.jpg",
    WebcamID.WMCROOF: "https://ns-webcams.its.sfu.ca/public/images/wmcroof-current.jpg",
    WebcamID.BRH: "https://ns-webcams.its.sfu.ca/public/images/brh-current.jpg",
}
