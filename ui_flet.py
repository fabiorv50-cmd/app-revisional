import os
import flet as ft
from core.calculos import calcular_revisao_contrato
from core.gerador_pdf import exportar_pdf


def main_flet(page: ft.Page):
    page.title = "Sistema Pericial Revisional"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 12

    # Estado da aplicação
    valores_pagos_custom = {}
    resumo_atual = {"dados": None}
    memoria_atual = {"dados": None}

    # --- 1. CAMPOS DE ENTRADA ---
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

    ent_logo_path = ft.TextField(label="Caminho/URL da Logo (Opcional)", value="",
                                 hint_text="Ex: /sdcard/Download/logo.png")
    ent_rodape = ft.TextField(label="Rodapé do PDF", value="Advocacia Rocha | OAB 12.345")

    lbl_parcelas_status = ft.Text("Nenhuma parcela customizada.", size=12, color=ft.Colors.GREY_500)

    # --- 2. MODAL PARA EDITAR PARCELAS PAGAS ---
    ent_num_parcela = ft.TextField(label="Nº da Parcela", keyboard_type=ft.KeyboardType.NUMBER)
    ent_val_parcela = ft.TextField(label="Valor Efetivamente Pago (R$)", keyboard_type=ft.KeyboardType.NUMBER)

    def salvar_parcela_custom(e):
        try:
            num = int(ent_num_parcela.value)
            val = float(ent_val_parcela.value.replace(",", "."))
            valores_pagos_custom[num] = val
            lbl_parcelas_status.value = f"{len(valores_pagos_custom)} parcela(s) customizada(s)."
            lbl_parcelas_status.color = ft.Colors.GREEN_400
            dialog_parcelas.open = False
            ent_num_parcela.value = ""
            ent_val_parcela.value = ""
            page.snack_bar = ft.SnackBar(ft.Text(f"Parcela {num} salva com R$ {val:.2f}!"))
            page.snack_bar.open = True
            page.update()
        except Exception as err:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao salvar parcela: {err}"))
            page.snack_bar.open = True
            page.update()

    def fechar_dialog(e):
        dialog_parcelas.open = False
        page.update()

    dialog_parcelas = ft.AlertDialog(
        title=ft.Text("Editar Parcela Paga"),
        content=ft.Column([
            ent_num_parcela,
            ent_val_parcela
        ], tight=True, spacing=10),
        actions=[
            ft.TextButton("Cancelar", on_click=fechar_dialog),
            ft.ElevatedButton("Salvar", on_click=salvar_parcela_custom, bgcolor=ft.Colors.GREEN_700,
                              color=ft.Colors.WHITE)
        ]
    )

    def abrir_dialog_parcelas(e):
        page.dialog = dialog_parcelas
        dialog_parcelas.open = True
        page.update()

    # --- 3. CARDS DE RESULTADOS (GRID 2x2) ---
    card_pago = ft.Text("R$ 0,00", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)
    card_devido = ft.Text("R$ 0,00", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
    card_simples = ft.Text("R$ 0,00", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
    card_dobro = ft.Text("R$ 0,00", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_400)

    painel_cards = ft.Column(
        controls=[
            ft.Row(
                [
                    ft.Card(
                        content=ft.Container(content=ft.Column([ft.Text("TOTAL PAGO", size=8), card_pago]), padding=6),
                        expand=True),
                    ft.Card(content=ft.Container(content=ft.Column([ft.Text("TOTAL DEVIDO", size=8), card_devido]),
                                                 padding=6), expand=True),
                ]
            ),
            ft.Row(
                [
                    ft.Card(content=ft.Container(content=ft.Column([ft.Text("REST. SIMPLES", size=8), card_simples]),
                                                 padding=6), expand=True),
                    ft.Card(content=ft.Container(content=ft.Column([ft.Text("REST. DOBRO", size=8), card_dobro]),
                                                 padding=6), expand=True),
                ]
            )
        ]
    )

    # --- 4. TABELA DE CÁLCULO ---
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

    # --- 5. LÓGICA DE CÁLCULO E EXPORTAÇÃO PDF ---
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

            page.snack_bar = ft.SnackBar(ft.Text("Cálculo realizado com sucesso!"))
            page.snack_bar.open = True
            page.update()

        except Exception as err:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro no cálculo: {str(err)}"))
            page.snack_bar.open = True
            page.update()

    def gerar_pdf_click(e):
        if not resumo_atual["dados"]:
            page.snack_bar = ft.SnackBar(ft.Text("Execute o cálculo antes de exportar!"))
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

            # Rotina de seleção de diretório no Android
            pasta_destino = "/storage/emulated/0/Download"
            if not os.path.exists(pasta_destino):
                os.makedirs(pasta_destino, exist_ok=True)

            caminho_pdf = os.path.join(pasta_destino, "laudo_revisional.pdf")
            exportar_pdf(caminho_pdf, params, resumo_atual["dados"], memoria_atual["dados"], ent_logo_path.value,
                         ent_rodape.value)

            page.snack_bar = ft.SnackBar(ft.Text(f"PDF salvo em: {caminho_pdf}"))
            page.snack_bar.open = True
            page.update()
        except Exception as err:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao gerar PDF: {str(err)}"))
            page.snack_bar.open = True
            page.update()

    # --- 6. MONTAGEM DA INTERFACE EM LISTVIEW ---
    conteudo_formulario = ft.Column(
        controls=[
            ft.Text("PARÂMETROS DO CONTRATO", size=15, weight=ft.FontWeight.BOLD),
            ent_valor,
            ent_tarifas,
            ent_prazo,
            ent_taxa_banco,
            ent_taxa_bacen,
            opt_sistema,
            ft.OutlinedButton("📝 Editar Parcelas Pagas", on_click=abrir_dialog_parcelas),
            lbl_parcelas_status,
            ent_logo_path,
            ent_rodape,
            ft.ElevatedButton("CALCULAR REVISÃO", on_click=executar_calculo, bgcolor=ft.Colors.GREEN_700,
                              color=ft.Colors.WHITE, height=45),
            ft.ElevatedButton("EXPORTAR PDF", on_click=gerar_pdf_click, bgcolor=ft.Colors.BLUE_700,
                              color=ft.Colors.WHITE, height=45),
            ft.Divider(),
            painel_cards,
            ft.Divider(),
            ft.Text("MEMÓRIA DE CÁLCULO", size=14, weight=ft.FontWeight.BOLD),
            ft.Row([tabela], scroll=ft.ScrollMode.ALWAYS)
        ],
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH
    )

    page.add(
        ft.ListView(
            controls=[conteudo_formulario],
            expand=True,
            spacing=10
        )
    )


if __name__ == "__main__":
    ft.app(target=main_flet)