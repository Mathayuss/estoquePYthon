# PyStock Ativos — Controle de Estoque para Ativos Individuais (QR)

**Desktop (Windows)** em Python + CustomTkinter, com SQLite + SQLAlchemy.

## Conceito do modelo
- **Produto** = modelo/tipo (ex.: "Notebook Dell Latitude 5420")
- **Ativo (unidade)** = item individual (patrimônio/serial) com **QR único**
- Entrada/Saída registra movimentações por **unidade** (não por quantidade)

## Telas principais
- Dashboard (total de ativos, em estoque, valor do estoque por custo, itens abaixo do mínimo)
- **Entrada (Retorno ao estoque)** — scan de QR
- **Saída (Entrega/Retirada)** — scan de QR + motivo personalizado
- Cadastros (Admin): Produtos, Categorias, Fornecedores, Ativos, Motivos de Saída, Usuários
- Relatórios (XLSX): ativos e movimentações

## Primeiro acesso
- usuário: `admin`
- senha: `admin123`

## Instalação / Execução (Windows PowerShell)
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Dica de operação
Use leitor USB (QR/Barcode) configurado para enviar **ENTER** após o scan.
No campo "Escanear QR", basta apontar e o sistema registra.

## Observação
Este build **removeu o preço de venda**; mantém apenas **custo** (uso interno e valuation).
