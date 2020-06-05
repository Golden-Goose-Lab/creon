import os
from datetime import timedelta
from time import sleep

from pyautogui import typewrite, press
from pywinauto import Application, timings
from pywinauto.findwindows import find_window
from creon.constants import TimeFrameUnit


def run_creon_plus(username: str, password: str, certification_password: str, starter_path: str):
    app = Application().start('%s /prj:cp' % starter_path)
    sleep(1)
    typewrite('\n', interval=0.1)

    dialog = timings.WaitUntilPasses(
        30, 1, lambda: app.window(handle=find_window(title='CREON Starter'))
    )
    username_input = getattr(dialog, '1')
    username_input.Click()
    username_input.TypeKeys(username)
    password_input = getattr(dialog, '2')
    password_input.Click()
    password_input.TypeKeys(password)
    certification_password_input = getattr(dialog, '3')
    certification_password_input.Click()
    certification_password_input.TypeKeys(certification_password)
    press('enter')


def snake_to_camel(value: str) -> str:
    return ''.join(x.capitalize() or '_' for x in value.split('_'))


def timeframe_to_timedelta(timeframe: tuple) -> timedelta:
    amount, unit = timeframe
    if unit in (TimeFrameUnit.MONTH, TimeFrameUnit.TICK):
        raise ValueError("Cannot convert month or tick to timedelta")
    elif unit == TimeFrameUnit.WEEK:
        time_delta = timedelta(weeks=1)
    elif unit == TimeFrameUnit.DAY:
        time_delta = timedelta(days=amount)
    elif unit == TimeFrameUnit.MINUTE:
        time_delta = timedelta(minutes=amount)
    else:
        raise ValueError('timeframe unit {} is not supported'.format(unit))

    return time_delta


def is_validate_path(path: str) -> bool:
    return os.path.exists(path) and os.access(path, os.W_OK)
