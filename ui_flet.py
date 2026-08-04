import flet as ft
from core.calculos import calcular_revisao_contrato
from core.gerador_pdf import exportar_pdf


def main_flet(page: ft.Page):
    page.title = "Sistema Pericial Revisional"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 15

    # Estado da aplicação
    valores_pagos_custom = {}
    logo_path = {"caminho": ""}
    resumo_atual = {"dados": None}
    memoria_atual = {"dados": None}

    # --- 1. FILEPICKER (Sem adicionar no page.overlay para evitar 'Unknown control') ---
    def on_logo_selecionada(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            logo_path["caminho"] = e.files[0].path
            lbl_logo_status.value = f"Logo: {e.files[0].name[:12]}..."
            lbl_logo_status.color = ft.Colors.GREEN_400
            page.update()

    file_picker_logo = ft.FilePicker(on_result=on_logo_selecionada)

    # NÃO adicione o file_picker_logo no page.overlay ou page.add!

    def selecionar_logo(e):
        try:
            file_picker_logo.pick_files(
                allow_multiple=False,
                file_type=ft.FilePickerFileType.IMAGE
            )
        except Exception as err:
            page.snack_bar = ft.SnackBar(ft.Text(f"Seleção indisponível no mobile: {err}"))
            page.snack_bar.open = True
            page.update()

    # --- 2. CAMPOS DE ENTRADA ---
    ent_valor = ft.TextField(label="Valor Financiado Bruto (R$)", value="50000", keyboard_type=ft.KeyboardType.NUMBER)
    ent_tarifas = ft.TextField(label="Tarifas/Seguros Indevidos (R$)", value="2000",
                               keyboard_type=ft.KeyboardType.NUMBER)
    ent_prazo = ft.TextField(label="Prazo (Nº Parcelas)", value="12", keyboard_type=ft.KeyboardType.NUMBER)
    ent_taxa_banco = ft.TextField(label="Taxa do Banco (% a.m.)", value="2.5", keyboard_type=ft.KeyboardType.NUMBER)
    ent_taxa_bacen = ft.TextField(label="Taxa BACEN Ref (% a.m.)", value="1.35", keyboard_type=ft.KeyboardType.NUMBER)

    opt_sistema = ft.Dropdown(
        label="Sistema de Amortização",
        value="PRICE",
        options=[ft.dropdown.Option("PRICE"), ft.dropdown.Option("SAC")]
    )

    lbl_logo_status = ft.Text("Sem logo selecionada", size=12, color=ft.Colors.GREY_500)
    ent_rodape = ft.TextField(label="Rodapé do PDF", value="Advocacia Rocha | OAB 12.345")

    # --- 3. CARDS DE RESULTADOS ---
    card_pago = ft.Text("R$ 0,00", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)
    card_devido = ft.Text("R$ 0,00", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
    card_simples = ft.Text("R$ 0,00", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
    card_dobro = ft.Text("R$ 0,00", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_400)

    # --- 4. TABELA DE MEMÓRIA DE CÁLCULO ---
    tabela = ft.DataTable(
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

    # --- 5. LÓGICA DE CÁLCULO E PDF ---
    def executar_calculo(e):
        try:
            val_bruto = float(ent_valor.value.replace(",", "."))
            tarifas = float(ent_tarifas.value.replace(",", "."))
            prazo = int(ent_prazo.value)
            taxa_banco = float(ent_taxa_banco.value.replace(",", ".")) / 100
            taxa_bacen = float(ent_taxa_bacen.value.replace(",", ".")) / 100
            sistema = opt_sistema.value

            resumo, memoria = calcular_revisao_contrato(
                val_bruto, tarifas, prazo, taxa_banco, taxa_bacen, sistema, valores_pagos_custom
            )

            resumo_atual["dados"] = resumo
            memoria_atual["dados"] = memoria

            tabela.rows.clear()
            for row in memoria:
                tabela.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(row['parcela']))),
                            ft.DataCell(ft.Text(f"R$ {row['pago_real']:,.2f}")),
                            ft.DataCell(ft.Text(f"R$ {row['saldo_inicial']:,.2f}")),
                            ft.DataCell(ft.Text(f"R$ {row['juros']:,.2f}")),
                            ft.DataCell(ft.Text(f"R$ {row['amortizacao']:,.2f}")),
                            ft.DataCell(ft.Text(f"R$ {row['prestacao_correta']:,.2f}")),
                            ft.DataCell(ft.Text(f"R$ {row['saldo_final']:,.2f}")),
                            ft.DataCell(ft.Text(f"R$ {row['diferenca']:,.2f}")),
                        ]
                    )
                )

            card_pago.value = f"R$ {resumo['tot_pago']:,.2f}"
            card_devido.value = f"R$ {resumo['tot_devido']:,.2f}"
            card_simples.value = f"R$ {resumo['tot_dif']:,.2f}"
            card_dobro.value = f"R$ {resumo['tot_dobro']:,.2f}"

            page.snack_bar = ft.SnackBar(ft.Text("Cálculo realizado!"))
            page.snack_bar.open = True
            page.update()

        except Exception as err:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro: {str(err)}"))
            page.snack_bar.open = True
            page.update()

    def gerar_pdf_click(e):
        if not resumo_atual["dados"]:
            page.snack_bar = ft.SnackBar(ft.Text("Calcule antes de exportar!"))
            page.snack_bar.open = True
            page.update()
            return

        try:
            params = {
                "val_bruto": float(ent_valor.value.replace(",", ".")),
                "tarifas": float(ent_tarifas.value.replace(",", ".")),
                "prazo": int(ent_prazo.value),
                "taxa_banco": float(ent_taxa_banco.value.replace(",", ".")) / 100,
                "taxa_bacen": float(ent_taxa_bacen.value.replace(",", ".")) / 100,
                "sistema": opt_sistema.value
            }
            caminho_pdf = "/sdcard/Download/laudo_revisional.pdf"
            exportar_pdf(caminho_pdf, params, resumo_atual["dados"], memoria_atual["dados"], logo_path["caminho"],
                         ent_rodape.value)

            page.snack_bar = ft.SnackBar(ft.Text("PDF salvo na pasta Downloads!"))
            page.snack_bar.open = True
            page.update()
        except Exception as err:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao gerar PDF: {str(err)}"))
            page.snack_bar.open = True
            page.update()

    # --- 6. PAINEL DE CARDS ---
    painel_cards = ft.Row(
        controls=[
            ft.Card(content=ft.Container(content=ft.Column([ft.Text("TOTAL PAGO", size=9), card_pago]), padding=6)),
            ft.Card(content=ft.Container(content=ft.Column([ft.Text("TOTAL DEVIDO", size=9), card_devido]), padding=6)),
            ft.Card(
                content=ft.Container(content=ft.Column([ft.Text("REST. SIMPLES", size=9), card_simples]), padding=6)),
            ft.Card(content=ft.Container(content=ft.Column([ft.Text("REST. DOBRO", size=9), card_dobro]), padding=6)),
        ],
        scroll=ft.ScrollMode.AUTO
    )

    # --- 7. MONTAGEM EM LISTVIEW COMPACTO ---
    layout_conteudo = ft.ListView(
        controls=[
            ft.Text("PARÂMETROS DO CONTRATO", size=16, weight=ft.FontWeight.BOLD),
            ent_valor,
            ent_tarifas,
            ent_prazo,
            ent_taxa_banco,
            ent_taxa_bacen,
            opt_sistema,
            ft.ElevatedButton("📷 Selecionar Logo", on_click=selecionar_logo),
            lbl_logo_status,
            ent_rodape,
            ft.ElevatedButton("CALCULAR REVISÃO", on_click=executar_calculo, bgcolor=ft.Colors.GREEN_700,
                              color=ft.Colors.WHITE, height=45),
            ft.ElevatedButton("EXPORTAR PDF", on_click=gerar_pdf_click, bgcolor=ft.Colors.BLUE_700,
                              color=ft.Colors.WHITE, height=45),
            ft.Divider(),
            painel_cards,
            ft.Divider(),
            ft.Text("MEMÓRIA DE CÁLCULO", size=15, weight=ft.FontWeight.BOLD),
            ft.Row([tabela], scroll=ft.ScrollMode.AUTO)
        ],
        spacing=10,
        expand=True
    )

    page.add(layout_conteudo)


if __name__ == "__main__":
    ft.app(target=main_flet)