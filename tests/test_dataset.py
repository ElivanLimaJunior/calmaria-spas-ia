import pandas as pd
import pytest

from config import COLUNAS_OBRIGATORIAS, INTENCOES, PROMPT_FILES
from dataset import DatasetInvalidoError, amostra, carregar_dataset, preprocessar_pergunta, validar_dataset
from observabilidade import mascarar_dados_sensiveis
from prompts import carregar_prompt


def test_dataset_real_e_valido():
    df = carregar_dataset()
    assert df.shape == (50, 6)
    assert list(df.columns) == COLUNAS_OBRIGATORIAS
    assert set(df["intencao"]) <= set(INTENCOES)


def test_amostra_de_10_cobre_as_6_intencoes_do_dataset():
    df = carregar_dataset()
    assert set(amostra(df, 10)["intencao"]) == set(df["intencao"])


def test_others_e_opcao_valida_mesmo_fora_do_dataset():
    assert "others" in INTENCOES
    assert "others" not in set(carregar_dataset()["intencao"])


def test_coluna_ausente():
    df = carregar_dataset().drop(columns=["intencao"])
    with pytest.raises(DatasetInvalidoError, match="intencao"):
        validar_dataset(df)


def test_valor_vazio_e_intencao_desconhecida():
    df = carregar_dataset()
    vazio = df.copy()
    vazio.loc[0, "pergunta_cliente"] = None
    with pytest.raises(DatasetInvalidoError, match="vazios"):
        validar_dataset(vazio)
    estranha = df.copy()
    estranha.loc[0, "intencao"] = "comprar_voucher"
    with pytest.raises(DatasetInvalidoError, match="desconhecidas"):
        validar_dataset(estranha)


def test_arquivo_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        carregar_dataset(tmp_path / "nao_existe.csv")


def test_preprocessar_pergunta():
    assert preprocessar_pergunta("  Quanto custa?  \n") == ("Quanto custa?", 13)


def test_prompts_existem_e_nao_estao_vazios():
    for arquivo in PROMPT_FILES.values():
        assert carregar_prompt(arquivo)
    assert "SCORE: X | REASON:" in carregar_prompt("juiz_calmaria.md")
    texto_intencao = carregar_prompt("classificar_intencao.md")
    assert all(intencao in texto_intencao for intencao in INTENCOES)


def test_mascara_remove_identificadores():
    dados = {"input": "Meu email é ana@exemplo.com, CPF 123.456.789-09, tel (11) 98765-4321",
             "lista": ["sem dados"], "numero": 3}
    mascarado = mascarar_dados_sensiveis(data=dados)
    assert mascarado["input"] == "Meu email é [EMAIL], CPF [CPF], tel [TELEFONE]"
    assert mascarado["lista"] == ["sem dados"] and mascarado["numero"] == 3
