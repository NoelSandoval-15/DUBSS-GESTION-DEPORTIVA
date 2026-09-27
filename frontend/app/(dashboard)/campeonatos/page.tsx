"use client";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import api from "@/lib/api/client";

const ESTADO_S: Record<string,{bg:string;color:string}> = {
  PLANIFICACION:{bg:"#f3f4f6",color:"#4b5563"},
  INSCRIPCIONES:{bg:"#eff6ff",color:"#1d4ed8"},
  EN_CURSO:     {bg:"#f0fdf4",color:"#15803d"},
  FINALIZADO:   {bg:"#f9fafb",color:"#9ca3af"},
  CANCELADO:    {bg:"#fef2f2",color:"#dc2626"},
};

export default function CampeonatosPage() {
  const { data, isLoading } = useQuery({
    queryKey:["campeonatos"],
    queryFn: ()=>api.get("/deportes/campeonatos/").then(r=>r.data),
  });

  return (
    <div style={{ padding:"24px", maxWidth:"960px", margin:"0 auto" }}>
      <div style={{ marginBottom:"24px" }}>
        <h1 style={{ fontSize:"24px", fontWeight:700, color:"#111827" }}>🏆 Campeonatos</h1>
        <p style={{ color:"#6b7280", fontSize:"14px" }}>Gestión de torneos deportivos DUBSS</p>
      </div>

      {isLoading && <div style={{ textAlign:"center", color:"#9ca3af", padding:"64px" }}>Cargando...</div>}

      <div style={{ display:"flex", flexDirection:"column", gap:"12px" }}>
        {data?.results?.map((c:{id:number;nombre:string;estado:string;deporte_detalle:{nombre:string};categoria_detalle:{nombre:string;genero:string};fecha_inicio:string;fecha_fin:string;total_equipos:number;max_equipos:number;formato:string}) => {
          const s = ESTADO_S[c.estado] ?? {bg:"#f3f4f6",color:"#6b7280"};
          return (
            <Link key={c.id} href={`/campeonatos/${c.id}`}
              style={{ backgroundColor:"white", borderRadius:"12px", border:"1px solid #e5e7eb",
                       padding:"20px", textDecoration:"none", color:"inherit", display:"block",
                       transition:"box-shadow 0.15s" }}
              onMouseEnter={e=>(e.currentTarget.style.boxShadow="0 4px 12px rgba(0,0,0,0.08)")}
              onMouseLeave={e=>(e.currentTarget.style.boxShadow="none")}>
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", gap:"16px" }}>
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ display:"flex", alignItems:"center", gap:"8px", marginBottom:"4px", flexWrap:"wrap" }}>
                    <h3 style={{ fontWeight:600, color:"#111827", fontSize:"16px" }}>{c.nombre}</h3>
                    <span style={{ display:"inline-flex", alignItems:"center", padding:"2px 8px",
                                   borderRadius:"999px", fontSize:"12px", fontWeight:500,
                                   backgroundColor:s.bg, color:s.color }}>
                      {c.estado.replace("_"," ")}
                    </span>
                  </div>
                  <p style={{ fontSize:"14px", color:"#6b7280" }}>
                    {c.deporte_detalle?.nombre} — {c.categoria_detalle?.nombre} ({c.categoria_detalle?.genero})
                  </p>
                  <div style={{ display:"flex", gap:"16px", marginTop:"8px", fontSize:"12px", color:"#9ca3af", flexWrap:"wrap" }}>
                    <span>📅 {new Date(c.fecha_inicio).toLocaleDateString("es-BO")} → {new Date(c.fecha_fin).toLocaleDateString("es-BO")}</span>
                    <span>👥 {c.total_equipos}/{c.max_equipos} equipos</span>
                    <span>🔄 {c.formato.replace("_"," ")}</span>
                  </div>
                </div>
                <span style={{ color:"#d1d5db", fontSize:"20px" }}>›</span>
              </div>
            </Link>
          );
        })}
        {data?.results?.length === 0 && (
          <div style={{ backgroundColor:"white", borderRadius:"12px", border:"1px solid #e5e7eb",
                        padding:"48px", textAlign:"center", color:"#9ca3af" }}>
            <p style={{ fontSize:"36px", marginBottom:"8px" }}>🏆</p>
            <p style={{ fontWeight:500 }}>No hay campeonatos registrados.</p>
            <p style={{ fontSize:"13px", marginTop:"4px" }}>Crea el primero desde el Admin de Django.</p>
          </div>
        )}
      </div>
    </div>
  );
}
