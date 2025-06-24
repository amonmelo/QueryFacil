# Gerador de Relatórios SQL com Interface Gráfica (PyQt5)

Esse é um app de desktop feito em Python pra facilitar a vida de quem trabalha com PostgreSQL e precisa rodar queries e exportar resultados direto pra Excel. Tudo isso com uma interface simples, sem depender de planilhas feitas na mão ou ferramentas complicadas.

As conexões e queries são salvas localmente usando SQLite, então você pode abrir o app outro dia e continuar de onde parou.

---

## 🧰 O que o app faz

- Conecta em múltiplos bancos PostgreSQL (você pode salvar, editar ou apagar conexões)
- Testa a conexão antes de salvar
- Executa comandos SQL (SELECT, INSERT, UPDATE, DELETE, etc.)
- Permite salvar e reaproveitar queries
- Exporta resultados de SELECT pra Excel (.xlsx), com colunas ajustadas automaticamente
- Mostra logs dentro da própria interface
- Salva tudo localmente (nada na nuvem)

---

## 🧑‍💻 Compatível com LATIN1

Esse app já vem pronto pra funcionar com bancos PostgreSQL que usam codificação `LATIN1` (ISO-8859-1). Isso evita erro com acentos, caracteres especiais e nomes de cliente.

A conexão é feita usando:

```python
options='-c client_encoding=LATIN1'
```

Se o seu banco usar `UTF-8`, também vai funcionar normalmente.

---

## 🗂️ Estrutura dos arquivos

```
📁 logs/                      # onde ficam os arquivos de log
📁 relatorios_gerados/       # onde os relatórios Excel são salvos
📄 app_completo.py           # código principal do sistema
📄 db_connections.db         # banco SQLite local com configs e queries
📄 requirements.txt          # bibliotecas necessárias
📄 README.md                 # esse arquivo aqui
```

---

## ⚙️ O que você precisa ter

- Python 3.8 ou superior
- PostgreSQL acessível
- Sistema operacional: Windows, Linux ou macOS

---

## 📦 Instalando as dependências

Crie seu ambiente virtual se quiser (opcional):

```bash
python -m venv venv
venv\Scripts\activate  # no Windows
source venv/bin/activate  # no Linux/mac
```

Depois instale os pacotes com:

```bash
pip install -r requirements.txt
```

Ou, se preferir instalar manualmente:

```bash
pip install PyQt5 pandas openpyxl psycopg2-binary
```

---

## ▶️ Como rodar

Abra o terminal ou prompt na pasta do projeto e execute:

```bash
python app_completo.py
```

---

## 🔎 Como usar na prática

1. Clique em **Add Connection** e preencha os dados (host, porta, banco, user, senha).
2. Teste a conexão e salve.
3. Escreva sua query SQL (ex: `SELECT * FROM clientes`).
4. Rode a query clicando em **Execute Query**.
5. Se quiser exportar o resultado, preencha o nome do relatório e clique em **Export Last Query Results**.
6. O Excel será salvo automaticamente na pasta `relatorios_gerados`.

---

## 📤 Exportação de Relatórios

- Formato: `.xlsx` (Excel)
- Os arquivos vão pra pasta `relatorios_gerados/`
- O app cria uma subpasta com o nome do banco + data/hora
- O nome do arquivo vem do campo "Report Name"

---

## 📝 Logs

O app gera logs automáticos em:

```
logs/app.log
```

Você também consegue ver os logs na parte de baixo da interface.

---

## 🗃️ Banco de dados local (SQLite)

Tudo que é salvo (conexões e queries) fica armazenado em um arquivo local chamado:

```
db_connections.db
```

💡 Importante: as senhas são armazenadas em texto puro (sem criptografia), então use em ambientes seguros.

---

## 💡 Exemplo de query

```sql
SELECT nome, cidade FROM tab_clientes WHERE uf = 'CE';
```

---

## 📜 Licença

Código livre. Pode usar, modificar e compartilhar à vontade. Só não vale dizer que foi você que fez se não foi 😄

---

Feito com carinho, café e Python ☕🐍
