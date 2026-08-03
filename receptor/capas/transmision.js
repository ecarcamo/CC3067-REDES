/** Capa de transmision: serializa/deserializa el sobre JSON sobre el socket TCP. Sin capa de ruido. */

/** Acumula fragmentos hasta encontrar '\n', porque TCP puede partir o pegar mensajes. */
export class LectorLineas {
  constructor() {
    this._buffer = "";
  }

  /** @param {string} fragmento */
  agregar(fragmento) {
    this._buffer += fragmento;
  }

  /** @returns {Generator<string>} lineas completas disponibles en el buffer, en orden */
  *extraerLineas() {
    let indice = this._buffer.indexOf("\n");
    while (indice !== -1) {
      yield this._buffer.slice(0, indice);
      this._buffer = this._buffer.slice(indice + 1);
      indice = this._buffer.indexOf("\n");
    }
  }
}

/** @param {import("node:net").Socket} conn @param {string} trama @param {string} algoritmo @param {Object} parametros */
export function enviarInformacion(conn, trama, algoritmo, parametros) {
  const sobre = { version: 1, algoritmo, parametros, trama };
  conn.write(`${JSON.stringify(sobre)}\n`);
}

/** @param {string} linea @returns {Object} */
export function recibirInformacion(linea) {
  let sobre;
  try { sobre = JSON.parse(linea); } catch { throw new Error("sobre JSON invalido"); }
  if (!sobre || sobre.version !== 1) throw new Error("version de sobre no soportada");
  if (typeof sobre.algoritmo !== "string" || typeof sobre.parametros !== "object") throw new Error("campos basicos del sobre invalidos");
  if (typeof sobre.trama !== "string" || /[^01]/.test(sobre.trama)) throw new Error("trama debe ser una cadena binaria");
  return sobre;
}
