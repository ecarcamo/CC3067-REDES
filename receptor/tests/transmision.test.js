import test from "node:test";
import assert from "node:assert/strict";
import { LectorLineas, recibirInformacion } from "../capas/transmision.js";

test("reconstruye fragmentos y separa lineas pegadas", () => {
  const lector = new LectorLineas();
  lector.agregar("uno"); assert.deepEqual([...lector.extraerLineas()], []);
  lector.agregar("\ndos\n"); assert.deepEqual([...lector.extraerLineas()], ["uno", "dos"]);
  lector.agregar("incompleta"); assert.deepEqual([...lector.extraerLineas()], []);
});

test("valida version, trama y JSON", () => {
  assert.throws(() => recibirInformacion("{"), /JSON invalido/);
  assert.throws(() => recibirInformacion('{"version":2}'), /version/);
  assert.throws(() => recibirInformacion('{"version":1,"algoritmo":"crc32","parametros":{},"trama":"2"}'), /binaria/);
});
