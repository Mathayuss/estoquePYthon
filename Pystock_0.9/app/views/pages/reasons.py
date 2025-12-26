import customtkinter as ctk
from tkinter import ttk, messagebox
from app.controllers import ExitReasonController

class ReasonsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        top = ctk.CTkFrame(self, corner_radius=12)
        top.pack(fill="x", pady=(0, 10))

        self.name = ctk.CTkEntry(top, placeholder_text="Novo motivo de saída (ex: Entrega, Manutenção, Baixa...)")
        self.name.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        ctk.CTkButton(top, text="Adicionar", command=self.add).pack(side="left", padx=6, pady=10)
        ctk.CTkButton(top, text="Ativar/Desativar", command=self.toggle).pack(side="left", padx=6, pady=10)
        ctk.CTkButton(top, text="Excluir", fg_color="#b91c1c", hover_color="#991b1b", command=self.delete).pack(side="left", padx=6, pady=10)

        self.table = ttk.Treeview(self, columns=("id","name","active"), show="headings", height=18)
        self.table.heading("id", text="ID")
        self.table.heading("name", text="Motivo")
        self.table.heading("active", text="Ativo")
        self.table.column("id", width=70, anchor="center")
        self.table.column("name", width=520, anchor="w")
        self.table.column("active", width=90, anchor="center")
        self.table.pack(fill="both", expand=True)

    def refresh(self):
        for i in self.table.get_children():
            self.table.delete(i)
        for r in ExitReasonController.list_reasons(active_only=False):
            self.table.insert("", "end", values=(r["id"], r["name"], "Sim" if int(r["is_active"])==1 else "Não"))

    def _selected(self):
        sel = self.table.selection()
        if not sel:
            return None
        vals = self.table.item(sel[0], "values")
        return int(vals[0]), vals[1], vals[2]

    def add(self):
        try:
            ExitReasonController.create_reason(self.name.get())
            self.name.delete(0, "end")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Motivos", str(e))

    def toggle(self):
        sel = self._selected()
        if not sel:
            messagebox.showwarning("Motivos", "Selecione um motivo.")
            return
        rid, name, active = sel
        try:
            new_active = 0 if active == "Sim" else 1
            ExitReasonController.update_reason(rid, name, new_active)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Motivos", str(e))

    def delete(self):
        sel = self._selected()
        if not sel:
            messagebox.showwarning("Motivos", "Selecione um motivo.")
            return
        rid, _, _ = sel
        if not messagebox.askyesno("Motivos", "Excluir motivo?"):
            return
        try:
            ExitReasonController.delete_reason(rid)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Motivos", str(e))
