/** Algoritmo de deteccion CRC-32 (IEEE 802.3, polinomio reflejado 0xEDB88320). Port directo de crc32.py. */

import { AlgoritmoIntegridad, EstadoVerificacion } from "./contrato.js";

export const POLINOMIO_REFLEJADO = 0xedb88320;
export const VALOR_INICIAL = 0xffffffff;
export const BITS_POR_BYTE = 8;
export const BITS_CHECKSUM = 32;

function bitsABytes(bits) {
  const bytes = [];
  for (let i = 0; i < bits.length; i += BITS_POR_BYTE) {
    bytes.push(parseInt(bits.slice(i, i + BITS_POR_BYTE), 2));
  }
  return bytes;
}

/** CRC-32 reflejado (mismo algoritmo que Ethernet FCS / zlib.crc32), bit a bit. */
export function calcularCrc(bitsDatos) {
  let crc = VALOR_INICIAL;
  for (const byte of bitsABytes(bitsDatos)) {
    crc ^= byte;
    for (let i = 0; i < BITS_POR_BYTE; i += 1) {
      if (crc & 1) {
        crc = (crc >>> 1) ^ POLINOMIO_REFLEJADO;
      } else {
        crc = crc >>> 1;
      }
    }
  }
  return (crc ^ VALOR_INICIAL) >>> 0;
}

export class Crc32 extends AlgoritmoIntegridad {
  nombre = "crc32";

  calcular(bits) {
    const checksum = calcularCrc(bits);
    const trama = bits + checksum.toString(2).padStart(BITS_CHECKSUM, "0");
    return { bits: trama, parametros: { bits_datos: bits.length } };
  }

  verificar(trama, parametros) {
    const n = parametros.bits_datos;
    const bitsDatos = trama.slice(0, n);
    const checksumRecibido = trama.slice(n);
    const checksumCalculado = calcularCrc(bitsDatos).toString(2).padStart(BITS_CHECKSUM, "0");

    if (checksumCalculado === checksumRecibido) {
      return { estado: EstadoVerificacion.SIN_ERROR, bits: bitsDatos, detalle: "checksum coincide" };
    }

    return {
      estado: EstadoVerificacion.ERROR_NO_CORREGIBLE,
      bits: null,
      detalle: "checksum no coincide: la trama llego corrupta",
    };
  }
}
