
"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Link from "next/link";
import api from "@/lib/api/client";
import { useAuth } from "@/lib/hooks/useAuth";

export default function PartidoDetallePage() {
  const { id }      = useParams<{ id: string }>();
  const { usuario } = useAuth();
  const qc          = useQueryClient();
  const [golesL,    setGolesL]    = useState("0");
  const [golesV,    setGolesV]    = useState("0");
  const [obs,       setObs]       = useState("");
  const [showForm,  setShowForm]  = useState(false);

  const {data:partido,isLoading} = useQuery({
    queryKey:["partido",id],
    queryFn: ()=>api.get(`/fixture/partidos/${id}/`).then(r=>r.data),
  });

  const registrar = useMutation({
    mutationFn: ()=>api.post(`/fixture/partidos/${id}/resultado/`,{
      goles_local:parseInt(golesL), goles_visitante:parseInt(golesV), observaciones:obs,
    }),
    onSuccess: ()=>{ qc.invalidateQueries({queryKey:["partido",id]}); setShowForm(false); },
    onError: (e:unknown)=>{ const m=(e as {response?:{data?:Record<string,unknown>}})?.response?.data; alert("Error: "+JSON.stringify(m)); },
  });

  const puedeRegistrar = ["ADMIN_DUBSS","COORDINADOR","ARBITRO"].includes(usuario?.rol??"");

  if (isLoading) return <div style={{padding:"24px",textAlign:"center",color:"#9ca3af"}}>Cargando...</div>;
  if (!partido)  return <div style={{padding:"24px",textAlign:"center"}}>Partido no encontrado. <Link href="/fixture">← Volver</Link></div>;

  const local     = partido.equipo_local_detalle;
  const visitante = partido.equipo_visitante_detalle;
  const resultado = partido.resultado;

  return (
    <div style={{padding:"24px",maxWidth:"720px",margin:"0 auto"}}>
      {/* Breadcrumb */}
      <div style={{display:"flex",alignItems:"center",gap:"8px",fontSize:"13px",color:"#9ca3af",marginBottom:"24px"}}>
        <Link href="/fixture" style={{color:"#9ca3af",textDecoration:"none"}}>Fixture</Link>
        <span>›</span>
        <span style={{color:"#374151",fontWeight:500}}>Partido #{id}</span>
      </div>

      {/* Marcador */}
      <div style={{backgroundColor:"white",borderRadius:"16px",border:"1px solid #e5e7eb",padding:"32px",marginBottom:"20px"}}>
        <p style={{textAlign:"center",fontSize:"12px",color:"#9ca3af",textTransform:"uppercase",letterSpacing:"0.1em",marginBottom:"20px",fontWeight:600}}>
          Jornada {partido.jornada} — {partido.fase}
        </p>
        <div style={{display:"flex",alignItems:"center",justifyContent:"space-between",gap:"16px"}}>
          {/* Local */}
          <div style={{flex:1,textAlign:"center"}}>
            <div style={{width:"56px",height:"56px",borderRadius:"50%",margin:"0 auto 8px",
                         display:"flex",alignItems:"center",justifyContent:"center",
                         color:"white",fontSize:"22px",fontWeight:700,
                         backgroundColor:local?.color_principal||"#1a6b3c"}}>
              {local?.nombre?.charAt(0)}
            </div>
            <p style={{fontWeight:700,fontSize:"15px",color:"#111827"}}>{local?.nombre}</p>
            <p style={{fontSize:"12px",color:"#9ca3af"}}>{local?.facultad}</p>
          </div>

          {/* Score */}
          <div style={{textAlign:"center",flexShrink:0}}>
            {resultado ? (
              <p style={{fontSize:"40px",fontWeight:800,color:"#111827",lineHeight:1}}>
                {resultado.goles_local} — {resultado.goles_visitante}
              </p>
            ) : (
              <div>
                <p style={{fontSize:"28px",fontWeight:700,color:"#e5e7eb",lineHeight:1}}>vs</p>
                <p style={{fontSize:"14px",fontWeight:600,color:"#1a6b3c",marginTop:"4px"}}>
                  {new Date(partido.fecha_hora).toLocaleTimeString("es-BO",{hour:"2-digit",minute:"2-digit"})}
                </p>
                <p style={{fontSize:"13px",color:"#6b7280"}}>
                  {new Date(partido.fecha_hora).toLocaleDateString("es-BO",{weekday:"long",day:"numeric",month:"long"})}
                </p>
              </div>
            )}
            <span style={{display:"inline-block",marginTop:"8px",padding:"4px 12px",borderRadius:"999px",fontSize:"12px",fontWeight:500,
                          backgroundColor:partido.estado==="FINALIZADO"?"#f0fdf4":"#eff6ff",
                          color:partido.estado==="FINALIZADO"?"#15803d":"#1d4ed8"}}>
              {partido.estado}
            </span>
          </div>

          {/* Visitante */}
          <div style={{flex:1,textAlign:"center"}}>
            <div style={{width:"56px",height:"56px",borderRadius:"50%",margin:"0 auto 8px",
                         display:"flex",alignItems:"center",justifyContent:"center",
                         color:"white",fontSize:"22px",fontWeight:700,
                         backgroundColor:visitante?.color_principal||"#7c3aed"}}>
              {visitante?.nombre?.charAt(0)}
            </div>
            <p style={{fontWeight:700,fontSize:"15px",color:"#111827"}}>{visitante?.nombre}</p>
            <p style={{fontSize:"12px",color:"#9ca3af"}}>{visitante?.facultad}</p>
          </div>
        </div>

        {partido.cancha_detalle && (
          <p style={{textAlign:"center",fontSize:"12px",color:"#9ca3af",marginTop:"20px",paddingTop:"16px",borderTop:"1px solid #f3f4f6"}}>
            🏟️ {partido.cancha_detalle.nombre}
          </p>
        )}
      </div>

      {/* Registrar resultado */}
      {puedeRegistrar && partido.estado!=="FINALIZADO" && (
        <div style={{backgroundColor:"white",borderRadius:"16px",border:"1px solid #e5e7eb",padding:"24px",marginBottom:"20px"}}>
          <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"16px"}}>
            <h3 style={{fontWeight:600,color:"#1f2937",fontSize:"16px"}}>⚽ Registrar resultado</h3>
            <button onClick={()=>setShowForm(!showForm)}
              style={{padding:"6px 14px",borderRadius:"8px",border:"1px solid #d1d5db",
                      fontSize:"13px",cursor:"pointer",backgroundColor:"white"}}>
              {showForm?"Cancelar":"Registrar"}
            </button>
          </div>
          {showForm && (
            <div>
              <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:"16px",marginBottom:"16px"}}>
                <div>
                  <label style={{display:"block",fontSize:"13px",fontWeight:500,color:"#374151",marginBottom:"6px"}}>
                    Goles — {local?.nombre}
                  </label>
                  <input type="number" min="0" max="99" value={golesL} onChange={e=>setGolesL(e.target.value)}
                    style={{width:"100%",border:"1px solid #d1d5db",borderRadius:"8px",padding:"10px",
                            textAlign:"center",fontSize:"24px",fontWeight:700,color:"#1a6b3c",boxSizing:"border-box"}} />
                </div>
                <div>
                  <label style={{display:"block",fontSize:"13px",fontWeight:500,color:"#374151",marginBottom:"6px"}}>
                    Goles — {visitante?.nombre}
                  </label>
                  <input type="number" min="0" max="99" value={golesV} onChange={e=>setGolesV(e.target.value)}
                    style={{width:"100%",border:"1px solid #d1d5db",borderRadius:"8px",padding:"10px",
                            textAlign:"center",fontSize:"24px",fontWeight:700,color:"#7c3aed",boxSizing:"border-box"}} />
                </div>
              </div>
              <textarea value={obs} onChange={e=>setObs(e.target.value)} rows={2}
                placeholder="Observaciones del partido (opcional)..."
                style={{width:"100%",border:"1px solid #d1d5db",borderRadius:"8px",padding:"10px",
                        fontSize:"14px",resize:"none",marginBottom:"12px",boxSizing:"border-box"}} />
              <button onClick={()=>registrar.mutate()} disabled={registrar.isPending}
                style={{width:"100%",padding:"12px",borderRadius:"8px",border:"none",cursor:"pointer",
                        fontWeight:600,fontSize:"15px",color:"white",
                        backgroundColor:registrar.isPending?"#9ca3af":"#1a6b3c"}}>
                {registrar.isPending?"Guardando...":"✅ Confirmar resultado"}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Resultado oficial */}
      {resultado && (
        <div style={{backgroundColor:"white",borderRadius:"16px",border:"1px solid #e5e7eb",padding:"24px",marginBottom:"20px"}}>
          <h3 style={{fontWeight:600,color:"#1f2937",fontSize:"16px",marginBottom:"12px"}}>📋 Resultado oficial</h3>
          <div style={{display:"flex",alignItems:"center",gap:"16px",flexWrap:"wrap"}}>
            <span style={{fontSize:"32px",fontWeight:800,color:"#111827"}}>
              {resultado.goles_local} — {resultado.goles_visitante}
            </span>
            {resultado.ganador ? (
              <span style={{padding:"6px 14px",borderRadius:"8px",fontSize:"14px",fontWeight:600,
                            backgroundColor:"#f0fdf4",color:"#15803d"}}>
                🏆 {resultado.ganador.nombre}
              </span>
            ) : (
              <span style={{padding:"6px 14px",borderRadius:"8px",fontSize:"14px",fontWeight:600,
                            backgroundColor:"#f3f4f6",color:"#6b7280"}}>
                🤝 Empate
              </span>
            )}
          </div>
          {resultado.observaciones && (
            <p style={{fontSize:"14px",color:"#6b7280",marginTop:"12px"}}>{resultado.observaciones}</p>
          )}
        </div>
      )}

      {/* Incidencias */}
      {partido.incidencias?.length>0 && (
        <div style={{backgroundColor:"white",borderRadius:"16px",border:"1px solid #e5e7eb",padding:"24px"}}>
          <h3 style={{fontWeight:600,color:"#1f2937",fontSize:"16px",marginBottom:"12px"}}>⚡ Incidencias</h3>
          {partido.incidencias.map((inc:{id:number;tipo:string;minuto:number;descripcion:string})=>(
            <div key={inc.id} style={{display:"flex",alignItems:"center",gap:"12px",padding:"8px 0",
                                      borderBottom:"1px solid #f3f4f6",fontSize:"14px"}}>
              <span style={{color:"#9ca3af",width:"40px",textAlign:"right",flexShrink:0,fontWeight:500}}>
                {inc.minuto?`${inc.minuto}'`:"—"}
              </span>
              <span style={{fontWeight:500,color:"#374151"}}>{inc.tipo.replace("_"," ")}</span>
              {inc.descripcion&&<span style={{color:"#9ca3af"}}>{inc.descripcion}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
