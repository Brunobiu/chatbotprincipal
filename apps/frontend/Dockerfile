# Dockerfile do Frontend Next.js
# TODO: Versão do Node.js - você pode atualizar para uma versão mais recente se necessário
FROM node:20-alpine

WORKDIR /app

# TODO: Configuração de variáveis de ambiente para build
# Estas variáveis são necessárias durante o build do Next.js
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Copiar arquivos de dependências
COPY package*.json ./

# Instalar dependências
# TODO: Adicionar --production se quiser ignorar devDependencies em produção
RUN npm install

# Copiar todo o código
COPY . .
COPY components ./components
COPY app ./app
COPY public ./public

# Build da aplicação
# TODO: O build pode demorar alguns minutos na primeira vez
RUN npm run build

# Expor porta 3000 (padrão do Next.js)
EXPOSE 3000

# TODO: Ajustar configuração de host se necessário
ENV HOSTNAME="0.0.0.0"

# Comando para iniciar
# TODO: 'start' inicia em modo produção. Use 'dev' apenas para desenvolvimento local
CMD ["npm", "start"]
