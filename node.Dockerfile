# Used only for local development
FROM node:lts-iron
WORKDIR /home/node
COPY esbuild.config.js package.json package-lock.json ./
COPY app/static/src app/static/src
RUN npm install
RUN npm run build
CMD ["node", "esbuild.config.js", "--watch"]
