import customtkinter as ctk
from app.database import init_db, seed_admin_if_needed
from app.views.app_shell import AppShell

def main():
    init_db()
    seed_admin_if_needed()

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = AppShell()
    app.mainloop()

if __name__ == "__main__":
    main()
