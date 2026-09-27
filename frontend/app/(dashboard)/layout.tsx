"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/hooks/useAuth";

const NAV = [
  { href: "/dashboard",     icon: "🏠", label: "Inicio" },
  { href: "/campeonatos",   icon: "🏆", label: "Campeonatos" },
  { href: "/fixture",       icon: "📅", label: "Fixture" },
  { href: "/fixture/tabla", icon: "📊", label: "Tabla posiciones" },
  { href: "/ml",            icon: "🤖", label: "Predicciones ML" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { usuario, logout } = useAuth();

  return (
    <div style={{ display:"flex", height:"100vh", overflow:"hidden" }}>
      {/* Sidebar */}
      <aside style={{ width:"224px", backgroundColor:"#0f3d22", display:"flex", flexDirection:"column", flexShrink:0 }}>
        {/* Logo */}
        <div style={{ padding:"20px 16px", borderBottom:"1px solid rgba(255,255,255,0.1)" }}>
          <div style={{ display:"flex", alignItems:"center", gap:"8px" }}>
            <span style={{ fontSize:"24px" }}>⚽</span>
            <div>
              <p style={{ color:"white", fontWeight:700, fontSize:"14px", lineHeight:1 }}>DUBSS</p>
              <p style={{ color:"#34d399", fontSize:"11px" }}>UAGRM</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav style={{ flex:1, padding:"12px 8px", overflowY:"auto" }}>
          {NAV.map(item => {
            const active = pathname === item.href ||
              (item.href !== "/dashboard" && item.href !== "/fixture" && pathname.startsWith(item.href)) ||
              (item.href === "/fixture" && (pathname === "/fixture" || pathname.startsWith("/fixture/partido")));
            return (
              <Link key={item.href} href={item.href}
                style={{
                  display:"flex", alignItems:"center", gap:"12px",
                  padding:"8px 12px", borderRadius:"8px", marginBottom:"2px",
                  fontSize:"14px", textDecoration:"none", transition:"background 0.15s",
                  backgroundColor: active ? "#1a6b3c" : "transparent",
                  color: active ? "white" : "#a7f3d0",
                  fontWeight: active ? 500 : 400,
                }}>
                <span style={{ fontSize:"16px" }}>{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* User */}
        <div style={{ padding:"12px", borderTop:"1px solid rgba(255,255,255,0.1)" }}>
          <div style={{ display:"flex", alignItems:"center", gap:"8px", marginBottom:"8px" }}>
            <div style={{
              width:"28px", height:"28px", borderRadius:"50%", backgroundColor:"#1a6b3c",
              display:"flex", alignItems:"center", justifyContent:"center",
              color:"white", fontSize:"12px", fontWeight:700, flexShrink:0,
            }}>
              {usuario?.nombre_completo?.charAt(0) ?? "U"}
            </div>
            <div style={{ minWidth:0 }}>
              <p style={{ color:"white", fontSize:"12px", fontWeight:500, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>
                {usuario?.nombre_completo ?? "Usuario"}
              </p>
              <p style={{ color:"#34d399", fontSize:"11px" }}>{usuario?.rol}</p>
            </div>
          </div>
          <button onClick={logout}
            style={{ width:"100%", textAlign:"left", fontSize:"12px", color:"#6ee7b7",
                     background:"none", border:"none", cursor:"pointer", padding:"4px 8px", borderRadius:"6px" }}>
            Cerrar sesión
          </button>
        </div>
      </aside>

      {/* Main */}
      <main style={{ flex:1, overflowY:"auto" }}>{children}</main>
    </div>
  );
}
