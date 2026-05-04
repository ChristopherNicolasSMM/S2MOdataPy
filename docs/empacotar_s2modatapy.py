#!/usr/bin/env python3
"""
Script Automatizado para Empacotamento da S2MOdataPy
Autor: Christopher N. S. M. Mauricio
"""
#Empacotar o projeto usando setuptools
#python "C:\Users\...\empacotar_s2modatapy.py"

#Subir versão para o PyPI
#python -m twine upload "C:\Users\...\empacotamento_temp\dist/*"

import os
import sys
import subprocess
import shutil
import re
from pathlib import Path
import time

# ==================================================
# CONFIGURAÇÕES - AJUSTE AQUI SE NECESSÁRIO
# ==================================================
NOME_PACOTE = "s2modatapy"
AUTOR = "Christopher N. S. M. Mauricio"
EMAIL_AUTOR = "christopher.nicolas.mauricio@gmail.com"
GITHUB_URL = "https://github.com/ChristopherNicolasSMM/S2MOdataPy"
# ==================================================

# Cores para terminal (Windows e Unix)
class Cores:
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    AZUL = '\033[94m'
    RESET = '\033[0m'

def print_color(texto, cor=Cores.AZUL):
    print(f"{cor}{texto}{Cores.RESET}")

def executar_comando(comando, descricao):
    
    

    print_color(f"\n📦 {descricao}...", Cores.AZUL)
    try:
        if isinstance(comando, str):
            import shlex
            comando = shlex.split(comando)
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            resultado = subprocess.run(comando, check=True, shell=False, text=True, capture_output=True, encoding='utf-8', env=env)            
        #resultado = subprocess.run(comando, check=True, shell=False, text=True, capture_output=True, encoding='utf-8')
        print_color(f"   ✅ Comando executado com sucesso!", Cores.VERDE)
        return True
    except subprocess.CalledProcessError as e:
        print_color(f"   ❌ Erro: {e.stderr if e.stderr else str(e)}", Cores.VERMELHO)
        return False

