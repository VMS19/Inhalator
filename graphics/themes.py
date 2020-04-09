class Theme(object):
    ACTIVE_THEME = None

    BACKGROUND = NotImplemented
    SURFACE = NotImplemented
    ERROR = NotImplemented
    ERROR_ACTIVE = NotImplemented

    BUTTON = NotImplemented
    BUTTON_TEXT = NotImplemented
    BUTTON_ACTIVE = NotImplemented
    BUTTON_ACTIVE_TEXT = NotImplemented

    OK = NotImplemented
    OK_ACTIVE = NotImplemented

    TXT_ON_SURFACE = NotImplemented
    TXT_ON_BG = NotImplemented
    TXT_ON_OK = NotImplemented
    TXT_ON_ERROR = NotImplemented

    ALERT_BAR_OK = NotImplemented
    ALERT_BAR_OK_TXT = NotImplemented

    RIGHT_SIDE_BUTTON_BG = NotImplemented
    RIGHT_SIDE_BUTTON_FG = NotImplemented
    RIGHT_SIDE_BUTTON_BG_ACTIVE = NotImplemented
    RIGHT_SIDE_BUTTON_FG_ACTIVE = NotImplemented

    REFRESH_BUTTON_ACTIVE_BG = NotImplemented
    REFRESH_BUTTON_ACTIVE_TEXT = NotImplemented

    UNSEEN_ALERT = NotImplemented
    TXT_ON_UNSEEN_ALERT = NotImplemented

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

    @classmethod
    def choose_theme(cls, theme='Dark'):
        if theme == "Dark":
            cls.ACTIVE_THEME = DarkTheme()

        elif theme == "light":
            cls.ACTIVE_THEME = LightTheme()

        else:
            raise TypeError(f"Theme {theme} doesn't  exists")


class LightTheme(Theme):
    def __init__(self):
        import matplotlib.pyplot as plt
        plt.style.use('classic')

    DARK_BLUE = "#011627"
    WHITE = "#fdfffc"
    LIGHT_BLUE = "#2ec4b6"
    RED = "#e71d36"
    YELLOW = "#ff9f1c"


class DarkTheme(Theme):
    def __init__(self):
        import matplotlib.pyplot as plt
        plt.style.use('dark_background')

    DARK_BLUE = "#011627"
    WHITE = "#fdfffc"
    LIGHT_BLUE = "#2ec4b6"
    RED = "#e71d36"
    YELLOW = "#ff9f1c"

    BACKGROUND = "#191919"
    SURFACE = "#232323"
    ERROR = "#b00020"
    ERROR_ACTIVE = "#cf6679"

    BUTTON = "#52475d"
    BUTTON_TEXT = "#f7f6f7"
    BUTTON_ACTIVE = "#52475d"
    BUTTON_ACTIVE_TEXT = "#f7f6f7"

    OK = "#4CAF50"
    OK_ACTIVE = "#66BB6A"

    TXT_ON_SURFACE = "#ffffff"
    TXT_ON_BG = "#ffffff"
    TXT_ON_OK = "#000000"
    TXT_ON_ERROR = "#ffffff"

    ALERT_BAR_OK = "#33691E"
    ALERT_BAR_OK_TXT = "#ffffff"

    RIGHT_SIDE_BUTTON_BG = "#3c3149"
    RIGHT_SIDE_BUTTON_FG = "#fdfffc"
    RIGHT_SIDE_BUTTON_BG_ACTIVE = "#d7b1f9"
    RIGHT_SIDE_BUTTON_FG_ACTIVE = "#3c3149"

    REFRESH_BUTTON_ACTIVE_BG = "#b787f7"
    REFRESH_BUTTON_ACTIVE_TEXT = "#1f1825"

    UNSEEN_ALERT = "#d36578"
    TXT_ON_UNSEEN_ALERT = "#201516"
