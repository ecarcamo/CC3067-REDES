/** Mapea el nombre de un algoritmo (string del protocolo) a su instancia. */

import { Crc32 } from "./crc32.js";
import { Hamming } from "./hamming.js";

const ALGORITMOS = {
  hamming: new Hamming(),
  crc32: new Crc32(),
};

/** @param {string} nombre @returns {import("./contrato.js").AlgoritmoIntegridad} */
export function obtenerAlgoritmo(nombre) {
  const algoritmo = ALGORITMOS[nombre];
  if (!algoritmo) {
    throw new Error(`Algoritmo desconocido: ${nombre}`);
  }
  return algoritmo;
}
