"""
Aplicação de Linha de Comando (CLI) para o Pipeline de Engenharia de Dados.
Permite executar o pipeline completo em 3 camadas e visualizar relatórios dos indicadores de negócio.
"""
import sys
import argparse
from pathlib import Path

# Adiciona o diretório raiz ao sys.path para permitir execução direta via `python src/main.py`
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Configura stdout para UTF-8 se possível
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from typing import Optional
import pandas as pd
from src.config import DB_PATH
from src.database import reset_db
from src.extract import extrair_camada_raw
from src.transform import transformar_camada_refined
from src.marts import materializar_camada_marts, gerar_indicador


def formatar_tabela(df: pd.DataFrame) -> str:
    """Formata um DataFrame para exibição elegante no terminal."""
    try:
        from tabulate import tabulate
        return tabulate(df, headers="keys", tablefmt="grid", showindex=False)
    except ImportError:
        return df.to_string(index=False)


def executar_pipeline_completo() -> None:
    """Executa a sequência ponta a ponta do pipeline: Raw -> Refined -> Marts."""
    print("\n" + "=" * 60)
    print(">>> INICIANDO EXECUCAO DO PIPELINE DE DADOS")
    print("=" * 60)

    # 1. Camada Raw
    print("\n[1/3] Ingestao da Camada RAW (Dados Brutos Intocados)...")
    raw_totais = extrair_camada_raw()
    for tab, total in raw_totais.items():
        print(f"      [OK] {tab}: {total} registros ingeridos.")

    # 2. Camada Refined
    print("\n[2/3] Processando Camada REFINED (Limpeza, Tipagem e Integridade)...")
    refined_totais = transformar_camada_refined()
    for tab, total in refined_totais.items():
        print(f"      [OK] {tab}: {total} registros refinados.")

    # 3. Camada Marts
    print("\n[3/3] Materializando Camada MARTS (Metricas e Indicadores SQL)...")
    marts_totais = materializar_camada_marts()
    for tab, total in marts_totais.items():
        print(f"      [OK] {tab}: {total} linhas analiticas geradas.")

    print("\n" + "=" * 60)
    print(">>> PIPELINE CONCLUIDO COM SUCESSO!")
    print("=" * 60)


def exibir_relatorio(titulo: str, arquivo_sql: str) -> None:
    """Executa e exibe no terminal o relatório de um indicador."""
    if not DB_PATH.exists():
        print("\n[!] O banco de dados ainda nao foi criado. Executando o pipeline primeiro...")
        executar_pipeline_completo()

    print(f"\n[RELATORIO] {titulo}")
    print("-" * 65)
    df = gerar_indicador(arquivo_sql)
    print(formatar_tabela(df))
    print("-" * 65)


def menu_interativo() -> None:
    """Exibe o menu de navegação no terminal."""
    while True:
        print("\n" + "=" * 55)
        print("  PLATAFORMA DE DADOS - E-COMMERCE TECH STORE")
        print("=" * 55)
        print("1. Executar Pipeline Completo (Raw -> Refined -> Marts)")
        print("2. Relatorio: Faturamento e Margem por Categoria")
        print("3. Relatorio: Ranking de Produtos Mais Vendidos")
        print("4. Relatorio: Faturamento por Cliente (LTV)")
        print("5. Relatorio: Metricas Mensais e Ticket Medio")
        print("6. Resetar Banco de Dados")
        print("0. Sair")
        print("=" * 55)

        opcao = input("Selecione uma opcao: ").strip()

        if opcao == "1":
            executar_pipeline_completo()
        elif opcao == "2":
            exibir_relatorio(
                "Faturamento e Margem por Categoria",
                "faturamento_por_categoria.sql"
            )
        elif opcao == "3":
            exibir_relatorio(
                "Ranking de Produtos Mais Vendidos",
                "produtos_mais_vendidos.sql"
            )
        elif opcao == "4":
            exibir_relatorio(
                "Faturamento e Ticket Medio por Cliente",
                "faturamento_por_cliente.sql"
            )
        elif opcao == "5":
            exibir_relatorio(
                "Metricas Mensais e Ticket Medio por Pedido",
                "metricas_mensais_ticket_medio.sql"
            )
        elif opcao == "6":
            confirmacao = input("Tem certeza que deseja apagar o banco? (s/N): ").strip().lower()
            if confirmacao == "s":
                reset_db()
                print("Banco de dados removido com sucesso.")
        elif opcao == "0":
            print("\nEncerrando a aplicacao. Ate logo!\n")
            sys.exit(0)
        else:
            print("[!] Opcao invalida. Tente novamente.")


def main():
    parser = argparse.ArgumentParser(description="Pipeline de Engenharia de Dados - E-commerce")
    parser.add_argument("--run-pipeline", action="store_true", help="Executa o pipeline completo sem abrir o menu")
    parser.add_argument("--report", type=str, choices=["categoria", "produtos", "clientes", "mensal"], help="Exibe relatorio especifico")
    args = parser.parse_args()

    if args.run_pipeline:
        executar_pipeline_completo()
        return

    if args.report:
        mapa_relatorios = {
            "categoria": ("Faturamento por Categoria", "faturamento_por_categoria.sql"),
            "produtos": ("Produtos Mais Vendidos", "produtos_mais_vendidos.sql"),
            "clientes": ("Faturamento por Cliente", "faturamento_por_cliente.sql"),
            "mensal": ("Metricas Mensais", "metricas_mensais_ticket_medio.sql"),
        }
        titulo, sql = mapa_relatorios[args.report]
        exibir_relatorio(titulo, sql)
        return

    menu_interativo()


if __name__ == "__main__":
    main()
