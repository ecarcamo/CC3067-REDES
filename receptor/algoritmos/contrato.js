/**
 * Contrato que debe cumplir todo algoritmo de integridad (corrección o detección).
 * Espejo exacto de emisor/algoritmos/contrato.py: mismos estados y mismas llaves.
 */

export const EstadoVerificacion = Object.freeze({
  SIN_ERROR: "sin_error",
  CORREGIDO: "corregido",
  ERROR_NO_CORREGIBLE: "error_no_corregible",
});

/**
 * @typedef {Object} TramaCodificada
 * @property {string} bits - trama completa: datos + redundancia
 * @property {Object} parametros - info que el receptor necesita para decodificar
 */

/**
 * @typedef {Object} ResultadoVerificacion
 * @property {string} estado - uno de EstadoVerificacion
 * @property {string|null} bits - bits de datos originales, o null si no se pudo recuperar
 * @property {string} detalle - texto legible
 */

/**
 * Interfaz que debe implementar cada algoritmo: { nombre, calcular(bits), verificar(trama, parametros) }.
 */
export class AlgoritmoIntegridad {
  /** @param {string} bits @returns {TramaCodificada} */
  calcular(bits) {
    throw new Error("no implementado");
  }

  /** @param {string} trama @param {Object} parametros @returns {ResultadoVerificacion} */
  verificar(trama, parametros) {
    throw new Error("no implementado");
  }
}
