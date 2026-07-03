# =================== AD-HOC PDF-01 =================== #
#     Remover páginas de PDF preservando  estrutura     #
# ----------------------------------------------------- #
# Comandos:                                             #
# =========                                             #
#                                                       #
# Remover páginas 3, 5 e 7                              #
# python3 tool_pdf_01.py entrada.pdf saida.pdf 3,5,7    #
#                                                       #
# Remover páginas de 1 a 5 e a página 10                #
# python3 tool_pdf_01.py entrada.pdf saida.pdf 1-5,10   #
#                                                       #
# Remover apenas a página 8                             #
# python3 tool_pdf_01.py entrada.pdf saida.pdf 8        #
#                                                       #
# Instalar: pip install pypdf                           #
# ===================================================== #

from pypdf import PdfReader, PdfWriter
import sys
import argparse

def parse_pages(pages_str):
    """Converte string como '1,3-5,10' em lista de números (1-based)"""
    pages = set()
    for part in pages_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    return sorted(pages)


def remove_pdf_pages(input_path: str, output_path: str, pages_to_remove: list):
    """
    Remove páginas específicas de um PDF sem alterar o conteúdo das páginas restantes.
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    total_pages = len(reader.pages)
    pages_to_remove_set = set(pages_to_remove)
    
    print(f"Total de páginas: {total_pages}")
    print(f"Removendo páginas: {pages_to_remove}\n")
    
    kept_pages = 0
    for i in range(total_pages):
        page_num = i + 1  # número da página (1-based)
        if page_num in pages_to_remove_set:
            print(f"Removendo página {page_num}")
        else:
            writer.add_page(reader.pages[i])
            kept_pages += 1
    
    # Salva o novo PDF
    with open(output_path, "wb") as output_file:
        writer.write(output_file)
    
    print(f"\nConcluído! {kept_pages} páginas mantidas.")
    print(f"Arquivo salvo como: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Remove páginas específicas de um PDF sem alterar o conteúdo original."
    )
    parser.add_argument("input", help="Caminho do PDF de entrada")
    parser.add_argument("output", help="Caminho do PDF de saída")
    parser.add_argument(
        "pages", 
        help="Páginas para remover (ex: 3,5,7-10,15)"
    )
    
    args = parser.parse_args()
    
    try:
        pages_to_remove = parse_pages(args.pages)
        remove_pdf_pages(args.input, args.output, pages_to_remove)
    except Exception as e:
        print(f"Erro: {e}")
