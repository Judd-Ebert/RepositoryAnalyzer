import "../App.css";
import { useEffect, useState } from "react";
import RALogo from "../assets/RALogo.png";
import { useNavigate } from "react-router-dom";


export default function Welcome() {
    const [repoUrl, setRepoUrl] = useState("");
    const [embeddingApiKey, setApiKey] = useState("");
    const [chatApiKey, setChatApiKey] = useState("");
    const [chatModel, setChatModel] = useState("");
    const [error, setError] = useState("");
    
    const EMBEDDING_MODEL_CATALOG: Record<string, string[]> = {
        OpenAI: ["text-embedding-3-large", "text-embedding-3-small"],
        Gemini: ["gemini-embedding-001", "gemini-embedding-2"]
    }
    
    const [embeddingProvider, setEmbeddingProvider] = useState("OpenAI");
    
    const [embeddingModel, setEmbeddingModel] = useState("text-embedding-3-large");

    const modelsForEmbeddingProvider = EMBEDDING_MODEL_CATALOG[embeddingProvider] ?? [];

    useEffect(() => {
        if (!modelsForEmbeddingProvider.includes(embeddingModel)) {
            setEmbeddingModel(modelsForEmbeddingProvider[0] ?? "");
        }
        
    }, [embeddingProvider, embeddingModel, modelsForEmbeddingProvider]
);






    const navigate = useNavigate();

    function isValidGithubUrl(url: string): boolean {
    try {
        const u = new URL(url.trim());
        if (u.protocol !== "https:") return false; //! Should I show the user this error?
        if (u.hostname !== "github.com") return false; //! Should I show the user this error?
        const parts = u.pathname.split("/").filter(Boolean);
        return parts.length >= 2; // needs at least /owner/repo
    } catch {
        return false;
    }
    
    }

    async function handleSubmit(e: React.FormEvent) {
        
        e.preventDefault();
        if (!isValidGithubUrl(repoUrl)) {
            setError("Please enter a valid Github repository URL.");
            return;
        }
        setError("");

        const response = await fetch("http://127.0.0.1:8000/ingest", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ github_url: repoUrl.trim() }),
        });

        if (!response.ok) {
            const err = await response.json()
            throw new Error(err?.detail?.message ?? "Ingestion failed :(");
        }
        else {
            console.log("Ingestion started successfully");
            const data = await response.json();
            navigate("/loading",{state: { repoUrl, job: data}})
        }

        

        // Nav after call
    }


    return (
        <section>
            <img src={RALogo} alt="Repository Analyzer Logo" className="logo" />
            
            <h1>Welcome</h1>
            <h3>Enter API Keys, models, and github repository URL below</h3>
            <label className="selector-label">Embedding Model Provider</label>
            <select
            className="selector-input"
            value={embeddingProvider}
            onChange={(e) => setEmbeddingProvider(e.currentTarget.value)}
            
            >
                {Object.keys(EMBEDDING_MODEL_CATALOG).map((p) => (
                    <option key={p} value={p}>{p}</option>
                ))}
            </select>

            <label className="selector-label">Embedding Model</label>
            <select
            className="selector-input"
            value={embeddingModel}
            onChange={(e) => setEmbeddingModel(e.currentTarget.value)}
            >
                {modelsForEmbeddingProvider.map((m) => (
                    <option key={m} value={m}>{m}</option>
                ))}
            </select>
            <form className="welcome-form" onSubmit={handleSubmit}>
                <input type="text"
                placeholder="https://github.com/owner/repo"
                className="input-field"
                size={40}
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.currentTarget.value)}
                />
                <button type="submit" className="submit-button">Analyze Repository</button>
            </form>
            
            {error && <p className="error-message">{error}</p>}
        </section>
    )
}



