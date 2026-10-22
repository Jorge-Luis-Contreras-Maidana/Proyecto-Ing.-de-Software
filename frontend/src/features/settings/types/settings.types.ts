/** Parámetros de la configuración de asistencia de la unidad educativa. */
export interface ConfiguracionAsistencia {
  id_configuracion: number;
  id_unidad: number;
  tolerancia_ingreso_min: number;
  limite_tardanza_min: number;
  ausencias_consecutivas_alerta: number;
  tardanzas_mes_alerta: number;
  porcentaje_ausencia_alerta: number;
  plazo_justificacion_dias: number;
  actualizado_en: string | null;
  actualizado_por: number | null;
}

/** Datos para modificar los parámetros de asistencia. */
export interface CambiosConfiguracion {
  tolerancia_ingreso_min?: number;
  limite_tardanza_min?: number;
  ausencias_consecutivas_alerta?: number;
  tardanzas_mes_alerta?: number;
  porcentaje_ausencia_alerta?: number;
  plazo_justificacion_dias?: number;
}
