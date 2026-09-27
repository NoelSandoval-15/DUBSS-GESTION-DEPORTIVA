
"use client";
import { useState, Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import api from "@/lib/api/client";

const R_LABEL: Record<string,string> = {local:"Victoria local",empate:"Empate",visitante:"Victoria visitante"};
const R_STYLE: Record<string,{bg:string;color:string}> = {
  local:    {bg:"#f0fdf4",color:"#15803d"},
  empate:   {bg:"#f3f4f6",color:"#4b5563"},
  visitante:{bg:"#eff6ff",color:"#1d4ed8"},
};

function MLContent() {
  const sp = useSearchParams();
  const [campeonatoId, setCampeonatoId] = useState(sp.get("campeonato")||"");

  const {data:camps} = useQuery({queryKey:["campeonatos"],queryFn:()=>api.get("/deportes/campeonatos/").then(r=>r.data)});
  const {data:tablero,isLoading} = useQuery({
    queryKey:["tablero-ml",campeonatoId],
    queryFn: ()=>api.get(`/ml/tablero/?campeonato=${campeonatoId}`).then(r=>r.data),
    enabled: !!campeonatoId,
  });

  return (
    <div style={{padding:"24px",maxWidth:"1024px",margin:"0 auto"}}>
      <div style={{marginBottom:"24px"}}>
        <div style={{display:"flex",alignItems:"center",gap:"8px",marginBottom:"4px"}}>
          <span style={{fontSize:"28px"}}>🤖</span>
          <h1 style={{fontSize:"24px",fontWeight:700,color:"#111827"}}>Predicciones ML</h1>
        </div>
        <p style={{color:"#6b7280",fontSize:"14px"}}>CU14 — Tablero de predicciones con Machine Learning (RandomForest)</p>
      </div>

      {/* Info modelo */}
      <div style={{backgroundColor:"#faf5ff",border:"1px solid #e9d5ff",borderRadius:"12px",padding:"16px",marginBottom:"24px"}}>
        <div style={{display:"flex",alignItems:"flex-start",gap:"12px"}}>
          <span style={{fontSize:"24px"}}>🧠</span>
          <div>
            <p style={{fontWeight:600,fontSize:"14px",color:"#6b21a8"}}>Modelo activo: RandomForest v1.0</p>
            <p style={{fontSize:"13px",color:"#7e22ce",marginTop:"2px"}}>
              Entrenado con historial de partidos. Considera puntos acumulados, diferencia de goles y enfrentamientos directos previos.
            </p>
          </div>
        </div>
      </div>

      <select value={campeonatoId} onChange={e=>setCampeonatoId(e.target.value)}
        style={{border:"1px solid #d1d5db",borderRadius:"8px",padding:"8px 12px",fontSize:"14px",width:"100%",maxWidth:"320px",marginBottom:"24px"}}>
        <option value="">Selecciona un campeonato</option>
        {camps?.results?.map((c:{id:number;nombre:string})=>(
          <option key={c.id} value={c.id}>{c.nombre}</option>
        ))}
      </select>

      {!campeonatoId&&(
        <div style={{backgroundColor:"white",borderRadius:"12px",border:"1px solid #e5e7eb",
                     padding:"48px",textAlign:"center",color:"#9ca3af"}}>
          <p style={{fontSize:"36px",marginBottom:"8px"}}>🤖</p>
          <p style={{fontWeight:500}}>Selecciona un campeonato para ver las predicciones.</p>
        </div>
      )}

      {campeonatoId&&isLoading&&<div style={{textAlign:"center",color:"#9ca3af",padding:"32px"}}>Calculando predicciones...</div>}

      {tablero?.length===0&&campeonatoId&&!isLoading&&(
        <div style={{backgroundColor:"white",borderRadius:"12px",border:"1px solid #e5e7eb",
                     padding:"48px",textAlign:"center",color:"#9ca3af"}}>
          <p style={{fontSize:"36px",marginBottom:"8px"}}>📭</p>
          <p style={{fontWeight:500}}>No hay partidos próximos para predecir.</p>
        </div>
      )}

      <div style={{display:"grid",gridTemplateColumns:"repeat(2,1fr)",gap:"16px"}}>
        {tablero?.map((pred:{partido_id:number;local:string;visitante:string;fecha_hora:string;prob_local:number;prob_empate:number;prob_visitante:number;resultado_probable:string;confianza:number})=>{
          const rs = R_STYLE[pred.resultado_probable]??{bg:"#f3f4f6",color:"#6b7280"};
          return (
            <div key={pred.partido_id} style={{backgroundColor:"white",borderRadius:"12px",border:"1px solid #e5e7eb",padding:"20px"}}>
              {/* Equipos */}
              <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",marginBottom:"8px"}}>
                <span style={{fontWeight:600,fontSize:"14px",color:"#111827",flex:1,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{pred.local}</span>
                <span style={{fontSize:"12px",color:"#9ca3af",margin:"0 8px",flexShrink:0}}>vs</span>
                <span style={{fontWeight:600,fontSize:"14px",color:"#111827",flex:1,textAlign:"right",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{pred.visitante}</span>
              </div>
              <p style={{fontSize:"12px",color:"#9ca3af",marginBottom:"16px"}}>
                📅 {new Date(pred.fecha_hora).toLocaleDateString("es-BO",{weekday:"short",day:"numeric",month:"short"})}
              </p>

              {/* Barras */}
              {[
                {label:pred.local,    val:pred.prob_local,     color:"#22c55e"},
                {label:"Empate",      val:pred.prob_empate,    color:"#9ca3af"},
                {label:pred.visitante,val:pred.prob_visitante, color:"#3b82f6"},
              ].map(b=>(
                <div key={b.label} style={{marginBottom:"8px"}}>
                  <div style={{display:"flex",justifyContent:"space-between",fontSize:"12px",marginBottom:"3px"}}>
                    <span style={{color:"#6b7280",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap",flex:1}}>{b.label}</span>
                    <span style={{fontWeight:600,marginLeft:"8px",flexShrink:0}}>{b.val}%</span>
                  </div>
                  <div style={{height:"6px",backgroundColor:"#f3f4f6",borderRadius:"999px",overflow:"hidden"}}>
                    <div style={{height:"100%",borderRadius:"999px",backgroundColor:b.color,width:`${b.val}%`}} />
                  </div>
                </div>
              ))}

              {/* Resultado probable */}
              <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginTop:"12px"}}>
                <span style={{padding:"4px 10px",borderRadius:"999px",fontSize:"12px",fontWeight:500,
                              backgroundColor:rs.bg,color:rs.color}}>
                  🎯 {R_LABEL[pred.resultado_probable]}
                </span>
                <span style={{fontSize:"12px",color:"#9ca3af"}}>Confianza: {pred.confianza}%</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function MLPage() {
  return <Suspense fallback={<div style={{padding:"24px",textAlign:"center",color:"#9ca3af"}}>Cargando...</div>}><MLContent /></Suspense>;
}
