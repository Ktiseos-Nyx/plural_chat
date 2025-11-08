import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ConfigProvider } from 'antd';
import { ThemeProvider } from "@/components/theme-provider";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Plural Chat - Web Edition",
  description: "Multi-user chat for plural systems with PluralKit integration",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <ThemeProvider defaultTheme="dark" storageKey="plural-chat-theme">
          <ConfigProvider
            theme={{
              token: {
                colorPrimary: '#8b5cf6',
                borderRadius: 8,
              },
            }}
          >
            {children}
          </ConfigProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
