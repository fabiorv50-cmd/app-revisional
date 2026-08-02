# main.py
import sys
import os

# Verifica se está rodando em dispositivo móvel (Android/iOS)
IS_MOBILE = "ANDROID_ARGUMENT" in os.environ or "PYTHONOPTIMIZE" in os.environ

if __name__ == "__main__":
    if IS_MOBILE:
        # Execução no Celular (Android)
        import flet as ft
        from ui_flet import main_flet
        ft.app(target=main_flet)
    else:
        # Execução no Computador (Windows/Desktop)
        try:
            from ui_desktop import AppDesktop
            app = AppDesktop()
            app.mainloop()
        except ImportError:
            # Fallback para Flet caso o customtkinter não esteja instalado
            import flet as ft
            from ui_flet import main_flet
            ft.app(target=main_flet)
