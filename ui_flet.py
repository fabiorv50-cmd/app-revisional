# ui_flet.py
import flet as ft
from core.calculos import calcular_revisao_contrato


def main_flet(page: ft.Page):
    page.title = "Sistema Revisional (Flet/Mobile)"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 15

    valores_pagos_custom = {}
    dados = {"resumo": None, "memoria": None}

    txt_valor = ft.TextField(label="Valor Financiado Bruto (R$)", value="50000")
    txt_tarifas = ft.TextField(label="Tarifas/Seguros (R$)", value="2000")
    txt_prazo = ft.TextField(label="Prazo (Parcelas)", value="12")
    txt_taxa_banco = ft.TextField(label="Taxa Banco (% a.m.)", value="2.5")
    txt_taxa_bacen = ft.TextField(label="Taxa BACEN (% a.m.)", value="1.35")
    dd_sistema = ft.Dropdown(label="Sistema", value="PRICE", options=[ft.dropdown.Option("PRICE"), ft.dropdown.Option("SAC")])
    txt_rodape = ft.TextField(label="Rodapé PDF", value="Advocacia Rocha | OAB 12.345")

    lbl_pago = ft.Text("R$ 0,00", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)
    lbl_devido = ft.Text("R$ 0,00", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
    lbl_simples = ft.Text("R$ 0,00", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
    lbl_dobro = ft.Text("R$ 0,00", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_400)

    dt_memoria = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nº")),
            ft.DataColumn(ft.Text("Pago Real")),
            ft.DataColumn(ft.Text("Saldo Inic.")),
            ft.DataColumn(ft.Text("Juros")),
            ft.DataColumn(ft.Text("Amortização")),
            ft.DataColumn(ft.Text("Prest. Correta")),
            ft.DataColumn(ft.Text("Saldo Final")),
            ft.DataColumn(ft.Text("Diferença")),
        ],
        rows=[]
    )

    def calcular(e):
        try:
            v_bruto = float(txt_valor.value.replace(",", "."))
            tar = float(txt_tarifas.value.replace(",", "."))
            prz = int(txt_prazo.value)
            tx_b = float(txt_taxa_banco.value.replace(",", ".")) / 100
            tx_bac = float(txt_taxa_bacen.value.replace(",", ".")) / 100
            sist = dd_sistema.value

            dados["resumo"], dados["memoria"] = calcular_revisao_contrato(
                v_bruto, tar, prz, tx_b, tx_bac, sist, valores_pagos_custom
            )

            dt_memoria.rows.clear()
            for row in dados["memoria"]:
                dt_memoria.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(row["parcela"]))),
                        ft.DataCell(ft.Text(f"R$ {row['pago_real']:,.2f}")),
                        ft.DataCell(ft.Text(f"R$ {row['saldo_inicial']:,.2f}")),
                        ft.DataCell(ft.Text(f"R$ {row['juros']:,.2f}")),
                        ft.DataCell(ft.Text(f"R$ {row['amortizacao']:,.2f}")),
                        ft.DataCell(ft.Text(f"R$ {row['prestacao_correta']:,.2f}")),
                        ft.DataCell(ft.Text(f"R$ {row['saldo_final']:,.2f}")),
                        ft.DataCell(ft.Text(f"R$ {row['diferenca']:,.2f}")),
                    ])
                )

            lbl_pago.value = f"R$ {dados['resumo']['tot_pago']:,.2f}"
            lbl_devido.value = f"R$ {dados['resumo']['tot_devido']:,.2f}"
            lbl_simples.value = f"R$ {dados['resumo']['tot_dif']:,.2f}"
            lbl_dobro.value = f"R$ {dados['resumo']['tot_dobro']:,.2f}"

            page.update()
        except Exception:
            page.snack_bar = ft.SnackBar(ft.Text("Erro nos dados de entrada!"), open=True)
            page.update()

    grid_cards = ft.ResponsiveRow([
        ft.Container(ft.Column([ft.Text("TOTAL PAGO", size=9), lbl_pago]), col={"sm": 6, "md": 3}, border=ft.Border.all(1, ft.Colors.RED_400), padding=8, border_radius=8),
        ft.Container(ft.Column([ft.Text("TOTAL DEVIDO", size=9), lbl_devido]), col={"sm": 6, "md": 3}, border=ft.Border.all(1, ft.Colors.GREEN_400), padding=8, border_radius=8),
        ft.Container(ft.Column([ft.Text("REST. SIMPLES", size=9), lbl_simples]), col={"sm": 6, "md": 3}, border=ft.Border.all(1, ft.Colors.BLUE_400), padding=8, border_radius=8),
        ft.Container(ft.Column([ft.Text("REST. DOBRO", size=9), lbl_dobro]), col={"sm": 6, "md": 3}, border=ft.Border.all(1, ft.Colors.PURPLE_400), padding=8, border_radius=8),
    ])

    page.add(
        ft.Text("SISTEMA REVISIONAL PERICIAL", size=18, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        txt_valor, txt_tarifas, txt_prazo, txt_taxa_banco, txt_taxa_bacen, dd_sistema, txt_rodape,
        ft.ElevatedButton("CALCULAR REVISÃO", on_click=calcular, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE, height=42),
        ft.Divider(),
        grid_cards,
        ft.Divider(),
        ft.Row([dt_memoria], scroll=ft.ScrollMode.ALWAYS)
    )

if __name__ == "__main__":
    ft.app(target=main_flet)