import os
import sys

# Detecta se está rodando no Android
IS_MOBILE = (
        "ANDROID_ARGUMENT" in os.environ
        or "PYTHONOPTIMIZE" in os.environ
        or "ANDROID_ROOT" in os.environ
)

if IS_MOBILE:
    # Interface Flet para o celular
    import flet as ft
    from ui_flet import main_flet

    ft.app(target=main_flet)

else:
    # Interface CustomTkinter para o PC (Windows)
    try:
        from ui_desktop import AppDesktop

        app = AppDesktop()
        app.mainloop()
    except Exception:
        import flet as ft
        from ui_flet import main_flet

        ft.app(target=main_flet)