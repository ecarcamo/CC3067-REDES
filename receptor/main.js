/** Servidor bancario (receptor). Orquesta: transmision -> enlace -> presentacion -> aplicacion. */

import net from "node:net";

import { EstadoVerificacion } from "./algoritmos/contrato.js";
import { manejarAccion } from "./capas/aplicacion.js";
import { calcularIntegridad, verificarIntegridad } from "./capas/enlace.js";
import { codificarMensaje, decodificarMensaje } from "./capas/presentacion.js";
import { LectorLineas, enviarInformacion, recibirInformacion } from "./capas/transmision.js";

const HOST = "127.0.0.1";
const PORT = 2705;

function enviarRespuesta(conn, mensaje, algoritmo) {
  const bits = codificarMensaje(JSON.stringify(mensaje));
  const tramaCodificada = calcularIntegridad(bits, algoritmo);
  enviarInformacion(conn, tramaCodificada.bits, algoritmo, tramaCodificada.parametros);
}

function procesarLinea(conn, linea, sesion) {
  const sobre = recibirInformacion(linea);
  const resultado = verificarIntegridad(sobre.trama, sobre.algoritmo, sobre.parametros);

  if (resultado.bits === null) {
    console.log(`[RECEPTOR] Trama corrupta: ${resultado.detalle}`);
    enviarRespuesta(conn, { action: "error", data: { message: `Trama corrupta: ${resultado.detalle}` } }, sobre.algoritmo);
    return true;
  }

  if (resultado.estado === EstadoVerificacion.CORREGIDO) {
    console.log(`[RECEPTOR] Se corrigio un error de transmision: ${resultado.detalle}`);
  }

  let mensaje;
  try {
    mensaje = JSON.parse(decodificarMensaje(resultado.bits));
  } catch (error) {
    // Falso negativo: el algoritmo reporto sin_error/corregido pero el mensaje
    // decodificado no es valido (limitacion conocida de Hamming con errores dobles).
    console.log(`[RECEPTOR] Mensaje irrecuperable pese a estado=${resultado.estado}: ${error.message}`);
    enviarRespuesta(conn, { action: "error", data: { message: "Mensaje corrupto" } }, sobre.algoritmo);
    return true;
  }
  console.log(`[RECEPTOR] Recibido: ${JSON.stringify(mensaje)}`);

  const respuesta = manejarAccion(mensaje, sesion);
  enviarRespuesta(conn, respuesta, sobre.algoritmo);

  return respuesta.action !== "logout_ok";
}

const server = net.createServer((conn) => {
  console.log("[RECEPTOR] Conexion entrante");
  const lector = new LectorLineas();
  const sesion = { tarjeta: null };

  conn.on("data", (datos) => {
    lector.agregar(datos.toString("utf-8"));
    for (const linea of lector.extraerLineas()) {
      const continuar = procesarLinea(conn, linea, sesion);
      if (!continuar) {
        conn.end();
      }
    }
  });

  conn.on("end", () => {
    console.log("[RECEPTOR] Cliente desconectado");
  });
});

server.listen(PORT, HOST, () => {
  console.log(`[RECEPTOR] Escuchando en ${HOST}:${PORT} ...`);
});
