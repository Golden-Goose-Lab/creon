from re import sub as re_sub
from time import sleep

from pyautogui import typewrite, press
# from pywinauto import Application, timings
# from pywinauto.findwindows import find_window


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
