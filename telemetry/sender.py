import logging
from collections import deque, namedtuple

import requests
from threading import Thread, Event

from pydantic import BaseModel, Field

from telemetry.status import VentilationStatus, SystemStatus, StatusReport, Alert


class Telemetry(BaseModel):
    # WARNING: Do not try to rename these fields because these are the exact
    # names the server expects.
    DeviceType: str = Field("81's Ventilation Monitor")
    DeviceId: str = Field(...)
    DeviceIp: str = Field("1.1.1.1")  # TODO: Get IP of active interface
    ComPort: str = Field("N/A")
    P_PEAK: float = Field(...)
    P_PEAK_HighAlarm: str = Field("NORMAL")
    P_PEAK_LowAlarm: str = Field("NORMAL")
    V_TE: float = Field(...)
    V_TE_High_Alarm: str = Field("NORMAL")
    V_TE_MAND: float = Field(0)
    V_TE_MAND_LowAlarm: str = Field("NORMAL")
    V_TI: float = Field(...)
    V_TI_HighAlarm1: str = Field("NORMAL")
    V_TI_HighAlarm2: str = Field("NORMAL")
    f_TOT: float = Field(0)
    f_TOT_HighAlarm: str = Field("NORMAL")
    O2percent: float = Field(...)
    O2percent_HighAlarm: str = Field("NORMAL")
    O2percent_LowAlarm: str = Field("NORMAL")
    I_ratio_E: str = Field("")
    PEEP: float = Field(...)
    ETCO2: str = Field("")
    P_MEAN: float = Field(0)
    P_I_END: float = Field(0)
    V_E_SPONT: float = Field(0)
    T_I_to_T_TOT: float = Field(0)
    f_to_V_T: float = Field(0)
    MandatoryType: str = Field("")
    Timestamp: int = Field(...)
    Sender: float = Field(0)


def get_device_id():
    import re
    import uuid
    # getnode returns the MAC address as a 48 bit integer. This line converts
    # it to a string in the well-known format AA:BB:CC:DD:EE:FF
    return ':'.join(re.findall('..', '%012x' % uuid.getnode()))


# Holds the data queued for sending. We don't construct the final `StatusReport`
# on queuing, because that might be time consuming and we want the queueing
# operation to be as fast as possible.
QueueItem = namedtuple(
    "QueueItem", ("ventilation_status", "system_alerts", "battery_percentage"))


class TelemetrySender(Thread):

    HEADERS = {
        'Content-Type': 'application/json',
    }

    def __init__(self, enable, url, api_key=None):
        super().__init__()
        self.daemon = True
        self.enable = enable
        self.url = url
        self.device_id = get_device_id()
        self.timeout = 5
        self.log = logging.getLogger(self.__class__.__name__)
        # If more than 5 telemetries are queued - throw the oldest
        self.queue = deque(maxlen=5)
        self.event = Event()
        if api_key is not None:
            self.HEADERS["x-api-key"] = api_key

    def run(self):
        if not self.enable:
            self.log.info("Telemetry disabled. Exiting")
            return

        while True:
            self.event.wait()
            # noinspection PyBroadException
            try:
                self._flush_queue()
            except Exception:
                self.log.exception("Unhandled exception while flushing queue")
            self.event.clear()

    def _flush_queue(self):
        while len(self.queue):
            item = self.queue.popleft()
            self._send(item)

    def enqueue(self, timestamp, inspiration_volume, expiration_volume,
                avg_inspiration_volume, avg_expiration_volume, peak_flow,
                peak_pressure, min_pressure, bpm, o2_saturation_percentage,
                current_state, alerts, battery_percentage):
        # The current implementation does not keep system alerts and
        # ventilation alerts separate, but it does make more sense to separate
        # the two.
        system_alerts = [Alert.from_app_alert(a)
                         for a in alerts if a.is_system_alert()]
        medical_alerts = [Alert.from_app_alert(a)
                          for a in alerts if a.is_medical_condition()]
        ventilation_status = VentilationStatus(
            timestamp=timestamp,
            inspiration_volume=inspiration_volume,
            expiration_volume=expiration_volume,
            avg_inspiration_volume=avg_inspiration_volume,
            avg_expiration_volume=avg_expiration_volume,
            peak_flow=peak_flow,
            peak_pressure=peak_pressure,
            min_pressure=min_pressure,
            bpm=bpm,
            o2_saturation_percentage=o2_saturation_percentage,
            current_state=current_state,
            alerts=medical_alerts
        )

        item = QueueItem(ventilation_status, system_alerts, battery_percentage)
        self.queue.append(item)  # `deque.append` is atomic
        self.event.set()
        self.log.debug("Telemetry enqueued: %s", item)

    @staticmethod
    def build(item: QueueItem):
        # Creating the SystemStatus instance is pretty time-consuming operation
        # because there are a lot of psutil stuff going on.
        # It is deferred to here, which happens on the Sender thread.
        system_status = SystemStatus(
            battery_percentage=item.battery_percentage,
            alerts=item.system_alerts)

        report = StatusReport(
            system_status=system_status,
            ventilation_status=item.ventilation_status
        )
        return report

    def _send(self, item: QueueItem):
        telemetry = self.build(item)
        self.log.debug("Sending telemetry: %s", telemetry)
        try:
            resp = requests.put(
                self.url, headers=self.HEADERS, data=telemetry.json(),
                timeout=self.timeout)
        except Exception as e:
            self.log.error("Failed to send telemetry: %s", e)
            return

        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            self.log.debug("Error Response: %s - %s", e, resp.text)
            return

        self.log.debug("Telemetry sent")
