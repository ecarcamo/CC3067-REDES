/** Servidor bancario (receptor). Hito 0: solo conecta y responde a un string de prueba. */

import net from "node:net";

const HOST = "127.0.0.1";
const PORT = 2705;

const server = net.createServer((conn) => {
  console.log("[RECEPTOR] Conexion entrante");

  conn.on("data", (data) => {
    const mensaje = data.toString("utf-8").trim();
    console.log(`[RECEPTOR] Recibido: ${mensaje}`);
    conn.write("hola cajero\n");
  });

  conn.on("end", () => {
    console.log("[RECEPTOR] Cliente desconectado");
  });
});

server.listen(PORT, HOST, () => {
  console.log(`[RECEPTOR] Escuchando en ${HOST}:${PORT} ...`);
});
