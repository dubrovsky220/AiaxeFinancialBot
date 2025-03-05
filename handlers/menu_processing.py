from keyboards.inline import get_main_menu_buttons


def get_main_page(*, session, level: int, menu_name: str):
    text = menu_name
    keyboard = get_main_menu_buttons(level=0)

    return text, keyboard
