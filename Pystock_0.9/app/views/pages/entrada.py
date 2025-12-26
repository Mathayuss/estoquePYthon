import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from app.controllers import AssetController, AssetMovementController

class EntradaPage(ctk.CTkFrame):
    def __init__(self, master, current_user: dict):
        super().__init__(master)
        self.current_user = current_user

        ctk.CTkLabel(self, text="Entrada (Retorno ao estoque)", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 10))

        box = ctk.CTkFrame(self, corner_radius=14)
        box.pack(fill="x", pady=(0, 12))

        self.ent_id = ctk.CTkEntry(box, width=360, placeholder_text="Escaneie o QR do ativo OU digite o patrimônio e pressione Enter")
        self.ent_id.pack(side="left", padx=12, pady=12)
        self.ent_id.bind("<Return>", lambda _e: self._process())

        self.notes = ctk.CTkEntry(box, placeholder_text="Observações (opcional)")
        self.notes.pack(side="left", fill="x", expand=True, padx=(0, 12), pady=12)
        self.notes.bind("<Return>", lambda _e: self._process())

        ctk.CTkButton(box, text="Registrar Entrada", command=self._process).pack(side="left", padx=(0, 12), pady=12)

        tip = "Dica: o leitor de QR geralmente envia ENTER automaticamente após o código."
        ctk.CTkLabel(self, text=tip, text_color="#6b7280").pack(anchor="w")

    def _process(self):
        try:
            ident = (self.ent_id.get() or "").strip()
            if not ident:
                raise ValueError("Informe o QR (scan) ou o patrimônio.")

            asset = AssetController.get_by_identifier(ident)
            if not asset:
                raise ValueError("Ativo não encontrado (QR ou patrimônio inválido).")

            AssetMovementController.register_in(
                asset_id=asset["id"],
                user_id=self.current_user["id"],
                notes=self.notes.get().strip() or None,
                occurred_at=datetime.utcnow()
            )

            self.ent_id.delete(0, "end")
            self.notes.delete(0, "end")

            messagebox.showinfo("Entrada", f"Entrada registrada: {asset['asset_tag']} ({asset.get('product','')})")
        except Exception as e:
            messagebox.showerror("Entrada", str(e))
