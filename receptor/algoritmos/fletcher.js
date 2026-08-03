/** Checksum Fletcher configurable para palabras de 8, 16 o 32 bits. */
import { AlgoritmoIntegridad, EstadoVerificacion } from "./contrato.js";

export class Fletcher extends AlgoritmoIntegridad {
  constructor(tamanoBloque = 16) {
    super();
    if (![8, 16, 32].includes(tamanoBloque)) throw new Error("tamano_bloque debe ser 8, 16 o 32");
    this.tamanoBloque = tamanoBloque;
  }

  static checksum(bits, tamano) {
    const modulo = (1n << BigInt(tamano)) - 1n;
    let suma1 = 0n;
    let suma2 = 0n;
    for (let i = 0; i < bits.length; i += tamano) {
      suma1 = (suma1 + BigInt(`0b${bits.slice(i, i + tamano)}`)) % modulo;
      suma2 = (suma2 + suma1) % modulo;
    }
    return (suma2 << BigInt(tamano)) | suma1;
  }

  calcular(bits) {
    const relleno = (this.tamanoBloque - (bits.length % this.tamanoBloque)) % this.tamanoBloque;
    const datos = bits + "0".repeat(relleno);
    const checksum = Fletcher.checksum(datos, this.tamanoBloque).toString(2).padStart(2 * this.tamanoBloque, "0");
    return { bits: datos + checksum, parametros: { tamano_bloque: this.tamanoBloque, bits_datos: bits.length } };
  }

  verificar(trama, parametros) {
    const tamano = parametros.tamano_bloque;
    const longitud = parametros.bits_datos + (tamano - (parametros.bits_datos % tamano)) % tamano;
    const datos = trama.slice(0, longitud);
    const esperado = Fletcher.checksum(datos, tamano).toString(2).padStart(2 * tamano, "0");
    if (trama.slice(longitud) === esperado) {
      return { estado: EstadoVerificacion.SIN_ERROR, bits: datos.slice(0, parametros.bits_datos), detalle: "checksum coincide" };
    }
    return { estado: EstadoVerificacion.ERROR_NO_CORREGIBLE, bits: null, detalle: "checksum Fletcher no coincide" };
  }
}
