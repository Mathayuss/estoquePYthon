import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from app.controllers import AssetController, AssetMovementController, ExitReasonController

class SaidaPage(ctk.CTkFrame):
    def __init__(self, master, current_user: dict):
        super().__init__(master)
        self.current_user = current_user
        self.reasons: list[dict] = []

        ctk.CTkLabel(self, text="Saída (Entrega/Retirada)", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 10))

        box = ctk.CTkFrame(self, corner_radius=14)
        box.pack(fill="x", pady=(0, 12))

        self.ent_id = ctk.CTkEntry(box, width=360, placeholder_text="Escaneie o QR do ativo OU digite o patrimônio e pressione Enter")
        self.ent_id.pack(side="left", padx=12, pady=12)
        self.ent_id.bind("<Return>", lambda _e: self._process())

        self.var_reason = ctk.StringVar(value="")
        self.cbo_reason = ctk.CTkOptionMenu(box, variable=self.var_reason, values=["Carregando..."])
        self.cbo_reason.pack(side="left", padx=8, pady=12)

        self.notes = ctk.CTkEntry(box, placeholder_text="Observações (opcional)")
        self.notes.pack(side="left", fill="x", expand=True, padx=8, pady=12)
        self.notes.bind("<Return>", lambda _e: self._process())

        ctk.CTkButton(box, text="Registrar Saída", command=self._process).pack(side="left", padx=(0, 12), pady=12)

        tip = "Dica: você pode usar QR ou digitar o patrimônio."
        ctk.CTkLabel(self, text=tip, text_color="#6b7280").pack(anchor="w")

        self._load_reasons()

    def _load_reasons(self):
        self.reasons = ExitReasonController.list_active()
        if not self.reasons:
            self.cbo_reason.configure(values=["(Cadastre motivos)"])
            self.var_reason.set("(Cadastre motivos)")
            return

        names = [r["name"] for r in self.reasons]
        self.cbo_reason.configure(values=names)
        self.var_reason.set(names[0])

    def _selected_reason_id(self) -> int | None:
        name = (self.var_reason.get() or "").strip()
        for r in self.reasons:
            if r["name"] == name:
                return int(r["id"])
        return None

    def _process(self):
        try:
            ident = (self.ent_id.get() or "").strip()
            if not ident:
                raise ValueError("Informe o QR (scan) ou o patrimônio.")

            reason_id = self._selected_reason_id()
            if not reason_id:
                raise ValueError("Selecione um motivo de saída válido.")

            asset = AssetController.get_by_identifier(ident)
            if not asset:
                raise ValueError("Ativo não encontrado (QR ou patrimônio inválido).")

            AssetMovementController.register_out(
                asset_id=asset["id"],
                user_id=self.current_user["id"],
                reason_id=reason_id,
                notes=self.notes.get().strip() or None,
                occurred_at=datetime.utcnow()
            )

            self.ent_id.delete(0, "end")
            self.notes.delete(0, "end")

            messagebox.showinfo("Saída", f"Saída registrada: {asset['asset_tag']} ({asset.get('product','')})")
        except Exception as e:
            messagebox.showerror("Saída", str(e))
