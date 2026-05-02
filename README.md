<div align="center">

🇧🇷 [Português](README.md) | 🇺🇸 [English](README.en.md) | 🇪🇸 [Español](README.es.md) | 🇩🇪 [Deutsch](README.de.md)

</div>

<br>

<div align="center">

# ⚡ QueryFacil

**Ferramenta desktop para otimizar e gerenciar queries SQL com interface gráfica intuitiva.**

Conecte-se ao PostgreSQL, execute queries, salve suas favoritas e exporte resultados para Excel — tudo num só lugar.

![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-41CD52?logo=qt&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Connected-336791?logo=postgresql&logoColor=white)
![License MIT](https://img.shields.io/badge/License-MIT-green.svg)

![Desktop App](https://img.shields.io/badge/Type-Desktop_Application-informational)
![Cross Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-orange)
![SQLite Local](https://img.shields.io/badge/Storage-Local_SQLite-critical)

</div>

<br>

## 📸 Interface

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Gerador de Relatórios SQL                                    ─  □  X   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─── Connection Management ──────────────────────────────────────────┐  │
│  │ Connection: [▼ Produção DB      ] [Add Connection] [Manage...]    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─── SQL Query ─────────────────────────────────────────────────────┐  │
│  │ Saved Query: [▼ Clientes por UF  ] [Save Current] [Manage...]    │  │
│  │ ┌────────────────────────────────────────────────────────────────┐ │  │
│  │ │ SELECT nome, cidade, uf                                       │ │  │
│  │ │ FROM tab_clientes                                             │ │  │
│  │ │ WHERE uf = 'CE'                                               │ │  │
│  │ │ ORDER BY nome;                                                │ │  │
│  │ └────────────────────────────────────────────────────────────────┘ │  │
│  │                              [ ▶  Execute Query                  ]  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─── Report Output Options ─────────────────────────────────────────┐  │
│  │ [✓] Excel (XLSX)    Output: relatorios_gerados/                   │  │
│  │ Report Name: [ clientes_ceara_ ]    [ 📥 Export Last Results    ] │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─── Logs and Query Output ─────────────────────────────────────────┐  │
│  │ 2026-01-15 10:32 - INFO - Connected to: Produção DB              │  │
│  │ 2026-01-15 10:32 - INFO - SELECT query executed successfully.     │  │
│  │         nome             cidade         uf                        │  │
│  │  ─────────────────────────────────────────────────                │  │
│  │  Ana Silva         Fortaleza        CE                           │  │
│  │  Carlos Souza      Sobral          CE                            │  │
│  │  ... (148 more rows. Export to see all.)                         │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

<br>

## ✅ Funcionalidades

| Recurso | Detalhes |
|---------|----------|
| ✅ **Múltiplas conexões** | Adicione, edite e gerencie várias conexões PostgreSQL |
| ✅ **Teste de conexão** | Valide a conexão antes de salvar |
| ✅ **Editor SQL integrado** | Escreva e execute queries diretamente na interface |
| ✅ **Queries favoritas** | Salve, carregue e gerencie suas queries mais usadas |
| ✅ **Exportação Excel** | Gere relatórios `.xlsx` com colunas auto-ajustadas |
| ✅ **Suporte LATIN1** | Compatível com bancos em codificação LATIN1/UTF-8 |
| ✅ **Logs em tempo real** | Visualize logs dentro da própria interface |
| ✅ **Armazenamento local** | Tudo salvo em SQLite — sem depender de nuvem |
| ✅ **Multi-plataforma** | Funciona no Windows, Linux e macOS |

<br>

## 🛠 Stack Técnica

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI_5.15%2B-41CD52?logo=qt&logoColor=white)
![psycopg2](https://img.shields.io/badge/psycopg2-binary-PostgreSQL_Driver-336791?logo=postgresql&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-Data_Manipulation-150458?logo=pandas&logoColor=white)
![openpyxl](https://img.shields.io/badge/openpyxl-Excel_Generation-217346?logo=openxml&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Local_Storage-003B57?logo=sqlite&logoColor=white)

<br>

## 🏗 Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                   MainWindow (PyQt5)                 │
│                    QMainWindow                      │
├──────────┬──────────────┬───────────────────────────┤
│ Connection│  SQL Query   │  Report Output            │
│  Dialogs  │   Editor     │  (Excel Export)           │
├──────────┴──────┬───────┴───────────────────────────┤
│                 ▼                                   │
│           ┌───────────┐                             │
│           │ DBManager │  ← psycopg2 → PostgreSQL    │
│           │  (Core)   │  ← sqlite3 → Config Local   │
│           └─────┬─────┘                             │
│                 ▼                                   │
│     ┌────────────────────┐                          │
│     │ ReportGenerator    │  → pandas + openpyxl     │
│     └────────────────────┘     → .xlsx files        │
└─────────────────────────────────────────────────────┘
```

<br>

## 📦 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- PostgreSQL acessível (local ou remoto)

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/amonmelo/QueryFacil.git
cd QueryFacil

# 2. (Opcional) Crie um ambiente virtual
python -m venv venv

# Ative o ambiente
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute o aplicativo
python app_completo.py
```

<br>

## 🚀 Como Usar

### 1. Adicionar uma conexão

Clique em **Add Connection**, preencha os dados do banco e teste a conexão:

```
Host: 192.168.1.100
Port: 5432
Database: meu_banco
User: postgres
Password: ********
```

### 2. Executar uma query

Selecione a conexão no combo, escreva sua SQL e clique em **Execute Query**:

```sql
SELECT nome, cidade, uf
FROM tab_clientes
WHERE uf = 'CE'
ORDER BY nome;
```

### 3. Salvar query favorita

Após escrever uma query, clique em **Save Current Query** e dê um nome.

### 4. Exportar para Excel

Após executar um `SELECT`, preencha o nome do relatório e clique em **Export Last Query Results**. O arquivo será salvo em `relatorios_gerados/`.

<br>

## 🗺 Roadmap

| Recurso | Status |
|---------|--------|
| Syntax highlighting no editor SQL | 🔜 Planejado |
| Tabela de resultados com `QTableView` | 🔜 Planejado |
| Execução assíncrona (threading) | 🔜 Planejado |
| Exportação para CSV e PDF | 🔜 Planejado |
| Histórico de queries executadas | 🔜 Planejado |
| Dark mode | 💡 Ideia |
| Criptografia de senhas | 💡 Ideia |

<br>

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma issue ou enviar um pull request. Para começar:

1. Faça um fork do projeto
2. Crie uma branch com sua feature (`git checkout -b feature/minha-feature`)
3. Commit suas mudanças (`git commit -m 'feat: descrição da mudança'`)
4. Push para a branch (`git push origin feature/minha-feature`)
5. Abra um Pull Request

<br>

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

<br>

---

<div align="center">

Feito com ☕ e 🐍 por **amonmelo**

<a href="https://www.linkedin.com/in/amonmelo/">![LinkedIn](https://img.shields.io/badge/LinkedIn-amonmelo-0A66C2?logo=linkedin&logoColor=white)</a>
<a href="https://github.com/amonmelo">![GitHub](https://img.shields.io/badge/GitHub-amonmelo-181717?logo=github&logoColor=white)</a>

</div>
