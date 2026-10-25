"""Carga, validação e pré-processamento do dataset de interações."""

import pandas as pd

from config import COLUNAS_OBRIGATORIAS, DATASET, INTENCOES


class DatasetInvalidoError(ValueError):
    """O arquivo existe, mas não tem a estrutura esperada."""


def carregar_dataset(caminho=DATASET):
    """Lê o CSV e valida a estrutura antes de qualquer processamento.

    Levanta FileNotFoundError se o arquivo não existir e DatasetInvalidoError se
    faltarem colunas, houver valores vazios nas colunas obrigatórias, ids
    repetidos ou intenções fora da lista conhecida.
    """
    if not caminho.exists():
        raise FileNotFoundError(f"Dataset não encontrado: {caminho}")
    df = pd.read_csv(caminho)
    validar_dataset(df)
    return df


def validar_dataset(df):
    faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in df.columns]
    if faltando:
        raise DatasetInvalidoError(f"Colunas ausentes: {faltando}")
    if df.empty:
        raise DatasetInvalidoError("O dataset está vazio.")
    vazios = df[COLUNAS_OBRIGATORIAS].isna().sum()
    vazios = vazios[vazios > 0]
    if not vazios.empty:
        raise DatasetInvalidoError(f"Valores vazios: {vazios.to_dict()}")
    if df["id"].duplicated().any():
        raise DatasetInvalidoError("Há ids repetidos.")
    desconhecidas = set(df["intencao"]) - set(INTENCOES)
    if desconhecidas:
        raise DatasetInvalidoError(f"Intenções desconhecidas: {sorted(desconhecidas)}")


def preprocessar_pergunta(texto):
    """Remove espaços nas pontas. Devolve o texto limpo e o comprimento."""
    limpo = str(texto).strip()
    return limpo, len(limpo)


def amostra(df, tamanho):
    """Amostra reprodutível: as primeiras `tamanho` linhas, na ordem do arquivo."""
    return df.head(tamanho)
