"use client";
import { useState, useEffect } from "react";
import Cookies from "js-cookie";
import { jwtDecode } from "jwt-decode";
import api from "@/lib/api/client";

interface JwtPayload {
  user_id: number;
  email: string;
  nombre_completo: string;
  rol: string;
  exp: number;
}

export function useAuth() {
  const [usuario, setUsuario] = useState<JwtPayload | null>(null);
  const [loading, setLoading]  = useState(true);

  useEffect(() => {
    const token = Cookies.get("access_token");
    if (token) {
      try {
        const decoded = jwtDecode<JwtPayload>(token);
        if (decoded.exp * 1000 > Date.now()) {
          setUsuario(decoded);
        } else {
          Cookies.remove("access_token");
        }
      } catch { /* token inválido */ }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const { data } = await api.post("/auth/login/", { email, password });
    Cookies.set("access_token",  data.access,  { expires: 1 / 24 });
    Cookies.set("refresh_token", data.refresh, { expires: 7 });
    setUsuario(jwtDecode<JwtPayload>(data.access));
    return data;
  };

  const logout = async () => {
    const refresh = Cookies.get("refresh_token");
    if (refresh) {
      try { await api.post("/auth/logout/", { refresh }); } catch { /* ok */ }
    }
    Cookies.remove("access_token");
    Cookies.remove("refresh_token");
    setUsuario(null);
    window.location.href = "/login";
  };

  const esAdmin = usuario?.rol === "ADMIN_DUBSS";
  const esCoord = ["ADMIN_DUBSS", "COORDINADOR"].includes(usuario?.rol ?? "");

  return { usuario, loading, login, logout, esAdmin, esCoord };
}
