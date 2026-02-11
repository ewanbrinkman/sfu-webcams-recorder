from enum import StrEnum, auto


class CameraID(StrEnum):
    AQN = auto()
    AQSW = auto()
    AQSE = auto()
    GAGLARDI = auto()
    TOWERN = auto()
    TOWERS = auto()
    UDN = auto()
    WMCROOF = auto()
    BRH = auto()


CAMERA_URLS: dict[CameraID, str] = {
    CameraID.AQN: "https://ns-webcams.its.sfu.ca/public/images/aqn-current.jpg",
    CameraID.AQSW: "https://ns-webcams.its.sfu.ca/public/images/aqsw-current.jpg",
    CameraID.AQSE: "https://ns-webcams.its.sfu.ca/public/images/aqse-current.jpg",
    CameraID.GAGLARDI: "https://ns-webcams.its.sfu.ca/public/images/gaglardi-current.jpg",
    CameraID.TOWERN: "https://ns-webcams.its.sfu.ca/public/images/towern-current.jpg",
    CameraID.TOWERS: "https://ns-webcams.its.sfu.ca/public/images/towers-current.jpg",
    CameraID.UDN: "https://ns-webcams.its.sfu.ca/public/images/udn-current.jpg",
    CameraID.WMCROOF: "https://ns-webcams.its.sfu.ca/public/images/wmcroof-current.jpg",
    CameraID.BRH: "https://ns-webcams.its.sfu.ca/public/images/brh-current.jpg",
}
