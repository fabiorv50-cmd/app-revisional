import os
import flet as ft
from core.calculos import calcular_revisao_contrato
from core.gerador_pdf import exportar_pdf


def main_flet(page: ft.Page):
    page.title = "Sistema Pericial Revisional"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 10

    # Estado global da aplicação
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

    ent_logo_path = ft.TextField(label="Caminho da Logo (Opcional)", value="")
    ent_rodape = ft.TextField(label="Rodapé do PDF", value="Advocacia Rocha | OAB 12.345")
    lbl_parcelas_status = ft.Text("Nenhuma parcela customizada.", size=12, color=ft.Colors.GREY_500)

    # --- 2. MODAL DE EDIÇÃO DE PARCELAS PAGAS ---
    ent_num_parcela = ft.TextField(label="Nº da Parcela", keyboard_type=ft.KeyboardType.NUMBER)
    ent_val_parcela = ft.TextField(label="Valor Pago (R$)", keyboard_type=ft.KeyboardType.NUMBER)

    def fechar_dialog(e):
        dialog_parcelas.open = False
        page.update()

    def salvar_parcela(e):
        if ent_num_parcela.value and ent_val_parcela.value:
            try:
                num = int(ent_num_parcela.value)
                val = float(ent_val_parcela.value.replace(",", "."))
                valores_pagos_custom[num] = val
                lbl_parcelas_status.value = f"{len(valores_pagos_custom)} parcela(s) alterada(s)."
                lbl_parcelas_status.color = ft.Colors.GREEN_400
                dialog_parcelas.open = False
                ent_num_parcela.value = ""
                ent_val_parcela.value = ""

                # Executa o cálculo para atualizar as parcelas na tela
                executar_calculo(None)
            except Exception as err:
                snack = ft.SnackBar(ft.Text(f"Erro ao salvar: {err}"))
                page.overlay.append(snack)
                snack.open = True
                page.update()

    dialog_parcelas = ft.AlertDialog(
        title=ft.Text("Editar Parcela Paga"),
        content=ft.Column([ent_num_parcela, ent_val_parcela], tight=True),
        actions=[
            ft.TextButton("Cancelar", on_click=fechar_dialog),
            ft.ElevatedButton("Salvar", on_click=salvar_parcela, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
        ]
    )

    def abrir_dialog(e):
        page.dialog = dialog_parcelas
        dialog_parcelas.open = True
        page.update()

    # --- 3. CARDS DE RESULTADOS ---
    card_pago = ft.Text("R$ 0,00", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)
    card_devido = ft.Text("R$ 0,00", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
    card_simples = ft.Text("R$ 0,00", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
    card_dobro = ft.Text("R$ 0,00", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_400)

    # --- 4. CONTAINER DA MEMÓRIA DE CÁLCULO ---
    lista_memoria = ft.Column(spacing=5)

    # --- 5. LÓGICA DO BOTÃO CALCULAR ---
    # --- LÓGICA DO BOTÃO CALCULAR CORRIGIDA ---
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

            card_pago.value = f"R$ {resumo['tot_pago']:,.2f}"
            card_devido.value = f"R$ {resumo['tot_devido']:,.2f}"
            card_simples.value = f"R$ {resumo['tot_dif']:,.2f}"
            card_dobro.value = f"R$ {resumo['tot_dobro']:,.2f}"

            # Montagem segura da lista de parcelas sem atributos de tema inexistentes
            lista_memoria.controls.clear()
            for row in memoria:
                lista_memoria.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(f"P{row['parcela']}", weight=ft.FontWeight.BOLD, width=35),
                                ft.Column([
                                    ft.Text(
                                        f"Pago: R$ {row['pago_real']:,.2f} | Correto: R$ {row['prestacao_correta']:,.2f}",
                                        size=11),
                                    ft.Text(f"Diferença: R$ {row['diferenca']:,.2f}", size=11,
                                            color=ft.Colors.GREEN_300 if row['diferenca'] > 0 else ft.Colors.WHITE)
                                ], expand=True)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        padding=8,
                        bgcolor=ft.Colors.GREY_900,  # Cor estática universal
                        border_radius=5
                    )
                )

            snack = ft.SnackBar(ft.Text("Cálculo e parcelas gerados com sucesso!"))
            page.overlay.append(snack)
            snack.open = True
            page.update()
        except Exception as err:
            snack = ft.SnackBar(ft.Text(f"Erro no cálculo: {err}"))
            page.overlay.append(snack)
            snack.open = True
            page.update()
            page.overlay.append(snack)
            snack.open = True
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

            # Define o caminho direto na pasta Downloads visível no Android
            pasta_download = "/storage/emulated/0/Download"
            if not os.path.exists(pasta_download):
                os.makedirs(pasta_download, exist_ok=True)

            caminho_pdf = os.path.join(pasta_download, "laudo_revisional.pdf")
            exportar_pdf(caminho_pdf, params, resumo_atual["dados"], memoria_atual["dados"], ent_logo_path.value,
                         ent_rodape.value)

            snack = ft.SnackBar(ft.Text(f"PDF salvo na pasta Downloads:\nlaudo_revisional.pdf"), duration=5000)
            page.overlay.append(snack)
            snack.open = True
            page.update()
        except Exception as err:
            snack = ft.SnackBar(ft.Text(f"Erro ao salvar PDF: {err}"))
            page.overlay.append(snack)
            snack.open = True
            page.update()

    # --- 7. MONTAGEM DA INTERFACE ---
    btn_calcular = ft.ElevatedButton("CALCULAR REVISÃO", on_click=executar_calculo, bgcolor=ft.Colors.GREEN_700,
                                     color=ft.Colors.WHITE, height=45)
    btn_pdf = ft.ElevatedButton("EXPORTAR PDF", on_click=gerar_pdf_click, bgcolor=ft.Colors.BLUE_700,
                                color=ft.Colors.WHITE, height=45)
    btn_editar = ft.OutlinedButton("📝 Editar Parcelas Pagas", on_click=abrir_dialog)

    page.add(
        ft.ListView(
            controls=[
                ft.Text("PARÂMETROS DO CONTRATO", size=15, weight=ft.FontWeight.BOLD),
                ent_valor,
                ent_tarifas,
                ent_prazo,
                ent_taxa_banco,
                ent_taxa_bacen,
                opt_sistema,
                btn_editar,
                lbl_parcelas_status,
                ent_logo_path,
                ent_rodape,
                btn_calcular,
                btn_pdf,
                ft.Divider(),
                ft.Text("RESUMO DOS CÁLCULOS", size=14, weight=ft.FontWeight.BOLD),
                ft.Card(content=ft.Container(content=ft.Column([ft.Text("TOTAL PAGO"), card_pago]), padding=8)),
                ft.Card(content=ft.Container(content=ft.Column([ft.Text("TOTAL DEVIDO"), card_devido]), padding=8)),
                ft.Card(
                    content=ft.Container(content=ft.Column([ft.Text("RESTITUIÇÃO SIMPLES"), card_simples]), padding=8)),
                ft.Card(
                    content=ft.Container(content=ft.Column([ft.Text("RESTITUIÇÃO EM DOBRO"), card_dobro]), padding=8)),
                ft.Divider(),
                ft.Text("MEMÓRIA DE CÁLCULO (PARCELAS)", size=14, weight=ft.FontWeight.BOLD),
                lista_memoria
            ],
            spacing=10,
            expand=True
        )
    )


if __name__ == "__main__":
    ft.app(target=main_flet)