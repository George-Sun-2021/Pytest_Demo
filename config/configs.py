"""
You'll probably want to customize this to your own environment and needs.

For changes to take effect immediately, use Python's Develop Mode.
Develop Mode Install: "pip install -e ."  (from the top-level directory)
"""

# #####>>>>>----- REQUIRED/IMPORTANT SETTINGS -----<<<<<#####

# Default maximum time (in seconds) to wait for page elements to appear.
# Different methods/actions in base_case.py use different timeouts.
# If the element to be acted on does not appear in time, the test fails.
MINI_TIMEOUT = 2
SMALL_TIMEOUT = 6
LARGE_TIMEOUT = 10
EXTREME_TIMEOUT = 30
POLL_FREQUENCY = 0.5
PAGE_REFRESH_TIMEOUT = 30
PAGE_LOAD_TIMEOUT = 60

# Default browser resolutions when opening new windows for tests.
# (Headless resolutions take priority, and include all browsers.)
# (Firefox starts maximized by default when running in GUI Mode.)
CHROME_START_WIDTH = 1250
CHROME_START_HEIGHT = 840
HEADLESS_START_WIDTH = 1440
HEADLESS_START_HEIGHT = 1880

# basic type of the element locator
LOCATE_MODE = {
    'css': 'By.CSS_SELECTOR',
    'xpath': 'By.XPATH',
    'name': 'By.NAME',
    'id': 'By.ID',
    'class': 'By.CLASS_NAME',
}

# information for email
EMAIL_INFO = {
    'username': 'xxxxx@xxxx.com',  # 切换成你自己的地址
    'password': 'xxxxx',
    'smtp_host': 'smtp.xxxxx.com',
    'smtp_port': 465
}

# 收件人
ADDRESSEE = [
    'xxxxxxx@xxxxx.com',
]


class Environment:
    # Usage Example => "--env=qa" => Then access value in tests with "self.env"
    DEVLOCAL = "devLocal"
    DEVINT = "devInt"
    BVT_DTTL = "dttl"
    BVT_KPMG = "kpmg"
    BVT_BDO = "bdo"
    BVT_RSM = "rsm"


class ValidBrowsers:
    valid_browsers = [
        "chrome",
        "edge",
        "firefox",
        "ie",
        # "opera",
        # "phantomjs",
        # "safari",
        # "android",
        # "iphone",
        # "ipad",
        # "remote",
    ]


class Browser:
    GOOGLE_CHROME = "chrome"
    EDGE = "edge"
    FIREFOX = "firefox"
    INTERNET_EXPLORER = "ie"
    OPERA = "opera"
    PHANTOM_JS = "phantomjs"
    SAFARI = "safari"
    ANDROID = "android"
    IPHONE = "iphone"
    IPAD = "ipad"
    REMOTE = "remote"

    VERSION = {
        "chrome": None,
        "edge": None,
        "firefox": None,
        "ie": None,
        "opera": None,
        "phantomjs": None,
        "safari": None,
        "android": None,
        "iphone": None,
        "ipad": None,
        "remote": None,
    }

    LATEST = {
        "chrome": None,
        "edge": None,
        "firefox": None,
        "ie": None,
        "opera": None,
        "phantomjs": None,
        "safari": None,
        "android": None,
        "iphone": None,
        "ipad": None,
        "remote": None,
    }
