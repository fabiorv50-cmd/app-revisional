# main.py
import os
import sys

# Detecta se é Android/Mobile ou Desktop
IS_MOBILE = (
    "ANDROID_ARGUMENT" in os.environ 
    or "PYTHONOPTIMIZE" in os.environ 
    or "ANDROID_ROOT" in os.environ
)

if IS_MOBILE:
    # No Android, carrega DIRETO a interface Flet
    import flet as ft
    from ui_flet import main_flet
    ft.app(target=main_flet)
else:
    # No Windows/Desktop, carrega a interface CustomTkinter
    try:
        from ui_desktop import AppDesktop
        app = AppDesktop()
        app.mainloop()
    except Exception:
        import flet as ft
        from ui_flet import main_flet
        ft.app(target=main_flet)
