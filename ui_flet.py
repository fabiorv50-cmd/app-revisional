import flet as ft
from core.calculos import calcular_revisao_contrato
from core.gerador_pdf import gerar_pdf_revisional


def main_flet(page: ft.Page):
    page.title = "Sistema Revisional (Flet/Mobile)"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 15

    valores_pagos_custom = {}
    dados = {"resumo": None, "memoria": None}
    caminho_logo = {"path": None}

    # Campos de Entrada
    txt_valor = ft.TextField(label="Valor Financiado Bruto (R$)", value="50000")
    txt_tarifas = ft.TextField(label="Tarifas/Seguros (R$)", value="2000")
    txt_prazo = ft.TextField(label="Prazo (Parcelas)", value="12")
    txt_taxa_banco = ft.TextField(label="Taxa Banco (% a.m.)", value="2.5")
    txt_taxa_bacen = ft.TextField(label="Taxa BACEN (% a.m.)", value="1.35")
    dd_sistema = ft.Dropdown(
        label="Sistema de Amortização",
        value="PRICE",
        options=[ft.dropdown.Option("PRICE"), ft.dropdown.Option("SAC")]
    )
    txt_rodape = ft.TextField(label="Texto do Rodapé do PDF", value="Bravo Service | Perícias & Advocacia")

    # Labels de Resultado
    lbl_pago = ft.Text("R$ 0,00", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)
    lbl_devido = ft.Text("R$ 0,00", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
    lbl_simples = ft.Text("R$ 0,00", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
    lbl_dobro = ft.Text("R$ 0,00", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_400)
    lbl_logo_status = ft.Text("Nenhuma logo selecionada", size=12, italic=True, color=ft.Colors.GREY_400)

    # FilePicker para Logo
    def resultado_picker_logo(e: ft.FilePickerResultEvent):
        if e.files:
            caminho_logo["path"] = e.files[0].path
            lbl_logo_status.value = f"Logo: {e.files[0].name}"
            lbl_logo_status.color = ft.Colors.GREEN_400
            page.update()

    picker_logo = ft.FilePicker(on_result=resultado_picker_logo)
    page.overlay.append(picker_logo)

    # Tabela de Memória de Cálculo
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

    # Função Principal de Cálculo
    def calcular(e=None):
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
        except Exception as err:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro nos dados: {err}"), open=True)
            page.update()

    # Modal para Editar Parcelas
    txt_num_parcela = ft.TextField(label="Nº da Parcela", keyboard_type=ft.KeyboardType.NUMBER)
    txt_val_custom = ft.TextField(label="Novo Valor Pago (R$)", keyboard_type=ft.KeyboardType.NUMBER)

    def salvar_edicao_parcela(e):
        try:
            p_num = int(txt_num_parcela.value)
            v_val = float(txt_val_custom.value.replace(",", "."))
            valores_pagos_custom[p_num] = v_val
            modal_editar.open = False
            calcular()
            page.snack_bar = ft.SnackBar(ft.Text(f"Parcela {p_num} alterada!"), open=True)
            page.update()
        except Exception:
            page.snack_bar = ft.SnackBar(ft.Text("Número ou valor inválido!"), open=True)
            page.update()

    modal_editar = ft.AlertDialog(
        title=ft.Text("Editar Valor da Parcela"),
        content=ft.Column([txt_num_parcela, txt_val_custom], tight=True),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: setattr(modal_editar, "open", False) or page.update()),
            ft.ElevatedButton("Salvar", on_click=salvar_edicao_parcela, bgcolor=ft.Colors.BLUE_700,
                              color=ft.Colors.WHITE)
        ]
    )

    # Gerar Relatório PDF
    def gerar_pdf(e):
        if not dados["resumo"]:
            page.snack_bar = ft.SnackBar(ft.Text("Execute o cálculo antes de gerar o PDF!"), open=True)
            page.update()
            return

        try:
            caminho_pdf = "relatorio_revisional.pdf"
            gerar_pdf_revisional(
                caminho_pdf,
                dados["resumo"],
                dados["memoria"],
                txt_rodape.value,
                caminho_logo["path"]
            )
            page.snack_bar = ft.SnackBar(ft.Text(f"PDF Gerado com sucesso em: {caminho_pdf}"), open=True)
            page.update()
        except Exception as err:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao gerar PDF: {err}"), open=True)
            page.update()

    # Interface Visual Grid
    grid_cards = ft.ResponsiveRow([
        ft.Container(ft.Column([ft.Text("TOTAL PAGO", size=9), lbl_pago]), col={"sm": 6, "md": 3},
                     border=ft.Border.all(1, ft.Colors.RED_400), padding=8, border_radius=8),
        ft.Container(ft.Column([ft.Text("TOTAL DEVIDO", size=9), lbl_devido]), col={"sm": 6, "md": 3},
                     border=ft.Border.all(1, ft.Colors.GREEN_400), padding=8, border_radius=8),
        ft.Container(ft.Column([ft.Text("REST. SIMPLES", size=9), lbl_simples]), col={"sm": 6, "md": 3},
                     border=ft.Border.all(1, ft.Colors.BLUE_400), padding=8, border_radius=8),
        ft.Container(ft.Column([ft.Text("REST. DOBRO", size=9), lbl_dobro]), col={"sm": 6, "md": 3},
                     border=ft.Border.all(1, ft.Colors.PURPLE_400), padding=8, border_radius=8),
    ])

    # Montagem da Tela
    page.add(
        ft.Text("SISTEMA REVISIONAL PERICIAL", size=18, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        txt_valor, txt_tarifas, txt_prazo, txt_taxa_banco, txt_taxa_bacen, dd_sistema, txt_rodape,

        # Seção de Upload de Logo
        ft.Row([
            ft.OutlinedButton("Selecionar Logo", icon=ft.Icons.IMAGE,
                              on_click=lambda _: picker_logo.pick_files(allow_multiple=False)),
            lbl_logo_status
        ]),
        ft.Divider(),

        # Botões de Ação Principais
        ft.ResponsiveRow([
            ft.Container(
                ft.ElevatedButton("CALCULAR REVISÃO", on_click=calcular, bgcolor=ft.Colors.GREEN_700,
                                  color=ft.Colors.WHITE, height=45),
                col={"sm": 12, "md": 4}
            ),
            ft.Container(
                ft.OutlinedButton("EDITAR PARCELA", icon=ft.Icons.EDIT, on_click=lambda e: page.open(modal_editar),
                                  height=45),
                col={"sm": 12, "md": 4}
            ),
            ft.Container(
                ft.ElevatedButton("GERAR RELATÓRIO PDF", icon=ft.Icons.PICTURE_AS_PDF, on_click=gerar_pdf,
                                  bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, height=45),
                col={"sm": 12, "md": 4}
            ),
        ]),
        ft.Divider(),
        grid_cards,
        ft.Divider(),
        ft.Text("Memória de Cálculo:", weight=ft.FontWeight.BOLD),
        ft.Row([dt_memoria], scroll=ft.ScrollMode.ALWAYS)
    )


if __name__ == "__main__":
    ft.app(target=main_flet)