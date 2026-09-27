import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "DUBSS — Sistema de Gestión Deportiva",
  description: "Sistema Inteligente de Gestión Deportiva UAGRM",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className={`${inter.variable} font-sans bg-gray-50 text-gray-900`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
