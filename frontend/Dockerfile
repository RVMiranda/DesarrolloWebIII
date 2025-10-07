FROM node:20-alpine

WORKDIR /app

# Instala dependencias primero para aprovechar caché
COPY package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copia el resto del código
COPY . .

# Vite servirá en el 3000 (dev server)
EXPOSE 3000

# Ejecuta Vite en modo dev, escuchando en todas las interfaces y puerto 3000
CMD ["npm","run","dev","--","--host","0.0.0.0","--port","3000"]
