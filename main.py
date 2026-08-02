<<<<<<< HEAD
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
=======
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
>>>>>>> 190c7c764260e047a6a47ffe88cfa11e49f29afc
    try:
        from ui_desktop import AppDesktop

        app = AppDesktop()
        app.mainloop()
<<<<<<< HEAD
    except Exception as e:
        # Caso falhar o desktop no PC, ele usa o Flet como plano B
        import flet as ft
        from ui_flet import main_flet

        ft.app(target=main_flet)
=======
    except Exception:
        import flet as ft
        from ui_flet import main_flet
        ft.app(target=main_flet)
>>>>>>> 190c7c764260e047a6a47ffe88cfa11e49f29afc
