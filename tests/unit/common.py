from data import alerts

ALERT_DICT = {
        alerts.AlertCodes.PRESSURE_LOW: "Low Pressure",
        alerts.AlertCodes.PRESSURE_HIGH: "High Pressure",
        alerts.AlertCodes.VOLUME_LOW: "Low Volume",
        alerts.AlertCodes.VOLUME_HIGH: "High Volume",
        alerts.AlertCodes.NO_BREATH: "No Breathing",
        alerts.AlertCodes.NO_CONFIGURATION_FILE: "Cannot Read Configuration"
    }
