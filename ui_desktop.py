# ui_desktop.py
import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog, filedialog
import os
from core.calculos import calcular_revisao_contrato
from core.gerador_pdf import exportar_pdf

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AppDesktop(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Pericial Revisional - Desktop Pro")
        self.geometry("1150x800")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        self.valores_pagos_custom = {}
        self.logo_path = ""
        self.resumo_atual = None
        self.memoria_atual = None

        self.criar_painel_esquerdo()
        self.criar_painel_direito()

    def criar_painel_esquerdo(self):
        f = ctk.CTkFrame(self)
        f.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        ctk.CTkLabel(f, text="PARÂMETROS", font=("Segoe UI", 16, "bold")).pack(pady=10)

        self.ent_valor = self.add_field(f, "Valor Financiado Bruto (R$):", "50000")
        self.ent_tarifas = self.add_field(f, "Tarifas/Seguros Indevidos (R$):", "2000")
        self.ent_prazo = self.add_field(f, "Prazo (Nº Parcelas):", "12")
        self.ent_taxa_banco = self.add_field(f, "Taxa do Banco (% a.m.):", "2.5")
        self.ent_taxa_bacen = self.add_field(f, "Taxa BACEN Ref (% a.m.):", "1.35")

        ctk.CTkLabel(f, text="Sistema de Amortização:").pack(anchor="w", padx=15)
        self.opt_sistema = ctk.CTkOptionMenu(f, values=["PRICE", "SAC"])
        self.opt_sistema.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(f, text="PERSONALIZAÇÃO LAUDO", font=("Segoe UI", 11, "bold"), text_color="#3498DB").pack(pady=5)

        self.btn_logo = ctk.CTkButton(f, text="📷 Selecionar Logo", command=self.selecionar_logo, fg_color="#34495E")
        self.btn_logo.pack(fill="x", padx=15, pady=3)

        self.lbl_logo_status = ctk.CTkLabel(f, text="Sem logo", font=("Segoe UI", 9), text_color="gray")
        self.lbl_logo_status.pack()

        self.ent_rodape = self.add_field(f, "Rodapé do PDF:", "Advocacia Rocha | OAB 12.345")

        ctk.CTkButton(f, text="CALCULAR REVISÃO", fg_color="#27AE60", height=38, command=self.executar_calculo).pack(
            fill="x", padx=15, pady=10)
        ctk.CTkButton(f, text="EDITAR PARCELA", fg_color="#D35400", command=self.editar_parcela).pack(fill="x", padx=15,
                                                                                                      pady=3)
        ctk.CTkButton(f, text="EXPORTAR PDF", fg_color="#2980B9", height=38, command=self.gerar_pdf).pack(fill="x",
                                                                                                          padx=15,
                                                                                                          pady=10)

    def add_field(self, parent, text, default_val):
        ctk.CTkLabel(parent, text=text, font=("Segoe UI", 10)).pack(anchor="w", padx=15)
        e = ctk.CTkEntry(parent)
        e.insert(0, default_val)
        e.pack(fill="x", padx=15, pady=(0, 4))
        return e

    def selecionar_logo(self):
        fp = filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg")])
        if fp:
            self.logo_path = fp
            self.lbl_logo_status.configure(text=os.path.basename(fp)[:15] + "...", text_color="#27AE60")

    def criar_painel_direito(self):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")
        f.grid_rowconfigure(1, weight=1)
        f.grid_columnconfigure(0, weight=1)

        fc = ctk.CTkFrame(f, fg_color="transparent")
        fc.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        fc.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_pago = self.criar_card(fc, 0, "TOTAL PAGO", "#C0392B")
        self.card_devido = self.criar_card(fc, 1, "TOTAL DEVIDO", "#27AE60")
        self.card_simples = self.criar_card(fc, 2, "RESTITUIÇÃO SIMPLES", "#2980B9")
        self.card_dobro = self.criar_card(fc, 3, "RESTITUIÇÃO DOBRO", "#8E44AD")

        ftbl = ctk.CTkFrame(f)
        ftbl.grid(row=1, column=0, sticky="nsew")
        ftbl.grid_rowconfigure(0, weight=1)
        ftbl.grid_columnconfigure(0, weight=1)

        cols = ("parc", "pago", "saldo_i", "juros", "amort", "prest", "saldo_f", "dif")
        self.tree = ttk.Treeview(ftbl, columns=cols, show="headings", selectmode="browse")
        headers = ["Nº", "Pago Real", "Saldo Inic.", "Juros", "Amortização", "Prest. Correta", "Saldo Final",
                   "Diferença"]

        for col, h in zip(cols, headers):
            self.tree.heading(col, text=h)
            self.tree.column(col, width=95, anchor="e" if col != "parc" else "center")

        sb = ttk.Scrollbar(ftbl, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")

    def criar_card(self, parent, col, title, color):
        c = ctk.CTkFrame(parent, border_width=1, border_color=color)
        c.grid(row=0, column=col, padx=4, sticky="ew")
        ctk.CTkLabel(c, text=title, font=("Segoe UI", 9, "bold"), text_color="gray").pack(pady=(6, 2))
        lbl = ctk.CTkLabel(c, text="R$ 0,00", font=("Segoe UI", 12, "bold"), text_color=color)
        lbl.pack(pady=(0, 6))
        return lbl

    def executar_calculo(self):
        try:
            val_bruto = float(self.ent_valor.get().replace(",", "."))
            tarifas = float(self.ent_tarifas.get().replace(",", "."))
            prazo = int(self.ent_prazo.get())
            taxa_banco = float(self.ent_taxa_banco.get().replace(",", ".")) / 100
            taxa_bacen = float(self.ent_taxa_bacen.get().replace(",", ".")) / 100
            sistema = self.opt_sistema.get()

            self.resumo_atual, self.memoria_atual = calcular_revisao_contrato(
                val_bruto, tarifas, prazo, taxa_banco, taxa_bacen, sistema, self.valores_pagos_custom
            )

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in self.memoria_atual:
                self.tree.insert("", "end", values=(
                    f"{row['parcela']}",
                    f"R$ {row['pago_real']:,.2f}",
                    f"R$ {row['saldo_inicial']:,.2f}",
                    f"R$ {row['juros']:,.2f}",
                    f"R$ {row['amortizacao']:,.2f}",
                    f"R$ {row['prestacao_correta']:,.2f}",
                    f"R$ {row['saldo_final']:,.2f}",
                    f"R$ {row['diferenca']:,.2f}"
                ))

            self.card_pago.configure(text=f"R$ {self.resumo_atual['tot_pago']:,.2f}")
            self.card_devido.configure(text=f"R$ {self.resumo_atual['tot_devido']:,.2f}")
            self.card_simples.configure(text=f"R$ {self.resumo_atual['tot_dif']:,.2f}")
            self.card_dobro.configure(text=f"R$ {self.resumo_atual['tot_dobro']:,.2f}")

        except Exception as e:
            messagebox.showerror("Erro", f"Entrada inválida: {str(e)}")

    def editar_parcela(self):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        num = int(vals[0])
        nv = simpledialog.askstring("Editar Parcela", f"Novo valor PAGO para parcela {num}:")
        if nv:
            self.valores_pagos_custom[num] = float(nv.replace(",", "."))
            self.executar_calculo()

    def gerar_pdf(self):
        if not self.resumo_atual:
            return
        fp = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if fp:
            params = {
                "val_bruto": float(self.ent_valor.get().replace(",", ".")),
                "tarifas": float(self.ent_tarifas.get().replace(",", ".")),
                "prazo": int(self.ent_prazo.get()),
                "taxa_banco": float(self.ent_taxa_banco.get().replace(",", ".")) / 100,
                "taxa_bacen": float(self.ent_taxa_bacen.get().replace(",", ".")) / 100,
                "sistema": self.opt_sistema.get()
            }
            exportar_pdf(fp, params, self.resumo_atual, self.memoria_atual, self.logo_path, self.ent_rodape.get())
            messagebox.showinfo("Sucesso", "PDF Gerado com Sucesso!")