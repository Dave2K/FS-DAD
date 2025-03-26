import os
import subprocess
from pathlib import Path

# Configurazione
SOLUTION_NAME = "FlexCore.All.sln"
ROOT_DIR = Path(".")  # Cartella radice (cambia se necessario)
SRC_DIR = "src"       # Cartella sorgenti
TEST_DIR = "tests"    # Cartella test

def run_command(command):
    """Esegue un comando shell e gestisce gli errori"""
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione: {e}")
        exit(1)

def generate_solution():
    # Crea/resetta la soluzione
    if os.path.exists(SOLUTION_NAME):
        os.remove(SOLUTION_NAME)
    run_command(f"dotnet new sln -n {SOLUTION_NAME[:-4]}")

    # Aggiunge progetti con cartelle virtuali
    for folder, virtual_folder in [(SRC_DIR, "Source"), (TEST_DIR, "Tests")]:
        for csproj in Path(ROOT_DIR, folder).rglob("*.csproj"):
            # Percorso relativo per la soluzione
            rel_path = str(csproj.relative_to(ROOT_DIR))
            
            # Aggiunge il progetto alla soluzione
            run_command(f"dotnet sln {SOLUTION_NAME} add {rel_path}")
            
            # Crea struttura cartelle virtuali
            parts = csproj.parent.relative_to(ROOT_DIR / folder).parts
            if parts:
                virtual_path = "\\".join([virtual_folder] + list(parts[:-1]))
                run_command(
                    f"dotnet sln {SOLUTION_NAME} slnfolders add "
                    f'"{virtual_path}" "{csproj.parent.name}"'
                )

    print(f"\n✅ Soluzione {SOLUTION_NAME} generata con successo!")
    print("Struttura cartelle virtuali:")
    run_command(f"dotnet sln {SOLUTION_NAME} slnfolders list")

if __name__ == "__main__":
    print("🗃️  Generazione soluzione Visual Studio...")
    generate_solution()