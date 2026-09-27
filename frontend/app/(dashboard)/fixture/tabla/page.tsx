
"use client";
import { useState, Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import api from "@/lib/api/client";

function TablaContent() {
  const sp = useSearchParams();
  const [campeonatoId, setCampeonatoId] = useState(sp.get("campeonato")||"");

  const {data:camps} = useQuery({queryKey:["campeonatos"],queryFn:()=>api.get("/deportes/campeonatos/").then(r=>r.data)});
  const {data:tabla,isLoading} = useQuery({
    queryKey:["tabla",campeonatoId],
    queryFn:()=>campeonatoId ? api.get(`/fixture/tabla-posiciones/?campeonato=${campeonatoId}`).then(r=>r.data) : Promise.resolve([]),
    enabled:!!campeonatoId,
  });

  return (
    <div style={{padding:"24px",maxWidth:"960px",margin:"0 auto"}}>
      <div style={{marginBottom:"24px"}}>
        <h1 style={{fontSize:"24px",fontWeight:700,color:"#111827"}}>📊 Tabla de posiciones</h1>
        <p style={{color:"#6b7280",fontSize:"14px"}}>Clasificación por campeonato</p>
      </div>

      <select value={campeonatoId} onChange={e=>setCampeonatoId(e.target.value)}
        style={{border:"1px solid #d1d5db",borderRadius:"8px",padding:"8px 12px",fontSize:"14px",width:"100%",maxWidth:"320px",marginBottom:"24px"}}>
        <option value="">Selecciona un campeonato</option>
        {camps?.results?.map((c:{id:number;nombre:string})=>(
          <option key={c.id} value={c.id}>{c.nombre}</option>
        ))}
      </select>

      {!campeonatoId && (
        <div style={{backgroundColor:"white",borderRadius:"12px",border:"1px solid #e5e7eb",
                     padding:"48px",textAlign:"center",color:"#9ca3af"}}>
          <p style={{fontSize:"36px",marginBottom:"8px"}}>📊</p>
          <p style={{fontWeight:500}}>Selecciona un campeonato para ver la tabla.</p>
        </div>
      )}

      {campeonatoId&&isLoading&&<div style={{textAlign:"center",color:"#9ca3af",padding:"32px"}}>Cargando tabla...</div>}

      {tabla&&tabla.length>0&&(
        <div style={{backgroundColor:"white",borderRadius:"12px",border:"1px solid #e5e7eb",overflow:"hidden"}}>
          <table style={{width:"100%",borderCollapse:"collapse",fontSize:"14px"}}>
            <thead>
              <tr style={{backgroundColor:"#1a6b3c",color:"white"}}>
                {["#","Equipo","PJ","PG","PE","PP","GF","GC","DG","Pts"].map(h=>(
                  <th key={h} style={{padding:"12px 12px",fontWeight:600,fontSize:"12px",textTransform:"uppercase",
                                      textAlign:h==="Equipo"?"left":"center"}}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tabla.map((f:{id:number;equipo_detalle:{nombre:string;facultad:string};pj:number;pg:number;pe:number;pp:number;gf:number;gc:number;diferencia_goles:number;puntos:number},i:number)=>(
                <tr key={f.id} style={{borderBottom:"1px solid #f3f4f6",backgroundColor:i===0?"#f0fdf4":i%2===0?"#fafafa":"white"}}>
                  <td style={{padding:"10px 12px",textAlign:"center",fontWeight:700,color:"#9ca3af"}}>{i+1}</td>
                  <td style={{padding:"10px 12px",fontWeight:600,color:"#111827"}}>
                    {f.equipo_detalle?.nombre}
                    <span style={{fontSize:"12px",color:"#9ca3af",marginLeft:"4px"}}>({f.equipo_detalle?.facultad})</span>
                  </td>
                  {[f.pj,f.pg,f.pe,f.pp,f.gf,f.gc].map((v,j)=>(
                    <td key={j} style={{padding:"10px 12px",textAlign:"center",color:"#4b5563"}}>{v}</td>
                  ))}
                  <td style={{padding:"10px 12px",textAlign:"center",fontWeight:600,
                               color:f.diferencia_goles>0?"#16a34a":f.diferencia_goles<0?"#ef4444":"#6b7280"}}>
                    {f.diferencia_goles>0?"+":""}{f.diferencia_goles}
                  </td>
                  <td style={{padding:"10px 12px",textAlign:"center"}}>
                    <span style={{fontWeight:700,fontSize:"16px",color:"#1a6b3c"}}>{f.puntos}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tabla&&tabla.length===0&&campeonatoId&&!isLoading&&(
        <div style={{backgroundColor:"white",borderRadius:"12px",border:"1px solid #e5e7eb",
                     padding:"48px",textAlign:"center",color:"#9ca3af"}}>
          <p style={{fontSize:"36px",marginBottom:"8px"}}>📭</p>
          <p style={{fontWeight:500}}>No hay datos aún. Registra resultados para ver la clasificación.</p>
        </div>
      )}
    </div>
  );
}

export default function TablaPage() {
  return <Suspense fallback={<div style={{padding:"24px",textAlign:"center",color:"#9ca3af"}}>Cargando...</div>}><TablaContent /></Suspense>;
}
