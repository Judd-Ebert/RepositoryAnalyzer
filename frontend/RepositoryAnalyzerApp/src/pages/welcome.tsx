import "../App.css";
import { useEffect, useState } from "react";
import RALogo from "../assets/RALogo.png";
import { useNavigate } from "react-router-dom";
import Dropdown from "../components/Dropdown/dropdown";


export default function Welcome() {
    const [repoUrl, setRepoUrl] = useState("");
    const [embeddingApiKey, setEmbeddingApiKey] = useState("");
    const [chatApiKey, setChatApiKey] = useState("");
    const [error, setError] = useState("");
    const [isToggled, setIsToggled] = useState(false);
    
    const EMBEDDING_MODEL_CATALOG: Record<string, string[]> = {
        OpenAI: ["text-embedding-3-large", "text-embedding-3-small"],
        Gemini: ["gemini-embedding-001", "gemini-embedding-2"],
        Ollama: ["ollama-embedding-001"]
    }
    const CHAT_MODEL_CATALOG: Record<string, string[]> = {
        OpenAI: ["gpt-4", "gpt-3.5-turbo"],
        Gemini: ["3.1 Pro", "3.6 Flash"],
        Ollama: ["ollama-4"],
    };

    const [embeddingProvider, setEmbeddingProvider] = useState("OpenAI");

    const [chatProvider, setChatProvider] = useState("OpenAI");
    
    const [embeddingModel, setEmbeddingModel] = useState("text-embedding-3-large");

    const [chatModel, setChatModel] = useState("gpt-4");

    const modelsForEmbeddingProvider = EMBEDDING_MODEL_CATALOG[embeddingProvider] ?? [];

    const modelsForChatProvider = CHAT_MODEL_CATALOG[chatProvider] ?? [];

    interface Option {
        label: string;
        value: string;
    }

    const embeddingProviderOptions: Option[] = Object.keys(EMBEDDING_MODEL_CATALOG).map((provider) => ({
        label: provider,
        value: provider
    }));

    const chatProviderOptions: Option[] = Object.keys(CHAT_MODEL_CATALOG).map((provider) => ({
        label: provider,
        value: provider
    }));

    const embeddingModelOptions: Option[] = modelsForEmbeddingProvider.map((model) => ({
        label: model,
        value: model
    }));

    const chatModelOptions: Option[] = modelsForChatProvider.map((model) => ({
        label: model,
        value: model
    }));
    
    

    useEffect(() => {
        if (!modelsForEmbeddingProvider.includes(embeddingModel)) {
            setEmbeddingModel(modelsForEmbeddingProvider[0] ?? "");
        }
        
    }, [embeddingProvider, embeddingModel, modelsForEmbeddingProvider]
);


    async function fetchOllamaStatus() {
        const response = await fetch("http://127.0.0.1:8000/ollama_Status", {
            method: "GET",
        });
        const data = await response.json();
        console.log(data)
    }


    const navigate = useNavigate();

    function handleToggle() {
        setIsToggled((current) => !current);
        if(!isToggled)
            fetchOllamaStatus();
    }

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

        if (!embeddingApiKey) {
            setError("Please enter your embedding API key.");
            return;
        }
        if (!chatApiKey) {
            setError("Please enter your chat API key.");
            return;
        }

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
        <section className="welcome-page">
            <div className="toggle-overlay">
                <p>Using Ollama?</p>
                <button
                    type="button"
                    className={`toggle-button top-left-toggle ${isToggled ? "toggled" : ""}`}
                    onClick={handleToggle}
                    aria-pressed={isToggled}
                    aria-label="Toggle"
                >
                    <span className="thumb" />
                </button>
            </div>
            <img src={RALogo} alt="Repository Analyzer Logo" className="logo" />
            
            <h1>Welcome</h1>
            <h3>Enter API Keys, models, and github repository URL below</h3>
            <div
            className="info-gathering-section"
            >
                <div
                className="info-gathering-cell"
                >
                    <div
                    className="dropdown-container"
                    >
                        <Dropdown
                            label="Embedding Model Provider"
                            options={embeddingProviderOptions}
                            value={embeddingProvider}
                            onChange={setEmbeddingProvider}
                        />

                        <Dropdown
                            label="Embedding Model"
                            options={embeddingModelOptions}
                            value={embeddingModel}
                            onChange={setEmbeddingModel}
                        />
                    </div>

                    <form className="welcome-form" onSubmit={handleSubmit}>
                        <input type="text"
                        placeholder="Enter your API key"
                        className="input-field"
                        size={40}
                        value={embeddingApiKey}
                        onChange={(e) => setEmbeddingApiKey(e.currentTarget.value)}
                        />
                    </form>

                </div>
                <div
                className="info-gathering-cell"
                >
                    <div
                    className="dropdown-container"
                    >
                        <Dropdown
                            label="Chat Model Provider"
                            options={chatProviderOptions}
                            value={chatProvider}
                            onChange={setChatProvider}
                        />

                        <Dropdown
                            label="Chat Model"
                            options={chatModelOptions}
                            value={chatModel}
                            onChange={setChatModel}
                        />

                    </div>
                    <form className="welcome-form" onSubmit={handleSubmit}>
                        <input type="text"
                        placeholder="Enter your API key"
                        className="input-field"
                        size={40}
                        value={chatApiKey}
                        onChange={(e) => setChatApiKey(e.currentTarget.value)}
                        />
                    </form>
                </div>
            </div>
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



