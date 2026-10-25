"""Leitura dos prompts em Markdown da pasta prompts/."""

from config import PASTA_PROMPTS


def carregar_prompt(nome_arquivo):
    """Devolve o conteúdo do prompt. Erro claro se o arquivo não existir ou estiver vazio."""
    caminho = PASTA_PROMPTS / nome_arquivo
    if not caminho.exists():
        raise FileNotFoundError(f"Prompt não encontrado: {caminho}")
    conteudo = caminho.read_text(encoding="utf-8").strip()
    if not conteudo:
        raise ValueError(f"Prompt vazio: {caminho}")
    return conteudo
