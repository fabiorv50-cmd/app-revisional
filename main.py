import os
import sys

# Detecta se está rodando dentro do aplicativo Android
IS_MOBILE = (
        "ANDROID_ARGUMENT" in os.environ
        or "PYTHONOPTIMIZE" in os.environ
        or "ANDROID_ROOT" in os.environ
)

if IS_MOBILE:
    # --- AMBIENTE ANDROID (CELULAR) ---
    import flet as ft
    from ui_flet import main_flet

    ft.app(target=main_flet)

else:
    # --- AMBIENTE DESKTOP (WINDOWS / PYCHARM) ---
    try:
        from ui_desktop import AppDesktop

        app = AppDesktop()
        app.mainloop()
    except Exception as e:
        # Caso falhar o desktop no PC, ele usa o Flet como plano B
        import flet as ft
        from ui_flet import main_flet

        ft.app(target=main_flet)