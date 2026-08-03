/** Mapea el nombre de un algoritmo (string del protocolo) a su instancia. */

import { Crc32 } from "./crc32.js";
import { Fletcher } from "./fletcher.js";
import { Hamming } from "./hamming.js";

const ALGORITMOS = {
  hamming: new Hamming(),
  crc32: new Crc32(),
  fletcher: new Fletcher(),
};

/** @param {string} nombre @returns {import("./contrato.js").AlgoritmoIntegridad} */
export function obtenerAlgoritmo(nombre, configuracion = {}) {
  if (nombre === "hamming" && configuracion.m) return new Hamming(configuracion.m);
  if (nombre === "fletcher" && configuracion.tamano_bloque) return new Fletcher(configuracion.tamano_bloque);
  const algoritmo = ALGORITMOS[nombre];
  if (!algoritmo) {
    throw new Error(`Algoritmo desconocido: ${nombre}`);
  }
  return algoritmo;
}
