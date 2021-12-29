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
