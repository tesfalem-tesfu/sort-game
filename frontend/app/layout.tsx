// app/layout.tsx
import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "bootstrap/dist/css/bootstrap.min.css";
import "./globals.css";

// Theme support
import { ThemeProvider } from "next-themes";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: {
    default: "Sorting Quiz Game",
    template: "%s | Sorting Quiz",
  },
  description: "Fun and educational sorting challenge game – rearrange items into the correct order!",
  keywords: ["sorting game", "quiz", "educational game", "drag and drop", "sorting puzzle"],
  authors: [{ name: "Tesfalem", url: "https://github.com/yourusername" }], // ← update if you have GitHub
  creator: "Tesfalem",
  publisher: "Tesfalem",
  openGraph: {
    title: "Sorting Quiz Game",
    description: "Test your sorting skills in this addictive puzzle game!",
    url: "https://yourdomain.com", // ← change to real domain when deployed
    siteName: "Sorting Quiz",
    images: [
      {
        url: "/og-image.jpg", // ← create this image later (1200×630 recommended)
        width: 1200,
        height: 630,
        alt: "Sorting Quiz Game",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Sorting Quiz Game",
    description: "Fun sorting challenge – can you beat your high score?",
    // images: ["/twitter-image.jpg"], // optional
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#4f46e5" },
    { media: "(prefers-color-scheme: dark)", color: "#312e81" },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        {/* Preconnect to Google Fonts (optional optimization) */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>

      <body
        className={`${inter.variable} font-sans antialiased min-vh-100 d-flex flex-column bg-gradient-to-br from-indigo-950 via-purple-950 to-pink-950 text-white`}
        style={{
          backgroundAttachment: "fixed",
          backgroundSize: "cover",
        }}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {/* Navbar */}
          <nav className="navbar navbar-expand-lg navbar-dark bg-dark bg-opacity-80 shadow-sm sticky-top">
            <div className="container">
              <a className="navbar-brand fw-bold fs-4" href="/">
                Sorting Quiz
              </a>

              <button
                className="navbar-toggler"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#navbarSupportedContent"
                aria-controls="navbarSupportedContent"
                aria-expanded="false"
                aria-label="Toggle navigation"
              >
                <span className="navbar-toggler-icon"></span>
              </button>

              <div className="collapse navbar-collapse" id="navbarSupportedContent">
                <ul className="navbar-nav ms-auto mb-2 mb-lg-0">
                  <li className="nav-item">
                    <a className="nav-link px-3" href="/">
                      Home
                    </a>
                  </li>
                  <li className="nav-item">
                    <a className="nav-link px-3" href="/game">
                      
                    </a>
                  </li>
                  {/* Add more links later: /leaderboard, /about, etc. */}
                </ul>
              </div>
            </div>
          </nav>

          {/* Main content */}
          <main className="flex-grow-1 container py-4 py-md-5">
            {children}
          </main>

          {/* Footer */}
          <footer className="py-4 text-center text-white-50 small bg-dark bg-opacity-60 mt-auto">
            <div className="container">
              <p className="mb-1">
                © {new Date().getFullYear()} Sorting Quiz Game
              </p>
              <p className="mb-0">
                Built with <span className="text-danger">♥</span> in Addis Ababa, Ethiopia
              </p>
            </div>
          </footer>
        </ThemeProvider>
      </body>
    </html>
  );
}