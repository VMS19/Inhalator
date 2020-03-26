class Theme(object):
    ACTIVE_THEME = None

    BACKGROUND = NotImplemented
    SURFACE = NotImplemented

    TXT_ON_BG = NotImplemented
    TXT_ON_SURFACE = NotImplemented
    TXT_ON_PRIMARY = NotImplemented
    TXT_ON_SECONDARY = NotImplemented

    OK = NotImplemented
    TXT_ON_OK = NotImplemented
    ERROR = NotImplemented
    TXT_ON_ERROR = NotImplemented

    @classmethod
    def active(cls):
        # This is an abstract Java Factory reduced to a static
        # method because Python
        if cls.ACTIVE_THEME is None:
            return LightTheme()

        return cls.ACTIVE_THEME

    @classmethod
    def toggle_theme(cls):
        if isinstance(cls.active(), LightTheme):
            cls.ACTIVE_THEME = DarkTheme()

        else:
            cls.ACTIVE_THEME = LightTheme()


class LightTheme(Theme):
    def __init__(self):
        import matplotlib.pyplot as plt
        plt.style.use('classic')

class DarkTheme(Theme):
    def __init__(self):
        import matplotlib.pyplot as plt
        plt.style.use('dark_background')

    BACKGROUND = "#191919"
    SURFACE = "#232323"
    ERROR = "#b00020"

    OK = "#4CAF50"
    OK_ACTIVE = "#66BB6A"

    TXT_ON_SURFACE = "#ffffff"
    TXT_ON_BG = "#ffffff"
    TXT_ON_OK = "#000000"
    TXT_ON_ERROR = "#ffffff"

    PRIMARY_VARIANT = "#3700B3"
