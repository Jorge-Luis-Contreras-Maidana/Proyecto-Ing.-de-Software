"""Mensajes de error: cada uno indica la causa y la acción a seguir. RNF-03.3."""

MESSAGES: dict[str, tuple[str, str]] = {
    "credenciales_invalidas": (
        "El usuario o la contraseña son incorrectos.",
        "Revise los datos e intente nuevamente.",
    ),
    "cuenta_inactiva": (
        "Su cuenta está inactiva o bloqueada.",
        "Comuníquese con la dirección de la unidad educativa.",
    ),
    "sin_rol": (
        "Su cuenta no tiene un rol asignado.",
        "Solicite a la dirección que le asigne un rol.",
    ),
    "no_autenticado": (
        "Debe iniciar sesión para continuar.",
        "Ingrese con su usuario y contraseña.",
    ),
    "token_invalido": (
        "Su sesión no es válida.",
        "Inicie sesión nuevamente.",
    ),
    "sesion_expirada": (
        "Su sesión se cerró por inactividad.",
        "Inicie sesión nuevamente.",
    ),
    "sesion_cerrada": (
        "Su sesión ya fue cerrada.",
        "Inicie sesión nuevamente.",
    ),
    "sin_permiso": (
        "No tiene permiso para realizar esta acción.",
        "Si cree que es un error, comuníquese con la dirección.",
    ),
    "datos_invalidos": (
        "Los datos enviados no son válidos.",
        "Revise la información ingresada e intente nuevamente.",
    ),
    "no_encontrado": (
        "No se encontró lo que busca.",
        "Verifique la dirección o regrese al inicio.",
    ),
    "metodo_no_permitido": (
        "La operación no está permitida.",
        "Regrese al inicio e intente de nuevo.",
    ),
    "solicitud_demasiado_grande": (
        "La información enviada es demasiado grande (máximo 100 KB).",
        "Reduzca el tamaño e intente nuevamente.",
    ),
    "error_interno": (
        "Ocurrió un error inesperado en el sistema.",
        "Intente nuevamente en unos minutos. Si persiste, avise al administrador.",
    ),
        "registro_duplicado": (
        "Ya existe un registro con esos datos.",
        "Verifique los datos e intente nuevamente.",
    ),
}