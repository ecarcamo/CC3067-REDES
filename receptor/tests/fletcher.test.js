import { readFileSync } from "node:fs";
import test from "node:test";
import assert from "node:assert/strict";
import { Fletcher } from "../algoritmos/fletcher.js";

const vectores = JSON.parse(readFileSync(new URL("../../docs/vectores.json", import.meta.url))).fletcher;

test("vectores Fletcher compartidos", () => {
  for (const vector of vectores) {
    const resultado = new Fletcher().verificar(vector.trama_recibida, vector.parametros);
    assert.equal(resultado.estado, vector.estado_esperado, vector.descripcion);
    assert.equal(resultado.bits, vector.bits_esperados, vector.descripcion);
  }
});

test("Fletcher detecta alteraciones en los tres tamanos", () => {
  for (const tamano of [8, 16, 32]) {
    const fletcher = new Fletcher(tamano);
    const codificada = fletcher.calcular("10101");
    const alterada = (codificada.bits[0] === "0" ? "1" : "0") + codificada.bits.slice(1);
    assert.equal(fletcher.verificar(alterada, codificada.parametros).estado, "error_no_corregible");
  }
});
