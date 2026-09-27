"use client";
import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Cookies from "js-cookie";
import api from "@/lib/api/client";
import { jwtDecode } from "jwt-decode";

function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const redirect = params.get("redirect") || "/dashboard";
  const [email, setEmail] = useState("");
  const [pass, setPass] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = Cookies.get("access_token");
    if (token) {
      try {
        const d = jwtDecode<{ exp: number }>(token);
        if (d.exp * 1000 > Date.now()) router.replace(redirect);
      } catch { /* ignore */ }
    }
  }, [redirect, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      const { data } = await api.post("/auth/login/", { email, password: pass });
      Cookies.set("access_token",  data.access,  { expires: 1/24 });
      Cookies.set("refresh_token", data.refresh, { expires: 7 });
      router.push(redirect);
    } catch {
      setError("Credenciales incorrectas. Verifica tu email y contraseña.");
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4"
      style={{ background: "linear-gradient(135deg, #0f3d22 0%, #1a6b3c 50%, #059669 100%)" }}>
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4"
            style={{ backgroundColor: "rgba(255,255,255,0.15)" }}>
            <span className="text-3xl">⚽</span>
          </div>
          <h1 className="text-3xl font-bold text-white">DUBSS</h1>
          <p className="text-sm mt-1" style={{ color: "#a7f3d0" }}>
            Sistema de Gestión Deportiva — UAGRM
          </p>
        </div>
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-6">Iniciar sesión</h2>
          {error && (
            <div className="rounded-lg px-4 py-3 mb-4 text-sm"
              style={{ backgroundColor:"#fef2f2", color:"#dc2626", border:"1px solid #fecaca" }}>
              {error}
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Correo electrónico</label>
              <input type="email" required value={email} onChange={e => setEmail(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-600"
                placeholder="admin@dubss.com" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
              <input type="password" required value={pass} onChange={e => setPass(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-600"
                placeholder="••••••••" />
            </div>
            <button type="submit" disabled={loading}
              className="w-full py-2.5 rounded-lg font-medium text-white text-base transition-all"
              style={{ backgroundColor: loading ? "#9ca3af" : "#1a6b3c" }}>
              {loading ? "Iniciando sesión..." : "Entrar al sistema"}
            </button>
          </form>
          <p className="text-center text-xs text-gray-400 mt-6">
            FICCT — Universidad Autónoma Gabriel René Moreno · Santa Cruz, Bolivia
          </p>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return <Suspense><LoginForm /></Suspense>;
}
