/** Capa de presentacion: texto <-> bits ASCII. */

export const BITS_POR_CARACTER = 8;
const LIMITE_ASCII = 128;

/** @param {string} texto @returns {string} */
export function codificarMensaje(texto) {
  for (const caracter of texto) {
    if (caracter.charCodeAt(0) >= LIMITE_ASCII) {
      throw new Error(`caracter no ASCII: ${caracter}`);
    }
  }
  return [...texto].map((c) => c.charCodeAt(0).toString(2).padStart(BITS_POR_CARACTER, "0")).join("");
}

/** @param {string} bits @returns {string} */
export function decodificarMensaje(bits) {
  if (bits.length % BITS_POR_CARACTER !== 0) {
    throw new Error("la longitud de bits debe ser multiplo de 8");
  }
  let texto = "";
  for (let i = 0; i < bits.length; i += BITS_POR_CARACTER) {
    texto += String.fromCharCode(parseInt(bits.slice(i, i + BITS_POR_CARACTER), 2));
  }
  return texto;
}
