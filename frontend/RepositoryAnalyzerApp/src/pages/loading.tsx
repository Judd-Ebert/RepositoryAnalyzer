import "../App.css";
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { JobId } from "../config/types";

export function Loading() {
  const navigate = useNavigate();
  const { job } = useLocation().state as { job: JobId };
  const jobId = job.job_id;
  const githubUrl = job.github_url;
  async function fetchJobStatus(jobId: string) {
    const response = await fetch("http://127.0.0.1:8000/job_status", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ job_id: jobId }),
    });

    if (!response.ok) {
      console.error("Failed to fetch job status");
      return;
    }

    const data = await response.json();
    console.log("Job status:", data);
  }

  useEffect(() => {
    const interval = setInterval(() => {
      fetchJobStatus(jobId);
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId]);

  fetchJobStatus("your-job-id-here"); // Replace with the actual job ID you want to check
  return (
    <div className="loading-container">
      <h1>Loading...</h1>
      <p>Please wait while we process your request.</p>
    </div>
  );
}
