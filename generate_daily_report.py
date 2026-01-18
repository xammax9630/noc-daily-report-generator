#!/usr/bin/env python3
"""
generate_daily_report.py

Script para gerar relatório diário do NOC em formato Markdown a partir de um CSV de incidentes.

O CSV de entrada deve conter colunas: timestamp (YYYY-MM-DD HH:MM:SS), host, categoria, severidade, descrição.

O script agrupa os incidentes por severidade e categoria, conta ocorrências, lista os incidentes mais recentes e gera um arquivo .md com sumário, estatísticas e incidentes listados.

Uso:
    python generate_daily_report.py --input incidents.csv --output relatorio.md --limit 10

Parâmetros:
    --input: arquivo CSV de entrada.
    --output: arquivo Markdown de saída (default: report_<data>.md).
    --limit: número máximo de incidentes a listar (default: 10).
    --encoding: encoding do CSV (default: utf-8).

Criado em 2026-01-18.
"""

import argparse
import csv
from collections import Counter
from datetime import datetime


def parse_arguments():
    parser = argparse.ArgumentParser(description="Gerar relatório diário do NOC em Markdown")
    parser.add_argument("--input", "-i", required=True, help="Arquivo CSV de incidentes")
    parser.add_argument("--output", "-o", help="Arquivo Markdown de saída (default: report_<data>.md)")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Número de incidentes a listar no relatório")
    parser.add_argument("--encoding", "-e", default="utf-8", help="Encoding do arquivo CSV")
    return parser.parse_args()


def read_incidents(path, encoding):
    incidents = []
    with open(path, "r", encoding=encoding) as f:
        reader = csv.DictReader(f)
        for row in reader:
            incidents.append(row)
    return incidents


def summarize_incidents(incidents):
    severidades = Counter()
    categorias = Counter()
    for inc in incidents:
        severidades[inc.get("severidade", "Desconhecido")] += 1
        categorias[inc.get("categoria", "Desconhecido")] += 1
    return severidades, categorias


def generate_markdown(incidents, severidades, categorias, limit):
    md = []
    md.append("# Relatório Diário do NOC\n")
    md.append(f"Data de geração: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    md.append("## Estatísticas de Incidentes\n")
    md.append("### Por Severidade\n")
    for sev, count in severidades.most_common():
        md.append(f"- **{sev}**: {count}\n")
    md.append("\n### Por Categoria\n")
    for cat, count in categorias.most_common():
        md.append(f"- **{cat}**: {count}\n")
    md.append("\n## Top Incidentes Recentes\n")
    # Ordena por timestamp decrescente
    sorted_inc = sorted(incidents, key=lambda x: x.get("timestamp", ""), reverse=True)
    for inc in sorted_inc[:limit]:
        md.append(f"- `{inc.get('timestamp')}` **{inc.get('severidade')}** {inc.get('categoria')} - {inc.get('host')}: {inc.get('descricao')}\n")
    return "\n".join(md)


def write_markdown(md_text, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_text)


def main():
    args = parse_arguments()
    output = args.output
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"report_{timestamp}.md"
    incidents = read_incidents(args.input, args.encoding)
    severidades, categorias = summarize_incidents(incidents)
    md_text = generate_markdown(incidents, severidades, categorias, args.limit)
    write_markdown(md_text, output)
    print(f"Relatório gerado: {output}")


if __name__ == "__main__":
    main()
