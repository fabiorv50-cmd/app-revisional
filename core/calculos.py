# core/calculos.py

def calcular_revisao_contrato(val_bruto, tarifas, prazo, taxa_banco, taxa_bacen, sistema, valores_pagos_custom=None):
    if valores_pagos_custom is None:
        valores_pagos_custom = {}

    val_liquido = val_bruto - tarifas
    saldo_dev = val_liquido

    pmt_orig = val_bruto * (taxa_banco * (1 + taxa_banco) ** prazo) / (((1 + taxa_banco) ** prazo) - 1)
    pmt_bacen = val_liquido * (taxa_bacen * (1 + taxa_bacen) ** prazo) / (((1 + taxa_bacen) ** prazo) - 1)

    memoria_calculo = []
    tot_pago = 0
    tot_devido = 0
    tot_dif = 0

    for i in range(1, prazo + 1):
        juros_mes = saldo_dev * taxa_bacen

        if sistema == "PRICE":
            prest_correta = pmt_bacen
            amort_mes = prest_correta - juros_mes
        else:  # SAC
            amort_mes = val_liquido / prazo
            prest_correta = amort_mes + juros_mes

        saldo_final = max(0, saldo_dev - amort_mes)
        pago_real = valores_pagos_custom.get(i, pmt_orig)
        diferenca = pago_real - prest_correta

        tot_pago += pago_real
        tot_devido += prest_correta
        tot_dif += diferenca

        memoria_calculo.append({
            "parcela": i,
            "pago_real": pago_real,
            "saldo_inicial": saldo_dev,
            "juros": juros_mes,
            "amortizacao": amort_mes,
            "prestacao_correta": prest_correta,
            "saldo_final": saldo_final,
            "diferenca": diferenca
        })

        saldo_dev = saldo_final

    resumo = {
        "tot_pago": tot_pago,
        "tot_devido": tot_devido,
        "tot_dif": tot_dif,
        "tot_dobro": tot_dif * 2
    }

    return resumo, memoria_calculo