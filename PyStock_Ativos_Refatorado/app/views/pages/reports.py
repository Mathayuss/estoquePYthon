import customtkinter as ctk
from tkinter import messagebox
from app.controllers import ReportController

class ReportsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        ctk.CTkLabel(self, text="Relatórios (Excel)", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 10))

        box = ctk.CTkFrame(self, corner_radius=14)
        box.pack(fill="x", pady=(0, 12))

        ctk.CTkButton(box, text="Exportar Ativos (XLSX)", command=self.export_assets).pack(side="left", padx=12, pady=12)
        ctk.CTkButton(box, text="Exportar Produtos/Modelos (XLSX)", command=self.export_products).pack(side="left", padx=12, pady=12)
        ctk.CTkButton(box, text="Exportar Movimentações (XLSX)", command=self.export_movs).pack(side="left", padx=12, pady=12)

        self.out = ctk.CTkTextbox(self, height=260)
        self.out.pack(fill="both", expand=True)

        self._log("Os arquivos são gerados automaticamente em: exports/")

    def _log(self, msg: str):
        self.out.insert("end", msg + "\n")
        self.out.see("end")

    def refresh(self):
        pass

    def export_assets(self):
        try:
            path = ReportController.export_assets_xlsx()
            self._log(f"Ativos exportados: {path}")
            messagebox.showinfo("Relatórios", "Exportação concluída.")
        except Exception as e:
            messagebox.showerror("Relatórios", str(e))

    def export_products(self):
        try:
            path = ReportController.export_products_xlsx()
            self._log(f"Produtos exportados: {path}")
            messagebox.showinfo("Relatórios", "Exportação concluída.")
        except Exception as e:
            messagebox.showerror("Relatórios", str(e))

    def export_movs(self):
        try:
            path = ReportController.export_movements_xlsx()
            self._log(f"Movimentações exportadas: {path}")
            messagebox.showinfo("Relatórios", "Exportação concluída.")
        except Exception as e:
            messagebox.showerror("Relatórios", str(e))
