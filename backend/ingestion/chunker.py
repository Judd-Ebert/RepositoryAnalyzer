"""
Judd Ebert 3/15/2026
Splits up files into pieces
Needs to
    Read files from temp
    skip .git
    skip node_modules
    collect code

use os.walk() to go through code, using a Denylist(.png, .exe, etc.) and then use a try/except UnicodeDecodeError when reading for edge cases
For each file, check suffix to find language and give to LangChain. If language not recognized, use a general splitter
Split with LangChain RecursiveCharacterTextSplitter, lang aware if possible
Attatch metadata to each chunk(file_path, language, start_line)
Find start_line using:
    start_char = content.find(chunk_text)
    start_line = content[:start_char].count("\n") + 1
Return a dict of chunks

"""

from langchain_text_splitters import (Language, RecursiveCharacterTextSplitter )
import os

supported_languages_map = {
    'cpp': 'CPP',
    'go': 'GO',
    'java': 'JAVA',
    'kt': 'KOTLIN',
    'js': 'JS',
    'ts': 'TS',
    'php': 'PHP',
    'proto': 'PROTO',
    'py': 'PYTHON',
    'rst': 'RST',
    'rb': 'RUBY',
    'rs': 'RUST',
    'scala': 'SCALA',
    'swift': 'SWIFT',
    'md': 'MARKDOWN',
    'tex': 'LATEX',
    'html': 'HTML',
    'sol': 'SOL',
    'cs': 'CSHARP',
    'cbl': 'COBOL',
    'c': 'C',
    'lua': 'LUA',
    'pl': 'PERL',
    'hs': 'HASKELL',
    'ex': 'ELIXIR',
    'ps1': 'POWERSHELL',
    'vbs': 'VISUALBASIC6',
    'r': 'R',
}

unsupported_file_types = [
    # Compiled Binaries & Executables
    '.exe', '.dll', '.so', '.dylib', '.bin', '.out', '.app', '.msi', '.com',
  
    # Compiled Code & Bytecode
    '.class', '.pyc', '.pyo', '.pyd', '.o', '.obj', '.a', '.lib', '.node',
  
    # Archives & Compressed Files
    '.zip', '.tar', '.gz', '.7z', '.rar', '.iso', '.dmg', '.pkg', '.bz2', '.xz',
  
    # Images & Graphics
    '.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.bmp', '.tiff', '.psd', '.ai',
  
    # Video & Audio
    '.mp4', '.mkv', '.mov', '.avi', '.mp3', '.wav', '.flac', '.aac', '.ogg',
  
    # Documents (Proprietary/Binary)
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
  
    # Databases & Objects
    '.sqlite', '.db', '.mdb', '.pdb', '.pkl', '.pickle', '.h5', '.parquet',
  
    # Fonts
    '.ttf', '.otf', '.woff', '.woff2', '.eot'

]

unsupported_directory_types = [
    # Version Control
    '.git', '.svn', '.hg', '.fossil',
    
    # Dependency Managers (Massive file counts)
    'node_modules', 'bower_components', 'vendor', '.venv', 'env', 'venv', 
    
    # Build & Output Folders
    'dist', 'build', 'out', 'target', 'bin', 'obj', '.next', '.nuxt',
    
    # Cache & Temporary Files
    '.cache', '.sass-cache', '.eslintcache', '.parcel-cache', 'tmp', 'temp',
    
    # IDE & Editor Metadata
    '.idea', '.vscode', '.vs', '.settings', '.project', '.classpath',
    
    # Testing & Coverage
    'coverage', '.nyc_output',
    
    # OS Metadata
    '.DS_Store', 'Thumbs.db'
]


CHUNK_SIZE = 512
CHUNK_OVERLAP = 64

def walk_through_files(root_path: str):
    file_paths = []
    for directorypath, directorynames, filenames in os.walk(root_path):
        directorynames[:] = [d for d in directorynames if d not in unsupported_directory_types]
        for file_path in filenames:
            if os.path.splitext(file_path)[1] not in unsupported_file_types:
                file_paths.append(os.path.join(directorypath, file_path)) 
    return file_paths

def chunk_file(file_path: str) -> list[dict]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError:
        return []
    indexed_chunks = []
    suffix = os.path.splitext(file_path)[1].lstrip(".")
    if suffix in supported_languages_map:
        file_language = (supported_languages_map[suffix])
        text_splitter = RecursiveCharacterTextSplitter(language=Language[file_language], chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    else:
        file_language = "Unknown"
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    raw_chunks = text_splitter.split_text(text)
    for chunk in raw_chunks:
        start_char = text.find(chunk)
        start_line = text[:start_char].count("\n") + 1
        indexed_chunks.append({
            "text": chunk,
            "file_path": file_path,
            "language": file_language,
            "start_line": start_line
        })
    return indexed_chunks
    
def chunk_repository(root_path: str):
    chunks = []
    paths = walk_through_files(root_path)
    for path in paths:
        chunks.extend(chunk_file(path))
    return chunks