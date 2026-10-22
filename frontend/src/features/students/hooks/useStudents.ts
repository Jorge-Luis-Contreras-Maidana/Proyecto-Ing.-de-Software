import { useCallback, useEffect, useState } from 'react';
import { obtenerDetalleError } from '../../../shared/api/errorMapper';
import {
  listarEstudiantes,
  listarObservaciones,
  obtenerEstudiante,
} from '../api/studentsApi';
import type {
  Curso,
  Estudiante,
  EstudianteDetalle,
  FiltrosEstudiante,
  Observacion,
} from '../types/students.types';

export interface ResultadoEstudiantes {
  estudiantes: Estudiante[];
  total: number;
  pagina: number;
  porPagina: number;
  cargando: boolean;
  error: string | null;
  recargar: () => void;
}

/** Carga la lista de estudiantes con los filtros indicados. */
export function useEstudiantes(filtros: FiltrosEstudiante): ResultadoEstudiantes {
  const [estudiantes, setEstudiantes] = useState<Estudiante[]>([]);
  const [total, setTotal] = useState(0);
  const [pagina, setPagina] = useState(1);
  const [porPagina, setPorPagina] = useState(20);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [contador, setContador] = useState(0);

  const { q, id_curso, estado, page } = filtros;

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError(null);

    listarEstudiantes({ q, id_curso, estado, page })
      .then((respuesta) => {
        if (!vigente) {
          return;
        }
        setEstudiantes(respuesta.items);
        setTotal(respuesta.total);
        setPagina(respuesta.page);
        setPorPagina(respuesta.per_page);
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setEstudiantes([]);
          setTotal(0);
          setError(obtenerDetalleError(fallo).mensaje);
        }
      })
      .finally(() => {
        if (vigente) {
          setCargando(false);
        }
      });

    return () => {
      vigente = false;
    };
  }, [q, id_curso, estado, page, contador]);

  const recargar = useCallback(() => setContador((valor) => valor + 1), []);

  return { estudiantes, total, pagina, porPagina, cargando, error, recargar };
}

export interface ResultadoEstudiante {
  estudiante: EstudianteDetalle | null;
  observaciones: Observacion[];
  cargando: boolean;
  error: string | null;
  recargar: () => void;
}

/** Carga el detalle de un estudiante y sus observaciones. */
export function useEstudiante(idEstudiante: number | null): ResultadoEstudiante {
  const [estudiante, setEstudiante] = useState<EstudianteDetalle | null>(null);
  const [observaciones, setObservaciones] = useState<Observacion[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [contador, setContador] = useState(0);

  useEffect(() => {
    if (idEstudiante === null) {
      setEstudiante(null);
      setObservaciones([]);
      return;
    }

    let vigente = true;
    setCargando(true);
    setError(null);

    Promise.all([obtenerEstudiante(idEstudiante), listarObservaciones(idEstudiante)])
      .then(([detalle, listaObservaciones]) => {
        if (!vigente) {
          return;
        }
        setEstudiante(detalle);
        setObservaciones(listaObservaciones.items);
      })
      .catch((fallo: unknown) => {
        if (vigente) {
          setEstudiante(null);
          setObservaciones([]);
          setError(obtenerDetalleError(fallo).mensaje);
        }
      })
      .finally(() => {
        if (vigente) {
          setCargando(false);
        }
      });

    return () => {
      vigente = false;
    };
  }, [idEstudiante, contador]);

  const recargar = useCallback(() => setContador((valor) => valor + 1), []);

  return { estudiante, observaciones, cargando, error, recargar };
}

/**
 * Cursos existentes en la unidad educativa.
 * El API no expone un catálogo de cursos, así que se arma con los estudiantes
 * que devuelve el listado.
 */
export function useCursosDisponibles(): Curso[] {
  const [cursos, setCursos] = useState<Curso[]>([]);

  useEffect(() => {
    let vigente = true;

    listarEstudiantes({ estado: 'todos', page: 1, per_page: 50 })
      .then((respuesta) => {
        if (!vigente) {
          return;
        }
        const unicos = new Map<number, Curso>();
        respuesta.items.forEach((estudiante) => {
          if (estudiante.curso) {
            unicos.set(estudiante.curso.id_curso, estudiante.curso);
          }
        });
        setCursos(
          Array.from(unicos.values()).sort((a, b) =>
            `${a.nivel} ${a.grado}${a.paralelo}`.localeCompare(`${b.nivel} ${b.grado}${b.paralelo}`)
          )
        );
      })
      .catch(() => {
        if (vigente) {
          setCursos([]);
        }
      });

    return () => {
      vigente = false;
    };
  }, []);

  return cursos;
}
