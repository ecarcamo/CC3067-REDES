/** Capa de aplicacion: logica del banco (cuentas, validaciones, respuestas). */

// "Base de datos" en memoria: tarjeta -> { pin, balance }
export const CUENTAS = {
  "4111111111111111": { pin: "1234", balance: 500.0 },
  "5500005555555559": { pin: "0000", balance: 1200.5 },
  23016: { pin: "123456789", balance: 400 },
};

/** @typedef {{ tarjeta: string|null }} Sesion */

/**
 * Procesa un mensaje de aplicacion (login/withdraw/logout) y devuelve la respuesta.
 * @param {{action: string, data: Object}} mensaje
 * @param {Sesion} sesion
 * @returns {{action: string, data: Object}}
 */
export function manejarAccion(mensaje, sesion) {
  const { action, data = {} } = mensaje;

  if (action === "login") {
    const cuenta = CUENTAS[data.card];
    if (cuenta && cuenta.pin === data.pin) {
      sesion.tarjeta = data.card;
      return { action: "login_ok", data: { message: "Autenticacion exitosa" } };
    }
    return { action: "login_denied", data: { message: "Tarjeta o PIN invalido" } };
  }

  if (action === "withdraw") {
    if (!sesion.tarjeta) {
      return { action: "error", data: { message: "No autenticado" } };
    }

    const cuenta = CUENTAS[sesion.tarjeta];
    const monto = data.amount ?? 0;

    if (monto <= 0) {
      return { action: "error", data: { message: "Monto invalido" } };
    }
    if (monto > cuenta.balance) {
      return { action: "error", data: { message: "Fondos insuficientes" } };
    }

    cuenta.balance -= monto;
    return { action: "withdraw_ok", data: { amount: monto, balance: cuenta.balance } };
  }

  if (action === "logout") {
    return { action: "logout_ok", data: { message: "Hasta luego" } };
  }

  return { action: "error", data: { message: "Accion desconocida" } };
}
