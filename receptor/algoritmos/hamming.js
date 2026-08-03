/** Algoritmo de correccion Hamming generico (n, m). Port directo de hamming.py. */

import { AlgoritmoIntegridad, EstadoVerificacion } from "./contrato.js";

export const BITS_POR_CARACTER = 8;

/** El r mas chico que cumple m + r + 1 <= 2**r. */
export function calcularBitsParidad(m) {
  let r = 0;
  while (m + r + 1 > 2 ** r) {
    r += 1;
  }
  return r;
}

function esPotenciaDeDos(n) {
  return n > 0 && (n & (n - 1)) === 0;
}

/** Inserta bits de paridad par en las posiciones potencia de 2 (1, 2, 4, ...). */
export function codificarBloque(bitsDatos) {
  const m = bitsDatos.length;
  const r = calcularBitsParidad(m);
  const n = m + r;

  const bloque = new Array(n + 1).fill(""); // 1-indexado; bloque[0] no se usa
  let indiceDatos = 0;
  for (let pos = 1; pos <= n; pos += 1) {
    if (esPotenciaDeDos(pos)) {
      bloque[pos] = "0";
    } else {
      bloque[pos] = bitsDatos[indiceDatos];
      indiceDatos += 1;
    }
  }

  for (let i = 0; i < r; i += 1) {
    const posParidad = 2 ** i;
    let paridad = 0;
    for (let pos = 1; pos <= n; pos += 1) {
      if (pos !== posParidad && (pos & posParidad) !== 0) {
        paridad ^= Number(bloque[pos]);
      }
    }
    bloque[posParidad] = String(paridad);
  }

  return bloque.slice(1).join("");
}

/** Recalcula el sindrome. Devuelve [bitsDatos, posicionError]; 0 = sin error. */
export function decodificarBloque(bloque) {
  const n = bloque.length;
  let r = 0;
  while (2 ** r < n + 1) {
    r += 1;
  }

  const b = [""].concat(bloque.split(""));
  let sindrome = 0;
  for (let i = 0; i < r; i += 1) {
    const posParidad = 2 ** i;
    let paridad = 0;
    for (let pos = 1; pos <= n; pos += 1) {
      if ((pos & posParidad) !== 0) {
        paridad ^= Number(b[pos]);
      }
    }
    if (paridad !== 0) {
      sindrome += posParidad;
    }
  }

  if (sindrome > 0 && sindrome <= n) {
    b[sindrome] = b[sindrome] === "0" ? "1" : "0";
  }

  const posicionesParidad = new Set(Array.from({ length: r }, (_, i) => 2 ** i));
  let bitsDatos = "";
  for (let pos = 1; pos <= n; pos += 1) {
    if (!posicionesParidad.has(pos)) {
      bitsDatos += b[pos];
    }
  }
  return [bitsDatos, sindrome];
}

export class Hamming extends AlgoritmoIntegridad {
  nombre = "hamming";

  constructor(m = 8) {
    super();
    if (!Number.isInteger(m) || m < 1) throw new Error("m debe ser mayor que cero");
    this.m = m;
  }

  calcular(bits) {
    const m = this.m;
    const bitsDatos = bits.length;
    bits += "0".repeat((m - (bits.length % m)) % m);
    const bloquesDatos = [];
    for (let i = 0; i < bits.length; i += m) {
      bloquesDatos.push(bits.slice(i, i + m));
    }
    const trama = bloquesDatos.map(codificarBloque).join("");
    return { bits: trama, parametros: { m, bloques: bloquesDatos.length, bits_datos: bitsDatos } };
  }

  verificar(trama, parametros) {
    const m = parametros.m;
    const n = m + calcularBitsParidad(m);

    const bloques = [];
    for (let i = 0; i < trama.length; i += n) {
      bloques.push(trama.slice(i, i + n));
    }

    const bitsDatos = [];
    const correcciones = [];
    bloques.forEach((bloque, indice) => {
      const [datos, posicionError] = decodificarBloque(bloque);
      bitsDatos.push(datos);
      if (posicionError !== 0) {
        correcciones.push(`bloque ${indice}: bit ${posicionError} corregido`);
      }
    });

    const estado = correcciones.length > 0 ? EstadoVerificacion.CORREGIDO : EstadoVerificacion.SIN_ERROR;
    const detalle = correcciones.length > 0 ? correcciones.join("; ") : "sin errores detectados";

    return { estado, bits: bitsDatos.join("").slice(0, parametros.bits_datos ?? bitsDatos.join("").length), detalle };
  }
}
