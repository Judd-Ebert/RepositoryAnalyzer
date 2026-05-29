import "../App.css";
import { useState } from "react";
import RALogo from "../assets/RALogo.png";
import { useNavigate } from "react-router-dom";


export default function Welcome() {
    const [repoUrl, setRepoUrl] = useState("");
    const [error, setError] = useState("");
    const [toggled, setToggled] = useState(false);
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
            throw new Error("Failed to start ingestion");
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
            <div className="toggle-container">
                <button className={`toggle-button ${toggled ? 'toggled': ' '}`}
                onClick={() => setToggled(!toggled)}>
                    <div className="thumb"></div>
                </button>
                <h4>Use OpenAI API Key?</h4>
            </div>
            <h1>Welcome</h1>
            <h3>Enter your Github Repository URL below</h3>
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