def obter_versao_atual(arquivo_pyproject):
    with open(arquivo_pyproject, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    match = re.search(r'version = "([^"]+)"', conteudo)
    return match.group(1) if match else "0.1.0"

def incrementar_versao(arquivo_pyproject, tipo="patch"):
    versao_atual = obter_versao_atual(arquivo_pyproject)
    major, minor, patch = map(int, versao_atual.split('.'))
    if tipo == "major":
        major += 1; minor = 0; patch = 0
    elif tipo == "minor":
        minor += 1; patch = 0
    else:
        patch += 1
    nova_versao = f"{major}.{minor}.{patch}"
    with open(arquivo_pyproject, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    novo_conteudo = re.sub(r'version = "[^"]+"', f'version = "{nova_versao}"', conteudo)
    with open(arquivo_pyproject, 'w', encoding='utf-8') as f:
        f.write(novo_conteudo)
    print_color(f"   📈 Versão atualizada: {versao_atual} → {nova_versao}", Cores.VERDE)
    return nova_versao

def rm_tree(path):
    """Remove diretório com renomeação prévia e retentativas."""
    if not path.exists():
        print_color(f"   ℹ️  Pasta '{path}' já removida.", Cores.AMARELO)
        return
    # Tenta renomear a pasta (quebra lock do Explorer)
    try:
        print_color(f"   🔄 Tentando renomear '{path}' para liberar lock...", Cores.AZUL)
        temp_path = path.with_suffix('.deleteme')
        if temp_path.exists():
            print_color(f"   ⚠️  Pasta temporária '{temp_path}' já existe, removendo...", Cores.AMARELO)
            shutil.rmtree(temp_path, ignore_errors=True)
        path.rename(temp_path)
        path = temp_path
    except Exception:
        print_color(f"   ⚠️  Falha ao renomear, tentando remover diretamente...", Cores.AMARELO)
        pass
    # Agora tenta remover com retentativas
    for _ in range(3):
        try:
            print_color(f"   🗑️  Tentando remover '{path}'...", Cores.AZUL)
            shutil.rmtree(path, ignore_errors=True)
            return
        except PermissionError:
            print_color(f"   ⚠️  Permissão negada, esperando e tentando novamente...", Cores.AMARELO)
            time.sleep(0.5)
    # Última tentativa ignorando qualquer erro
    print_color(f"   🗑️  Tentativa final de remoção de '{path}'...", Cores.AZUL)
    shutil.rmtree(path, ignore_errors=True) 
        
def main():
    print_color("\n" + "="*70, Cores.AZUL)
    print_color(" EMPACOTADOR AUTOMÁTICO - S2MODATAPY ".center(70), Cores.AZUL)
    print_color("="*70, Cores.AZUL)
    print_color(f"\n👤 Autor: {AUTOR}", Cores.AMARELO)
    print_color(f"📦 Pacote: {NOME_PACOTE}", Cores.AMARELO)

    # 1. Localizar biblioteca
    print_color("\n🔍 [1/7] Verificando localização...", Cores.AZUL)
    caminho_biblioteca = Path.cwd() / NOME_PACOTE
    if not caminho_biblioteca.exists():
        print_color(f"   ❌ Pasta '{NOME_PACOTE}' não encontrada!", Cores.VERMELHO)
        sys.exit(1)
    print_color(f"   ✅ Encontrada em: {caminho_biblioteca}", Cores.VERDE)

    # 2. Verificar arquivos essenciais
    print_color("\n📄 [2/7] Verificando arquivos do código...", Cores.AZUL)
    arquivos_essenciais = [
        caminho_biblioteca / "s2modatapy" / "__init__.py",
        caminho_biblioteca / "s2modatapy" / "client.py",
    ]
    for arquivo in arquivos_essenciais:
        if arquivo.exists():
            print_color(f"   ✅ {arquivo.relative_to(caminho_biblioteca)}", Cores.VERDE)
        else:
            print_color(f"   ⚠️  {arquivo.name} não encontrado!", Cores.AMARELO)

    # 3. Versionamento (opcional)
    print_color("\n📈 [3/7] Controle de versão...", Cores.AZUL)
    arquivo_pyproject = caminho_biblioteca / "pyproject.toml"
    if arquivo_pyproject.exists():
        versao_atual = obter_versao_atual(arquivo_pyproject)
        print_color(f"   Versão atual: {versao_atual}", Cores.AMARELO)
        resposta = input("   Incrementar versão? (patch/minor/major/N): ").lower()
        if resposta in ['patch','minor','major']:
            incrementar_versao(arquivo_pyproject, resposta)
        else:
            print_color("   ℹ️  Mantendo versão atual.", Cores.AMARELO)

    # 4. Criar estrutura temporária
    print_color("\n📁 [4/7] Criando estrutura de empacotamento...", Cores.AZUL)
    pasta_temp = Path.cwd() / "empacotamento_temp"
    pasta_src = pasta_temp / "src" / NOME_PACOTE
    if pasta_temp.exists():
        rm_tree(pasta_temp)
    pasta_src.mkdir(parents=True, exist_ok=True)
    print_color(f"   ✅ Estrutura criada em: {pasta_src}", Cores.VERDE)

    # 5. Copiar código da biblioteca
    print_color("\n📦 [5/7] Copiando código...", Cores.AZUL)
    codigo_origem = caminho_biblioteca / "s2modatapy"
    for arquivo in codigo_origem.glob("*.py"):
        shutil.copy2(arquivo, pasta_src / arquivo.name)
        print_color(f"   📄 Copiado: {arquivo.name}", Cores.VERDE)
    for subdir in codigo_origem.iterdir():
        if subdir.is_dir() and subdir.name != "__pycache__":
            shutil.copytree(subdir, pasta_src / subdir.name)
            print_color(f"   📁 Copiada pasta: {subdir.name}/", Cores.VERDE)

    # 6. Copiar arquivos de configuração
    print_color("\n⚙️  [6/7] Copiando configuração...", Cores.AZUL)
    for nome in ["pyproject.toml", "README.md", "LICENSE", "requirements.txt"]:
        origem = caminho_biblioteca / nome
        if origem.exists():
            shutil.copy2(origem, pasta_temp / nome)
            print_color(f"   ✅ {nome} copiado", Cores.VERDE)

    # 7. Build
    print_color("\n🏗️  [7/7] Construindo pacote...", Cores.AZUL)
    python_exe = sys.executable

    # Instalar build (se necessário)
    if executar_comando([python_exe, "-m", "pip", "install", "--upgrade", "build"], "Instalando build"):
        # Muda para a pasta temporária
        os.chdir(pasta_temp)
        print_color(f"   Diretório de build: {os.getcwd()}", Cores.AMARELO)

        # Executa build com captura de saída desabilitada para ver erros
        print_color("   🔨 Executando 'python -m build'...", Cores.AZUL)
        result = subprocess.run([python_exe, "-m", "build"], text=True)
        if result.returncode != 0:
            print_color("   ❌ Falha ao construir pacote!", Cores.VERMELHO)
            sys.exit(1)

        # Verifica se a pasta dist foi gerada
        dist_dir = pasta_temp / "dist"
        if not dist_dir.exists():
            print_color(f"   ❌ Pasta 'dist' não encontrada após o build!", Cores.VERMELHO)
            print_color("   Verifique se há erros no pyproject.toml ou no código.", Cores.AMARELO)
            sys.exit(1)

        print_color(f"\n   📦 Arquivos gerados em: {dist_dir}", Cores.AMARELO)
        for arquivo in dist_dir.iterdir():
            print_color(f"      - {arquivo.name} ({arquivo.stat().st_size/1024:.1f} KB)", Cores.VERDE)



    # 8. Upload para TestPyPI (opcional)
    resposta = input("\n☁️  Deseja fazer upload para o TestPyPI? (s/N): ").lower()
    if resposta in ['s','sim','y','yes']:
        executar_comando([python_exe, "-m", "pip", "install", "--upgrade", "twine"], "Instalando twine")
        resposta2 = input("   Continuar com upload? (s/N): ").lower()
        if resposta2 in ['s','sim','y','yes']:
            
            dist_dir = pasta_temp / "dist"
            #executar_comando([python_exe, "-m", "twine", "upload", "--repository", "testpypi", str(dist_dir / "*")], "Upload para TestPyPI")

            arquivos = [str(p) for p in dist_dir.glob("*") if p.suffix in ('.whl', '.tar.gz')]
            if arquivos:
                executar_comando([python_exe, "-m", "twine", "upload", "--repository", "testpypi"] + arquivos, "Upload para TestPyPI")   
                         

    # Finalização
    print_color("\n" + "="*70, Cores.VERDE)
    print_color(" 🎉 EMPACOTAMENTO CONCLUÍDO! ".center(70), Cores.VERDE)
    print_color("="*70, Cores.VERDE)
    print_color(f"\n📁 Pasta do pacote: {pasta_temp}", Cores.AMARELO)
    print_color(f"📦 Arquivos: {pasta_temp / 'dist'}", Cores.AMARELO)
    print_color("\n🚀 Para publicar no PyPI oficial:")
    print_color(f"   python -m twine upload {pasta_temp / 'dist'}/*", Cores.VERDE)

    resposta_clean = input("\n   Deseja limpar a pasta temporária? (s/N): ").lower()
    if resposta_clean in ['s','sim','y','yes']:
        rm_tree(pasta_temp)
        #shutil.rmtree(pasta_temp, ignore_errors=True)     
        
        print_color("   ✅ Pasta removida.", Cores.VERDE)
        
    

if __name__ == "__main__":
    main()