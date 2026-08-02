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
  return JSON.parse(linea);
}
