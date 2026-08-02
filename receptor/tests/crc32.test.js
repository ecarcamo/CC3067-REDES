import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import zlib from "node:zlib";
import test from "node:test";
import assert from "node:assert/strict";

import { Crc32, calcularCrc } from "../algoritmos/crc32.js";
import { EstadoVerificacion } from "../algoritmos/contrato.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rutaVectores = path.join(__dirname, "..", "..", "docs", "vectores.json");

function cargarVectores() {
  return JSON.parse(readFileSync(rutaVectores, "utf-8")).crc32;
}

function textoABits(texto) {
  return [...texto].map((c) => c.charCodeAt(0).toString(2).padStart(8, "0")).join("");
}

test("calcularCrc coincide con zlib.crc32", () => {
  const bits = textoABits("Hola");
  const esperado = zlib.crc32(Buffer.from("Hola", "ascii"));
  assert.equal(calcularCrc(bits), esperado);
});

test("codificar y verificar sin error recupera bits identicos", () => {
  const crc32 = new Crc32();
  const bits = textoABits("Hola");
  const tramaCodificada = crc32.calcular(bits);

  const resultado = crc32.verificar(tramaCodificada.bits, tramaCodificada.parametros);
  assert.equal(resultado.estado, EstadoVerificacion.SIN_ERROR);
  assert.equal(resultado.bits, bits);
});

test("bit alterado se detecta como error no corregible", () => {
  const crc32 = new Crc32();
  const bits = textoABits("Hola");
  const tramaCodificada = crc32.calcular(bits);

  const tramaConError = tramaCodificada.bits.split("");
  tramaConError[0] = tramaConError[0] === "0" ? "1" : "0";

  const resultado = crc32.verificar(tramaConError.join(""), tramaCodificada.parametros);
  assert.equal(resultado.estado, EstadoVerificacion.ERROR_NO_CORREGIBLE);
  assert.equal(resultado.bits, null);
});

test("crc nunca devuelve corregido", () => {
  const crc32 = new Crc32();
  const bits = textoABits("X");
  const tramaCodificada = crc32.calcular(bits);

  const tramaConError = tramaCodificada.bits.split("");
  tramaConError[3] = tramaConError[3] === "0" ? "1" : "0";
  const resultado = crc32.verificar(tramaConError.join(""), tramaCodificada.parametros);

  assert.notEqual(resultado.estado, EstadoVerificacion.CORREGIDO);
});

test("vectores compartidos", () => {
  const crc32 = new Crc32();
  for (const vector of cargarVectores()) {
    const resultado = crc32.verificar(vector.trama_recibida, vector.parametros);
    assert.equal(resultado.estado, vector.estado_esperado, vector.descripcion);
    if (vector.estado_esperado === "sin_error") {
      assert.equal(resultado.bits, vector.bits_esperados, vector.descripcion);
    }
  }
});
