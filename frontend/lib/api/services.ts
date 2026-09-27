/**
 * frontend/lib/api/services.ts
 * Servicios tipados para consumir la API DUBSS.
 */
import api from "./client";

// ─── Tipos ────────────────────────────────────────────────────────────────────

export interface Usuario {
  id: number;
  email: string;
  nombre: string;
  apellido: string;
  nombre_completo: string;
  rol: "ADMIN_DUBSS" | "COORDINADOR" | "ARBITRO" | "DEPORTISTA" | "PUBLICO";
  facultad: string;
  foto_perfil?: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  usuario: Usuario;
}

export interface Campeonato {
  id: number;
  nombre: string;
  deporte: { id: number; nombre: string };
  categoria: { id: number; nombre: string; genero: string };
  estado: string;
  formato: string;
  fecha_inicio: string;
  fecha_fin: string;
  max_equipos: number;
}

export interface Partido {
  id: number;
  campeonato: number;
  equipo_local: { id: number; nombre: string; facultad: string };
  equipo_visitante: { id: number; nombre: string; facultad: string };
  cancha: { id: number; nombre: string };
  fecha_hora: string;
  jornada: number;
  fase: string;
  estado: string;
}

export interface TablaPosicion {
  equipo: { id: number; nombre: string; facultad: string };
  pj: number;
  pg: number;
  pe: number;
  pp: number;
  gf: number;
  gc: number;
  puntos: number;
  diferencia_goles: number;
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export const authService = {
  login: (email: string, password: string) =>
    api.post<LoginResponse>("/auth/login/", { email, password }),

  registro: (data: Record<string, unknown>) =>
    api.post("/auth/registro/", data),

  logout: (refresh: string) =>
    api.post("/auth/logout/", { refresh }),

  refreshToken: (refresh: string) =>
    api.post<{ access: string }>("/auth/token/refresh/", { refresh }),

  cambioPassword: (data: Record<string, string>) =>
    api.post("/auth/cambio-password/", data),

  miPerfil: () =>
    api.get<Usuario>("/usuarios/perfil/"),
};

// ─── Campeonatos ──────────────────────────────────────────────────────────────

export const campeonatoService = {
  listar: (params?: Record<string, unknown>) =>
    api.get<{ results: Campeonato[]; count: number }>("/deportes/campeonatos/", { params }),

  obtener: (id: number) =>
    api.get<Campeonato>(`/deportes/campeonatos/${id}/`),

  crear: (data: Partial<Campeonato>) =>
    api.post<Campeonato>("/deportes/campeonatos/", data),

  actualizar: (id: number, data: Partial<Campeonato>) =>
    api.patch<Campeonato>(`/deportes/campeonatos/${id}/`, data),

  equipos: (id: number) =>
    api.get(`/deportes/campeonatos/${id}/equipos/`),
};

// ─── Fixture ──────────────────────────────────────────────────────────────────

export const fixtureService = {
  generar: (campeonatoId: number, usarML = false) =>
    api.post(`/fixture/generar/`, { campeonato_id: campeonatoId, usar_ml: usarML }),

  partidos: (campeonatoId: number, params?: Record<string, unknown>) =>
    api.get<{ results: Partido[] }>("/fixture/partidos/", {
      params: { campeonato: campeonatoId, ...params },
    }),

  registrarResultado: (partidoId: number, data: Record<string, unknown>) =>
    api.post(`/fixture/partidos/${partidoId}/resultado/`, data),

  tablaPosiciones: (campeonatoId: number) =>
    api.get<TablaPosicion[]>(`/fixture/tabla-posiciones/`, {
      params: { campeonato: campeonatoId },
    }),
};

// ─── ML / Predicciones ────────────────────────────────────────────────────────

export const mlService = {
  predecirPartido: (partidoId: number) =>
    api.get(`/ml/prediccion-partido/${partidoId}/`),

  tableroPredicciones: (campeonatoId: number) =>
    api.get(`/ml/tablero/`, { params: { campeonato: campeonatoId } }),

  riesgoClimatico: (partidoId: number) =>
    api.get(`/ml/riesgo-climatico/${partidoId}/`),
};

// ─── Reportes ────────────────────────────────────────────────────────────────

export const reporteService = {
  exportarPDF: (campeonatoId: number) =>
    api.get(`/reportes/campeonato/${campeonatoId}/pdf/`, { responseType: "blob" }),

  exportarExcel: (campeonatoId: number) =>
    api.get(`/reportes/campeonato/${campeonatoId}/excel/`, { responseType: "blob" }),
};
