
"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Link from "next/link";
import api from "@/lib/api/client";
import { useAuth } from "@/lib/hooks/useAuth";

const ESTADO_S: Record<string,{bg:string;color:string}> = {
  PLANIFICACION:{bg:"#f3f4f6",color:"#4b5563"},
  INSCRIPCIONES:{bg:"#eff6ff",color:"#1d4ed8"},
  EN_CURSO:     {bg:"#f0fdf4",color:"#15803d"},
  FINALIZADO:   {bg:"#f9fafb",color:"#9ca3af"},
  CANCELADO:    {bg:"#fef2f2",color:"#dc2626"},
};

export default function CampeonatoDetallePage() {
  const { id }      = useParams<{ id: string }>();
  const { esCoord } = useAuth();
  const qc          = useQueryClient();

  const { data: camp, isLoading } = useQuery({
    queryKey:["campeonato",id],
    queryFn: ()=>api.get(`/deportes/campeonatos/${id}/`).then(r=>r.data),
  });
  const { data: equipos } = useQuery({
    queryKey:["camp-equipos",id],
    queryFn: ()=>api.get(`/deportes/campeonatos/${id}/equipos/`).then(r=>r.data),
    enabled: !!id,
  });
  const { data: partidos } = useQuery({
    queryKey:["partidos-camp",id],
    queryFn: ()=>api.get(`/fixture/partidos/?campeonato=${id}`).then(r=>r.data),
    enabled: !!id,
  });

  const generarFixture = useMutation({
    mutationFn: ()=>api.post(`/fixture/generar/?campeonato_id=${id}&hora_inicio=09%3A00`),
    onSuccess: ()=>{ qc.invalidateQueries({queryKey:["partidos-camp",id]}); alert("✅ Fixture generado"); },
    onError: (e:unknown)=>{ const m=(e as {response?:{data?:{error?:string}}})?.response?.data?.error; alert("Error: "+(m||"No se pudo generar")); },
  });

  const cambiarEstado = useMutation({
    mutationFn: (estado:string)=>api.patch(`/deportes/campeonatos/${id}/estado/`,{estado}),
    onSuccess: ()=>qc.invalidateQueries({queryKey:["campeonato",id]}),
  });

  if (isLoading) return <div style={{padding:"24px",textAlign:"center",color:"#9ca3af"}}>Cargando...</div>;
  if (!camp)    return <div style={{padding:"24px",textAlign:"center",color:"#9ca3af"}}>No encontrado. <Link href="/campeonatos">← Volver</Link></div>;

  const s = ESTADO_S[camp.estado] ?? {bg:"#f3f4f6",color:"#6b7280"};
  const totalPartidos = partidos?.count ?? 0;
  const finalizados   = partidos?.results?.filter((p:{estado:string})=>p.estado==="FINALIZADO").length ?? 0;
  const totalEquipos  = Array.isArray(equipos) ? equipos.length : 0;

  return (
    <div style={{padding:"24px",maxWidth:"960px",margin:"0 auto"}}>
      {/* Breadcrumb */}
      <div style={{display:"flex",alignItems:"center",gap:"8px",fontSize:"13px",color:"#9ca3af",marginBottom:"24px"}}>
        <Link href="/campeonatos" style={{color:"#9ca3af",textDecoration:"none"}}>Campeonatos</Link>
        <span>›</span>
        <span style={{color:"#374151",fontWeight:500}}>{camp.nombre}</span>
      </div>

      {/* Header card */}
      <div style={{backgroundColor:"white",borderRadius:"16px",border:"1px solid #e5e7eb",padding:"24px",marginBottom:"24px"}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",gap:"16px",flexWrap:"wrap"}}>
          <div>
            <div style={{display:"flex",alignItems:"center",gap:"12px",marginBottom:"8px",flexWrap:"wrap"}}>
              <h1 style={{fontSize:"22px",fontWeight:700,color:"#111827"}}>{camp.nombre}</h1>
              <span style={{padding:"4px 12px",borderRadius:"999px",fontSize:"13px",fontWeight:500,backgroundColor:s.bg,color:s.color}}>
                {camp.estado.replace("_"," ")}
              </span>
            </div>
            <p style={{fontSize:"14px",color:"#6b7280"}}>
              {camp.deporte_detalle?.nombre} — {camp.categoria_detalle?.nombre} ({camp.categoria_detalle?.genero})
            </p>
            <p style={{fontSize:"12px",color:"#9ca3af",marginTop:"4px"}}>
              📅 {new Date(camp.fecha_inicio).toLocaleDateString("es-BO")} → {new Date(camp.fecha_fin).toLocaleDateString("es-BO")}
              {" · "} 🔄 {camp.formato?.replace("_"," ")}
            </p>
          </div>
          {esCoord && (
            <div style={{display:"flex",gap:"8px",flexWrap:"wrap"}}>
              {camp.estado==="INSCRIPCIONES" && totalPartidos===0 && (
                <button onClick={()=>generarFixture.mutate()} disabled={generarFixture.isPending}
                  style={{padding:"8px 16px",borderRadius:"8px",fontSize:"13px",fontWeight:500,
                          color:"white",border:"none",cursor:"pointer",
                          backgroundColor:generarFixture.isPending?"#9ca3af":"#1a6b3c"}}>
                  {generarFixture.isPending?"Generando...":"⚡ Generar fixture"}
                </button>
              )}
              <select value={camp.estado} onChange={e=>cambiarEstado.mutate(e.target.value)}
                style={{padding:"8px 12px",borderRadius:"8px",border:"1px solid #d1d5db",fontSize:"13px",cursor:"pointer"}}>
                <option value="PLANIFICACION">Planificación</option>
                <option value="INSCRIPCIONES">Inscripciones</option>
                <option value="EN_CURSO">En curso</option>
                <option value="FINALIZADO">Finalizado</option>
              </select>
            </div>
          )}
        </div>

        {/* Stats */}
        <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:"16px",marginTop:"20px",
                     paddingTop:"20px",borderTop:"1px solid #f3f4f6"}}>
          {[
            {label:"Equipos inscritos", value:`${totalEquipos}/${camp.max_equipos}`},
            {label:"Partidos totales",  value:totalPartidos},
            {label:"Finalizados",       value:finalizados},
          ].map(s2=>(
            <div key={s2.label} style={{textAlign:"center"}}>
              <p style={{fontSize:"28px",fontWeight:700,color:"#111827"}}>{s2.value}</p>
              <p style={{fontSize:"12px",color:"#9ca3af",marginTop:"2px"}}>{s2.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Equipos */}
      <div style={{marginBottom:"24px"}}>
        <h2 style={{fontSize:"16px",fontWeight:600,color:"#1f2937",marginBottom:"12px"}}>👥 Equipos inscritos</h2>
        {totalEquipos===0 ? (
          <div style={{backgroundColor:"white",borderRadius:"12px",border:"1px solid #e5e7eb",
                       padding:"32px",textAlign:"center",color:"#9ca3af"}}>
            <p style={{fontSize:"13px"}}>No hay equipos inscritos aún.</p>
          </div>
        ) : (
          <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:"12px"}}>
            {(Array.isArray(equipos)?equipos:[]).map((eq:{id:number;nombre:string;facultad:string;color_principal:string})=>(
              <div key={eq.id} style={{backgroundColor:"white",borderRadius:"12px",border:"1px solid #e5e7eb",
                                       padding:"16px",textAlign:"center"}}>
                <div style={{width:"40px",height:"40px",borderRadius:"50%",margin:"0 auto 8px",
                             display:"flex",alignItems:"center",justifyContent:"center",
                             color:"white",fontSize:"14px",fontWeight:700,
                             backgroundColor:eq.color_principal||"#1a6b3c"}}>
                  {eq.nombre.charAt(0)}
                </div>
                <p style={{fontWeight:600,fontSize:"13px",color:"#111827",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{eq.nombre}</p>
                <p style={{fontSize:"11px",color:"#9ca3af",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{eq.facultad}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Partidos recientes */}
      <div style={{marginBottom:"24px"}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"12px"}}>
          <h2 style={{fontSize:"16px",fontWeight:600,color:"#1f2937"}}>📅 Partidos</h2>
          <Link href={`/fixture?campeonato=${id}`} style={{fontSize:"13px",color:"#1a6b3c",textDecoration:"none"}}>Ver todos →</Link>
        </div>
        {totalPartidos===0 ? (
          <div style={{backgroundColor:"white",borderRadius:"12px",border:"1px solid #e5e7eb",
                       padding:"32px",textAlign:"center",color:"#9ca3af"}}>
            <p style={{fontSize:"36px",marginBottom:"8px"}}>📅</p>
            <p style={{fontSize:"13px"}}>No hay fixture generado.</p>
            {esCoord && <p style={{fontSize:"12px",marginTop:"4px"}}>Usa el botón "Generar fixture" arriba.</p>}
          </div>
        ) : (
          <div style={{backgroundColor:"white",borderRadius:"12px",border:"1px solid #e5e7eb",overflow:"hidden"}}>
            {partidos?.results?.slice(0,6).map((p:{id:number;jornada:number;local:string;visitante:string;fecha_hora:string;estado:string})=>(
              <Link key={p.id} href={`/fixture/partido/${p.id}`}
                style={{display:"flex",alignItems:"center",gap:"12px",padding:"12px 16px",
                        borderBottom:"1px solid #f3f4f6",textDecoration:"none",color:"inherit"}}
                onMouseEnter={e=>(e.currentTarget.style.backgroundColor="#f9fafb")}
                onMouseLeave={e=>(e.currentTarget.style.backgroundColor="transparent")}>
                <span style={{fontSize:"12px",color:"#9ca3af",width:"40px",flexShrink:0,fontWeight:500}}>J{p.jornada}</span>
                <div style={{display:"flex",alignItems:"center",gap:"8px",flex:1,minWidth:0}}>
                  <span style={{fontSize:"14px",fontWeight:500,flex:1,textAlign:"right",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{p.local}</span>
                  <span style={{fontSize:"12px",color:"#9ca3af",flexShrink:0}}>vs</span>
                  <span style={{fontSize:"14px",fontWeight:500,flex:1,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{p.visitante}</span>
                </div>
                <div style={{textAlign:"right",flexShrink:0}}>
                  <p style={{fontSize:"12px",color:"#6b7280"}}>{new Date(p.fecha_hora).toLocaleDateString("es-BO",{day:"numeric",month:"short"})}</p>
                  <span style={{fontSize:"11px",padding:"2px 6px",borderRadius:"4px",
                                backgroundColor:p.estado==="FINALIZADO"?"#f0fdf4":"#eff6ff",
                                color:p.estado==="FINALIZADO"?"#15803d":"#1d4ed8"}}>{p.estado}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Quick links */}
      <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:"12px"}}>
        {[
          {href:`/fixture/tabla?campeonato=${id}`, icon:"📊", label:"Tabla posiciones"},
          {href:`/ml?campeonato=${id}`,            icon:"🤖", label:"Predicciones ML"},
          {href:`http://localhost:8000/api/v1/reportes/campeonato/${id}/pdf/`,   icon:"📄", label:"Descargar PDF",   ext:true},
          {href:`http://localhost:8000/api/v1/reportes/campeonato/${id}/excel/`, icon:"📊", label:"Descargar Excel", ext:true},
        ].map(item=>
          item.ext ? (
            <a key={item.href} href={item.href} target="_blank" rel="noopener noreferrer"
              style={{backgroundColor:"white",borderRadius:"12px",border:"1px solid #e5e7eb",
                      padding:"16px",textAlign:"center",textDecoration:"none",display:"block"}}
              onMouseEnter={e=>(e.currentTarget.style.boxShadow="0 4px 12px rgba(0,0,0,0.08)")}
              onMouseLeave={e=>(e.currentTarget.style.boxShadow="none")}>
              <span style={{fontSize:"24px",display:"block",marginBottom:"4px"}}>{item.icon}</span>
              <span style={{fontSize:"13px",fontWeight:500,color:"#374151"}}>{item.label}</span>
            </a>
          ) : (
            <Link key={item.href} href={item.href}
              style={{backgroundColor:"white",borderRadius:"12px",border:"1px solid #e5e7eb",
                      padding:"16px",textAlign:"center",textDecoration:"none",display:"block"}}
              onMouseEnter={e=>(e.currentTarget.style.boxShadow="0 4px 12px rgba(0,0,0,0.08)")}
              onMouseLeave={e=>(e.currentTarget.style.boxShadow="none")}>
              <span style={{fontSize:"24px",display:"block",marginBottom:"4px"}}>{item.icon}</span>
              <span style={{fontSize:"13px",fontWeight:500,color:"#374151"}}>{item.label}</span>
            </Link>
          )
        )}
      </div>
    </div>
  );
}
