# Análise da elasticidade de preços de e-commerces brasileiros

Para rodar o projeto você deve instalar os pacotes definidos no `requirements.txt`,
```bash
pip install -r requirements.txt
```

Esse projeto utiliza um banco de dados PotgreSQL para armazenamento dos resultados do scrape. Para isso você deve instalar o software e criar uma banco com nome `ecommerce`, criar um usuário e dar permissões de criação e modificação de schema para ele. Você também pode adicionar o usuário como criador do banco.

Para o script criar a tabela automaticamente você também deve criar um arquivo `.env` com usuário e senha para logar no banco. O arquivo deve ter as variáveis:
```
# .env
USR= <coloque um usuario>
PASSWORD= <coloque uma senha>
```

Depois disso basta executar o script de ETL com python:
```bash
python etl.py
```
que toda a raspagem e armazenamento serão feitos automaticamente. Caso você deseje fazer um scrape específico de algum sites, ou não armazenar em um banco, você pode olhar as funções definidas em `scrappers.py`.