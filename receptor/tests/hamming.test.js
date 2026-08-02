import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import test from "node:test";
import assert from "node:assert/strict";

import { Hamming, calcularBitsParidad, codificarBloque, decodificarBloque } from "../algoritmos/hamming.js";
import { EstadoVerificacion } from "../algoritmos/contrato.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rutaVectores = path.join(__dirname, "..", "..", "docs", "vectores.json");

function cargarVectores() {
  return JSON.parse(readFileSync(rutaVectores, "utf-8")).hamming;
}

test("calcularBitsParidad para un caracter ASCII", () => {
  assert.equal(calcularBitsParidad(8), 4);
});

test("codificar y decodificar sin error recupera bits identicos", () => {
  const bitsDatos = "01000001"; // 'A'
  const trama = codificarBloque(bitsDatos);
  const [recuperado, posicionError] = decodificarBloque(trama);
  assert.equal(recuperado, bitsDatos);
  assert.equal(posicionError, 0);
});

test("voltear un bit en cada posicion siempre corrige", () => {
  const bitsDatos = "01000001";
  const trama = codificarBloque(bitsDatos);
  for (let posicion = 0; posicion < trama.length; posicion += 1) {
    const tramaConError = trama.split("");
    tramaConError[posicion] = tramaConError[posicion] === "0" ? "1" : "0";
    const [recuperado, posicionError] = decodificarBloque(tramaConError.join(""));
    assert.equal(recuperado, bitsDatos);
    assert.equal(posicionError, posicion + 1);
  }
});

test("voltear dos bits no garantiza el resultado correcto", () => {
  const bitsDatos = "01000001";
  const trama = codificarBloque(bitsDatos).split("");
  trama[0] = trama[0] === "0" ? "1" : "0";
  trama[1] = trama[1] === "0" ? "1" : "0";
  const [recuperado] = decodificarBloque(trama.join(""));
  assert.notEqual(recuperado, bitsDatos);
});

test("mensaje de varios caracteres procesa todos los bloques", () => {
  const hamming = new Hamming();
  const bits = [..."Hola"].map((c) => c.charCodeAt(0).toString(2).padStart(8, "0")).join("");
  const tramaCodificada = hamming.calcular(bits);
  assert.equal(tramaCodificada.parametros.bloques, 4);

  const resultado = hamming.verificar(tramaCodificada.bits, tramaCodificada.parametros);
  assert.equal(resultado.estado, EstadoVerificacion.SIN_ERROR);
  assert.equal(resultado.bits, bits);
});

test("vectores compartidos", () => {
  const hamming = new Hamming();
  for (const vector of cargarVectores()) {
    const resultado = hamming.verificar(vector.trama_recibida, vector.parametros);
    assert.equal(resultado.estado, vector.estado_esperado, vector.descripcion);
    assert.equal(resultado.bits, vector.bits_esperados, vector.descripcion);
  }
});
