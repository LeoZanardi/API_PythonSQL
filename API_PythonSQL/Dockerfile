# Usa a imagem oficial do Python
FROM python:3.9

# Define o diretório de trabalho no container
WORKDIR /app

# Copia os arquivos do projeto
COPY requirements.txt .

# Instala as dependências do Flask e do MySQL Connector
RUN pip install --no-cache-dir -r requirements.txt

# Copia os arquivos restantes
COPY . .

# Expõe a porta 5001
EXPOSE 5001

# Comando para iniciar a aplicação
CMD ["python", "app.py"]
