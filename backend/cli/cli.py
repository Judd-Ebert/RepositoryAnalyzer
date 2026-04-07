import click
import shutil

from backend.ingestion.cloner import clone_repo
from backend.ingestion.chunker import chunk_repository
from backend.ingestion.embedder import embed_chunks
from backend.ingestion.indexer import build_index
from backend.search.retriever import retrieve
from backend.llm.explainer import explain


@click.group()
def cli():
    """Repository Analyzer CLI"""
    pass

@cli.command()
@click.argument("github_url")
def ingest(github_url: str):
    """Clones, chunks, embeds, and indexes a repo URL"""
    local_path = None
    try:
        click.echo("Cloning Repo")
        local_path = clone_repo

        click.echo("Chunking files")
        chunks = chunk_repository(local_path)
        if not chunks:
            raise click.ClickException("No text chunks found")
        
        click.echo(f"Embedding {len(chunks)} chunks")
        chunks = embed_chunks(chunks)

        click.echo("Building index")
        repo_id = build_index(chunks, github_url)

        click.echo(f"Completed - Repo ID: {repo_id}")
        click.echo(f"Indexed {len(chunks)} chunks")
    except Exception as e:
        raise click.ClickException(str(e))
    finally:
        if local_path:
            shutil.rmtree(local_path, ignore_errors=True) #Deletes temp stuff

@cli.command()
@click.argument("repo_id")
@click.argument("question")
@click.option("--top-k", default=8, show_default=True, type=int)
def ask(repo_id: str, question: str, top_k: int):
    """Ask a question about an already indexed repo"""
    try:
        chunks = retrieve(repo_id=repo_id, question=question, top_k=top_k)
        if not chunks:
            raise click.ClickException("No chunks found")
        
        result = explain(question=question, chunks=chunks)

        click.echo("\nAnswer:\n")
        click.echo(result["answer"])

        click.echo("\nSources:\n")

        seen = set()
        for s in result["sources"]:
            key = (s["file_path"], s["start_line"])
            if key in seen:
                continue 
            seen.add(key)
            click.echo(f"- {s['file_path']}:{s['start_line']}")
    except Exception as e:
        raise click.ClickException(str(e))
    
if __name__ == "__main__":
    cli()