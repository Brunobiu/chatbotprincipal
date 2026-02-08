# Dockerfile do Frontend Next.js
FROM node:20-alpine

WORKDIR /app

# Configuração de variáveis de ambiente para build
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Copiar arquivos de dependências
COPY package*.json ./

# Instalar dependências
RUN npm install

# Copiar todo o código
COPY . .

# Build da aplicação
RUN npm run build

# Expor porta 3000 (padrão do Next.js)
EXPOSE 3000

ENV HOSTNAME="0.0.0.0"

# Comando para iniciar
CMD ["npm", "start"]
