/** Capa de enlace: calcula y verifica la integridad delegando en el algoritmo del registro. */

import { obtenerAlgoritmo } from "../algoritmos/registro.js";

/** @param {string} bits @param {string} nombreAlgoritmo @returns {import("../algoritmos/contrato.js").TramaCodificada} */
export function calcularIntegridad(bits, nombreAlgoritmo, configuracion = {}) {
  return obtenerAlgoritmo(nombreAlgoritmo, configuracion).calcular(bits);
}

/** @param {string} trama @param {string} nombreAlgoritmo @param {Object} parametros @returns {import("../algoritmos/contrato.js").ResultadoVerificacion} */
export function verificarIntegridad(trama, nombreAlgoritmo, parametros) {
  return obtenerAlgoritmo(nombreAlgoritmo).verificar(trama, parametros);
}
