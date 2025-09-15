import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { headers } from 'next/headers';
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "The Third Voice",
  description: "Your AI companion for emotionally intelligent communication",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Get the host from the headers to build a dynamic URL
  const headersList = await headers();
  const host = headersList.get('host');
  const dynamicUrl = `https://${host}`;

  return (
    <html lang="en">
      <head>
        {/* PWA Manifest */}
        <link rel="manifest" href="/manifest.json" />
        {/* Theme color */}
        <meta name="theme-color" content="#000000" />
        {/* iOS support */}
        <link rel="apple-touch-icon" href="/icon-192.png" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        {/* Open Graph Meta Tags for Social Media Sharing */}
        <meta property="og:title" content="The Third Voice" />
        <meta property="og:description" content="Your AI companion for emotionally intelligent communication." />
        <meta property="og:image" content="/icon-512.png" />
        <meta property="og:url" content={dynamicUrl} />
        <meta property="og:type" content="website" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}