"""Verifica se o ambiente está pronto para rodar os pipelines.

Uso:  python src/verificar_conexao.py

Checa: variáveis do .env preenchidas (sem mostrar valores), dataset válido,
prompts presentes e autenticação no Langfuse via get_client().auth_check().
Não chama a OpenAI (não gera custo).
"""

import sys

from config import (
    PROMPT_ASSISTENTE, PROMPT_FILES, PROMPT_INTENCAO, PROMPT_JUIZ,
    carregar_ambiente, credenciais_faltando,
)
from dataset import carregar_dataset
from observabilidade import inicializar_langfuse
from prompts import carregar_prompt


def main():
    modelo = carregar_ambiente()
    ok = True

    faltando = credenciais_faltando()
    if faltando:
        print(f"[PENDENTE] Variáveis vazias no .env: {', '.join(faltando)}")
        ok = False
    else:
        print("[OK] Variáveis do .env preenchidas")
    print(f"[INFO] Modelo configurado: {modelo}")

    df = carregar_dataset()
    print(f"[OK] Dataset válido: {len(df)} linhas, {len(df.columns)} colunas")

    for arquivo in [PROMPT_ASSISTENTE, *PROMPT_FILES.values(), PROMPT_INTENCAO, PROMPT_JUIZ]:
        carregar_prompt(arquivo)
    print("[OK] Prompts encontrados")

    if "LANGFUSE_PUBLIC_KEY" not in faltando and "LANGFUSE_SECRET_KEY" not in faltando:
        langfuse = inicializar_langfuse()
        if langfuse.auth_check():
            print("[OK] Langfuse autenticado")
        else:
            print("[ERRO] Langfuse recusou as credenciais. Confira as chaves e LANGFUSE_BASE_URL (região).")
            ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
