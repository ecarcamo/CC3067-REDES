/** Algoritmo de deteccion CRC-32 (IEEE 802.3). Implementacion pendiente (Hito 1). */

import { AlgoritmoIntegridad } from "./contrato.js";

export class Crc32 extends AlgoritmoIntegridad {
  nombre = "crc32";

  calcular(bits) {
    throw new Error("no implementado");
  }

  verificar(trama, parametros) {
    throw new Error("no implementado");
  }
}
