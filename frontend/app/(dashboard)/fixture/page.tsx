
"use client";
import { useState, Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import api from "@/lib/api/client";

const ES: Record<string,{bg:string;color:string}> = {
  PROGRAMADO:{bg:"#eff6ff",color:"#1d4ed8"},
  EN_CURSO:  {bg:"#f0fdf4",color:"#15803d"},
  FINALIZADO:{bg:"#f9fafb",color:"#4b5563"},
  SUSPENDIDO:{bg:"#fef2f2",color:"#dc2626"},
  POSTERGADO:{bg:"#fffbeb",color:"#d97706"},
};

function FixtureContent() {
  const sp = useSearchParams();
  const [campeonatoId, setCampeonatoId] = useState(sp.get("campeonato")||"");
  const [jornada, setJornada] = useState("");

  const {data:camps} = useQuery({queryKey:["campeonatos"],queryFn:()=>api.get("/deportes/campeonatos/").then(r=>r.data)});
  const {data:partidos,isLoading} = useQuery({
    queryKey:["partidos",campeonatoId,jornada],
    queryFn:()=>{
      const p=new URLSearchParams();
      if(campeonatoId) p.set("campeonato",campeonatoId);
      if(jornada) p.set("jornada",jornada);
      return api.get(`/fixture/partidos/?${p}`).then(r=>r.data);
    },
  });

  const por: Record<number,{id:number;jornada:number;local:string;visitante:string;cancha:string;fecha_hora:string;estado:string;resultado?:{goles_local:number;goles_visitante:number}}[]> = {};
  partidos?.results?.forEach((p:{id:number;jornada:number;local:string;visitante:string;cancha:string;fecha_hora:string;estado:string;resultado?:{goles_local:number;goles_visitante:number}})=>{
    if(!por[p.jornada]) por[p.jornada]=[];
    por[p.jornada].push(p);
  });

  return (
    <div style={{padding:"24px",maxWidth:"960px",margin:"0 auto"}}>
      <div style={{marginBottom:"24px"}}>
        <h1 style={{fontSize:"24px",fontWeight:700,color:"#111827"}}>📅 Fixture</h1>
        <p style={{color:"#6b7280",fontSize:"14px"}}>Click en un partido para ver detalles o registrar resultado</p>
      </div>

      <div style={{display:"flex",gap:"12px",marginBottom:"24px",flexWrap:"wrap"}}>
        <select value={campeonatoId} onChange={e=>setCampeonatoId(e.target.value)}
          style={{border:"1px solid #d1d5db",borderRadius:"8px",padding:"8px 12px",fontSize:"14px",minWidth:"200px"}}>
          <option value="">Todos los campeonatos</option>
          {camps?.results?.map((c:{id:number;nombre:string})=>(
            <option key={c.id} value={c.id}>{c.nombre}</option>
          ))}
        </select>
        <input type="number" min="1" placeholder="Jornada #" value={jornada}
          onChange={e=>setJornada(e.target.value)}
          style={{border:"1px solid #d1d5db",borderRadius:"8px",padding:"8px 12px",fontSize:"14px",width:"120px"}} />
        {(campeonatoId||jornada) && (
          <button onClick={()=>{setCampeonatoId("");setJornada("");}}
            style={{border:"1px solid #d1d5db",borderRadius:"8px",padding:"8px 12px",fontSize:"14px",cursor:"pointer",backgroundColor:"white"}}>
            Limpiar
          </button>
        )}
      </div>

      {isLoading && <div style={{textAlign:"center",color:"#9ca3af",padding:"64px"}}>Cargando partidos...</div>}

      {Object.entries(por).map(([j,ps])=>(
        <div key={j} style={{marginBottom:"24px"}}>
          <h3 style={{fontSize:"12px",fontWeight:600,color:"#6b7280",textTransform:"uppercase",letterSpacing:"0.05em",marginBottom:"8px"}}>
            Jornada {j}
          </h3>
          <div style={{display:"flex",flexDirection:"column",gap:"8px"}}>
            {ps.map(p=>{
              const s=ES[p.estado]??{bg:"#f3f4f6",color:"#6b7280"};
              return (
                <Link key={p.id} href={`/fixture/partido/${p.id}`}
                  style={{backgroundColor:"white",borderRadius:"12px",border:"1px solid #e5e7eb",
                          display:"flex",alignItems:"center",gap:"16px",padding:"12px 20px",
                          textDecoration:"none",color:"inherit",transition:"box-shadow 0.15s"}}
                  onMouseEnter={e=>(e.currentTarget.style.boxShadow="0 4px 12px rgba(0,0,0,0.08)")}
                  onMouseLeave={e=>(e.currentTarget.style.boxShadow="none")}>
                  <div style={{flex:1,textAlign:"right"}}>
                    <p style={{fontWeight:600,fontSize:"14px",color:"#111827"}}>{p.local}</p>
                  </div>
                  <div style={{width:"140px",textAlign:"center",flexShrink:0}}>
                    {p.estado==="FINALIZADO"&&p.resultado ? (
                      <p style={{fontSize:"20px",fontWeight:700,color:"#111827"}}>
                        {p.resultado.goles_local} — {p.resultado.goles_visitante}
                      </p>
                    ) : (
                      <div>
                        <p style={{fontSize:"12px",color:"#6b7280"}}>{new Date(p.fecha_hora).toLocaleDateString("es-BO",{day:"numeric",month:"short"})}</p>
                        <p style={{fontSize:"14px",fontWeight:700,color:"#111827"}}>{new Date(p.fecha_hora).toLocaleTimeString("es-BO",{hour:"2-digit",minute:"2-digit"})}</p>
                      </div>
                    )}
                    <span style={{display:"inline-block",marginTop:"4px",padding:"2px 8px",borderRadius:"999px",
                                  fontSize:"11px",fontWeight:500,backgroundColor:s.bg,color:s.color}}>
                      {p.estado}
                    </span>
                  </div>
                  <div style={{flex:1}}>
                    <p style={{fontWeight:600,fontSize:"14px",color:"#111827"}}>{p.visitante}</p>
                  </div>
                  <span style={{color:"#d1d5db",flexShrink:0}}>›</span>
                </Link>
              );
            })}
          </div>
        </div>
      ))}

      {partidos?.results?.length===0&&!isLoading&&(
        <div style={{backgroundColor:"white",borderRadius:"12px",border:"1px solid #e5e7eb",
                     padding:"48px",textAlign:"center",color:"#9ca3af"}}>
          <p style={{fontSize:"36px",marginBottom:"8px"}}>📅</p>
          <p style={{fontWeight:500}}>No hay partidos.</p>
          <p style={{fontSize:"13px",marginTop:"4px"}}>Genera el fixture desde el detalle del campeonato.</p>
        </div>
      )}
    </div>
  );
}

export default function FixturePage() {
  return <Suspense fallback={<div style={{padding:"24px",textAlign:"center",color:"#9ca3af"}}>Cargando...</div>}><FixtureContent /></Suspense>;
}
