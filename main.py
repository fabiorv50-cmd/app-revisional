# main.py
import sys

# Escolha o modo de execução: "desktop" ou "flet"
MODO_EXECUCAO = "desktop"

if __name__ == "__main__":
    if MODO_EXECUCAO == "desktop":
        from ui_desktop import AppDesktop
        app = AppDesktop()
        app.mainloop()
    else:
        import flet as ft
        from ui_flet import main_flet
        ft.app(target=main_flet)