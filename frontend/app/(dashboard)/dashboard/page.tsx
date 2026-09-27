"use client";
import { useQuery } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import Link from "next/link";
import api from "@/lib/api/client";
import { useAuth } from "@/lib/hooks/useAuth";

export default function DashboardPage() {
  const { usuario } = useAuth();
  const { data: camps } = useQuery({ queryKey:["campeonatos"], queryFn:()=>api.get("/deportes/campeonatos/").then(r=>r.data) });
  const { data: partidos } = useQuery({ queryKey:["partidos-prox"], queryFn:()=>api.get("/fixture/partidos/?estado=PROGRAMADO").then(r=>r.data) });
  const { data: equipos } = useQuery({ queryKey:["equipos"], queryFn:()=>api.get("/deportes/equipos/").then(r=>r.data) });

  const [saludo, setSaludo] = useState("Bienvenido");
  useEffect(() => {
    const hora = new Date().getHours();
    setSaludo(hora < 12 ? "Buenos días" : hora < 18 ? "Buenas tardes" : "Buenas noches");
  }, []);

  const stats = [
    { icon:"🏆", label:"Campeonatos", value: camps?.count ?? "—" },
    { icon:"📅", label:"Próx. partidos", value: partidos?.count ?? "—" },
    { icon:"👥", label:"Equipos", value: equipos?.count ?? "—" },
    { icon:"🤖", label:"Módulo ML", value: "Activo" },
  ];

  const accesos = [
    { href:"/campeonatos", icon:"🏆", label:"Ver campeonatos" },
    { href:"/fixture", icon:"📅", label:"Calendario fixture" },
    { href:"/fixture/tabla", icon:"📊", label:"Tabla posiciones" },
    { href:"/ml", icon:"🤖", label:"Predicciones ML" },
  ];

  return (
    <div style={{ padding:"24px", maxWidth:"1024px", margin:"0 auto" }}>
      <div style={{ marginBottom:"32px" }}>
        <h1 style={{ fontSize:"24px", fontWeight:700, color:"#111827" }}>
          {saludo}, {usuario?.nombre_completo?.split(" ")[0] ?? "usuario"} 👋
        </h1>
        <p style={{ color:"#6b7280", fontSize:"14px", marginTop:"4px" }}>
          Sistema de Gestión Deportiva DUBSS — UAGRM
        </p>
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:"16px", marginBottom:"32px" }}>
        {stats.map(s => (
          <div key={s.label} style={{ backgroundColor:"white", borderRadius:"12px", border:"1px solid #e5e7eb", padding:"20px", display:"flex", alignItems:"center", gap:"16px" }}>
            <div style={{ width:"48px", height:"48px", borderRadius:"12px", backgroundColor:"#f0fdf4", display:"flex", alignItems:"center", justifyContent:"center", fontSize:"24px" }}>
              {s.icon}
            </div>
            <div>
              <p style={{ fontSize:"13px", color:"#6b7280" }}>{s.label}</p>
              <p style={{ fontSize:"24px", fontWeight:700, color:"#111827" }}>{s.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginBottom:"32px" }}>
        <h2 style={{ fontSize:"18px", fontWeight:600, color:"#1f2937", marginBottom:"16px" }}>Accesos rápidos</h2>
        <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:"12px" }}>
          {accesos.map(a => (
            <Link key={a.href} href={a.href}
              style={{ backgroundColor:"white", border:"2px solid #e5e7eb", borderRadius:"12px", padding:"16px", display:"flex", flexDirection:"column", alignItems:"center", gap:"8px", textAlign:"center", textDecoration:"none", transition:"border-color 0.15s" }}
              onMouseEnter={e=>(e.currentTarget.style.borderColor="#1a6b3c")}
              onMouseLeave={e=>(e.currentTarget.style.borderColor="#e5e7eb")}>
              <span style={{ fontSize:"28px" }}>{a.icon}</span>
              <span style={{ fontSize:"13px", fontWeight:500, color:"#374151" }}>{a.label}</span>
            </Link>
          ))}
        </div>
      </div>

      <div>
        <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"16px" }}>
          <h2 style={{ fontSize:"18px", fontWeight:600, color:"#1f2937" }}>Próximos partidos</h2>
          <Link href="/fixture" style={{ fontSize:"13px", color:"#1a6b3c", textDecoration:"none" }}>Ver todos →</Link>
        </div>
        <div style={{ backgroundColor:"white", borderRadius:"12px", border:"1px solid #e5e7eb", overflow:"hidden" }}>
          {partidos?.results?.length === 0 && (
            <p style={{ textAlign:"center", color:"#9ca3af", padding:"32px", fontSize:"14px" }}>
              No hay partidos programados.
            </p>
          )}
          {partidos?.results?.slice(0,5).map((p:{id:number;jornada:number;local:string;visitante:string;fecha_hora:string}) => (
            <Link key={p.id} href={`/fixture/partido/${p.id}`}
              style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"12px 20px", borderBottom:"1px solid #f3f4f6", textDecoration:"none", color:"inherit" }}
              onMouseEnter={e=>(e.currentTarget.style.backgroundColor="#f9fafb")}
              onMouseLeave={e=>(e.currentTarget.style.backgroundColor="transparent")}>
              <div style={{ display:"flex", alignItems:"center", gap:"16px", flex:1, minWidth:0 }}>
                <span style={{ fontSize:"12px", color:"#9ca3af", width:"40px", flexShrink:0 }}>J{p.jornada}</span>
                <div style={{ display:"flex", alignItems:"center", gap:"8px", minWidth:0 }}>
                  <span style={{ fontSize:"14px", fontWeight:500, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{p.local}</span>
                  <span style={{ fontSize:"12px", color:"#9ca3af", flexShrink:0 }}>vs</span>
                  <span style={{ fontSize:"14px", fontWeight:500, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{p.visitante}</span>
                </div>
              </div>
              <div style={{ textAlign:"right", flexShrink:0, marginLeft:"16px" }}>
                <p style={{ fontSize:"12px", color:"#6b7280" }}>{new Date(p.fecha_hora).toLocaleDateString("es-BO",{day:"numeric",month:"short"})}</p>
                <p style={{ fontSize:"12px", color:"#9ca3af" }}>{new Date(p.fecha_hora).toLocaleTimeString("es-BO",{hour:"2-digit",minute:"2-digit"})}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
