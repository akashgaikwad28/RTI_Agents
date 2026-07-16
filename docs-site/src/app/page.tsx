import Link from 'next/link';
import { ArrowRight, Bot, Database, Shield, Zap, Search, Globe, Code } from 'lucide-react';

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center bg-zinc-950 text-slate-50 overflow-hidden font-sans">
      {/* Background gradients */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))]" />
      
      {/* Hero Section */}
      <section className="relative z-10 flex flex-col items-center justify-center pt-32 pb-20 px-6 text-center lg:pt-48 lg:pb-32">
        <div className="inline-flex items-center rounded-full border border-zinc-800 bg-zinc-900/50 px-3 py-1 text-sm font-medium text-zinc-300 mb-8 backdrop-blur-md">
          <span className="flex h-2 w-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span>
          Enterprise-Grade RTI Automation
        </div>
        
        <h1 className="bg-gradient-to-br from-white to-zinc-500 bg-clip-text text-5xl font-extrabold tracking-tight text-transparent sm:text-7xl lg:text-8xl max-w-5xl">
          AI-Powered Transparency
        </h1>
        
        <p className="mt-8 max-w-2xl text-lg text-zinc-400 sm:text-xl">
          A multi-agent automation platform designed to streamline the Right to Information process in India. Built with LangGraph, FastAPI, and advanced Retrieval-Augmented Generation.
        </p>
        
        <div className="mt-10 flex flex-col sm:flex-row gap-4">
          <Link
            href="/docs"
            className="inline-flex h-12 items-center justify-center rounded-md bg-white px-8 text-sm font-medium text-zinc-950 transition-colors hover:bg-zinc-200 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 disabled:pointer-events-none disabled:opacity-50"
          >
            Explore the Docs
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
          <a
            href="https://github.com/akashgaikwad28/RTI_Agents"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex h-12 items-center justify-center rounded-md border border-zinc-800 bg-zinc-950 px-8 text-sm font-medium text-white transition-colors hover:bg-zinc-900 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950"
          >
            <svg
              className="mr-2 h-4 w-4"
              fill="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                clipRule="evenodd"
              />
            </svg>
            View Repository
          </a>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 w-full max-w-7xl px-6 py-20 lg:py-32">
        <div className="mb-16 text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">System Capabilities</h2>
          <p className="mt-4 text-zinc-400">Architected for scale, precision, and security.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <FeatureCard 
            icon={<Bot className="h-6 w-6 text-blue-400" />}
            title="Multi-Agent Orchestration"
            description="LangGraph-powered agents specializing in formatting, translation, classification, and execution."
          />
          <FeatureCard 
            icon={<Globe className="h-6 w-6 text-emerald-400" />}
            title="Multilingual Support"
            description="Process queries in multiple Indian languages utilizing dynamic translation and transliteration."
          />
          <FeatureCard 
            icon={<Search className="h-6 w-6 text-amber-400" />}
            title="Hybrid RAG Pipeline"
            description="Incremental ingestion from PDFs and government sites, coupled with OCR and FAISS semantic search."
          />
          <FeatureCard 
            icon={<Zap className="h-6 w-6 text-purple-400" />}
            title="Proactive Interception"
            description="Scans government portals to deliver instant answers if data is already publicly available."
          />
          <FeatureCard 
            icon={<Shield className="h-6 w-6 text-rose-400" />}
            title="Security & Guardrails"
            description="Built-in PII masking, response sanitization, and hallucination detection for safe outputs."
          />
          <FeatureCard 
            icon={<Database className="h-6 w-6 text-cyan-400" />}
            title="State Checkpointing"
            description="MongoDB and Redis integration for Human-in-the-Loop pauses, rate limiting, and semantic caching."
          />
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="relative z-10 w-full max-w-7xl px-6 py-20 lg:py-32 border-t border-zinc-800">
        <div className="flex flex-col md:flex-row gap-12 items-center">
          <div className="w-full md:w-1/2">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-6">Modern Tech Stack</h2>
            <p className="text-zinc-400 mb-6 text-lg">
              The RTI-Agent leverages a bleeding-edge stack tailored for high-performance AI orchestration and enterprise security.
            </p>
            <ul className="space-y-4">
              <li className="flex items-center">
                <div className="bg-zinc-900 p-2 rounded-md mr-4 border border-zinc-800">
                  <Code className="h-5 w-5 text-white" />
                </div>
                <div>
                  <span className="font-semibold text-white">Frameworks:</span> 
                  <span className="text-zinc-400 ml-2">LangChain, LangGraph, FastAPI, Next.js</span>
                </div>
              </li>
              <li className="flex items-center">
                <div className="bg-zinc-900 p-2 rounded-md mr-4 border border-zinc-800">
                  <Bot className="h-5 w-5 text-white" />
                </div>
                <div>
                  <span className="font-semibold text-white">LLMs:</span> 
                  <span className="text-zinc-400 ml-2">Groq (Llama 3), Google Gemini, OpenAI</span>
                </div>
              </li>
              <li className="flex items-center">
                <div className="bg-zinc-900 p-2 rounded-md mr-4 border border-zinc-800">
                  <Database className="h-5 w-5 text-white" />
                </div>
                <div>
                  <span className="font-semibold text-white">Databases:</span> 
                  <span className="text-zinc-400 ml-2">MongoDB, Redis, FAISS, MongoDB Atlas Vector</span>
                </div>
              </li>
            </ul>
          </div>
          <div className="w-full md:w-1/2 bg-zinc-900/50 border border-zinc-800 rounded-2xl p-8 backdrop-blur-sm">
             <div className="font-mono text-sm text-zinc-300">
              <div className="flex items-center gap-2 mb-4 border-b border-zinc-800 pb-4">
                <div className="h-3 w-3 rounded-full bg-rose-500"></div>
                <div className="h-3 w-3 rounded-full bg-amber-500"></div>
                <div className="h-3 w-3 rounded-full bg-emerald-500"></div>
              </div>
              <pre className="overflow-x-auto text-emerald-400">
{`version: '3.8'
services:
  api:
    build: ./backend
    ports: ["8000:8000"]
    depends_on:
      - redis
      - mongo
  frontend:
    build: ./frontend
    ports: ["3001:3001"]
  redis:
    image: redis:alpine
  mongo:
    image: mongo:latest`}
              </pre>
             </div>
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="w-full border-t border-zinc-900 py-8 text-center text-sm text-zinc-500">
        <p>Built to empower transparency and citizen access to public information in India.</p>
      </footer>
    </main>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="flex flex-col rounded-2xl border border-zinc-800 bg-zinc-900/40 p-6 backdrop-blur-sm transition-all hover:bg-zinc-900/80 hover:border-zinc-700">
      <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-zinc-950 border border-zinc-800">
        {icon}
      </div>
      <h3 className="mb-2 text-xl font-semibold text-white">{title}</h3>
      <p className="text-zinc-400">{description}</p>
    </div>
  );
}
