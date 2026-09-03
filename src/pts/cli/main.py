#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import os
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .. import __version__
from ..core.database import Database
from ..core.snapshot import SnapshotManager
from ..adapters import get_adapter
from ..exceptions import PtsError

console = Console()
logger = logging.getLogger("pts")

@click.group()
@click.version_option(version=__version__, prog_name="pts")
@click.option('--verbose', '-v', is_flag=True, help="Aumenta verbosidade")
@click.option('--db-path', help="Caminho alternativo para o banco de dados")
@click.pass_context
def cli(ctx, verbose, db_path):
    """Proteus Tool Suite - Gerenciador de pacotes universal"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    # Usa o DB_PATH da env se não foi passado
    ctx.obj['db_path'] = db_path or os.environ.get('PTS_DB_PATH')

@cli.command()
@click.argument('packages', nargs=-1, required=True)
@click.pass_context
def install(ctx, packages):
    """Instala um ou mais pacotes"""
    try:
        db_path = ctx.obj.get('db_path')
        adapter = get_adapter()
        db = Database(db_path) if db_path else Database()
        snapman = SnapshotManager(db)
        
        snap_id = snapman.create(
            name=f"pre-install-{'-'.join(packages)}",
            description=f"Snapshot antes de instalar {', '.join(packages)}"
        )
        console.print(f"[yellow]Snapshot automático criado: {snap_id}[/yellow]")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task("Instalando pacotes...", total=len(packages))
            
            for pkg in packages:
                progress.update(task, description=f"Instalando {pkg}...")
                if adapter.is_installed(pkg):
                    console.print(f"[yellow]⚠ {pkg} já está instalado[/yellow]")
                else:
                    adapter.install(pkg)
                progress.advance(task)
        
        console.print(f"[green]✅ {len(packages)} pacote(s) instalado(s) com sucesso[/green]")
        
    except PtsError as e:
        console.print(f"[red]❌ Erro: {e}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('packages', nargs=-1, required=True)
@click.pass_context
def remove(ctx, packages):
    """Remove pacotes"""
    try:
        db_path = ctx.obj.get('db_path')
        adapter = get_adapter()
        db = Database(db_path) if db_path else Database()
        
        for pkg in packages:
            if not adapter.is_installed(pkg):
                console.print(f"[yellow]⚠ {pkg} não está instalado[/yellow]")
                continue
            adapter.remove(pkg)
            console.print(f"[green]✓ {pkg} removido[/green]")
        
    except PtsError as e:
        console.print(f"[red]❌ Erro: {e}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('name', required=False)
@click.option('--description', '-d', help="Descrição do snapshot")
@click.pass_context
def snapshot_create(ctx, name, description):
    """Cria um snapshot do estado atual"""
    try:
        db_path = ctx.obj.get('db_path')
        db = Database(db_path) if db_path else Database()
        snapman = SnapshotManager(db)
        
        snapshot_name = name or f"snapshot-{__import__('datetime').datetime.now().strftime('%Y%m%d-%H%M%S')}"
        snapshot_id = snapman.create(
            name=snapshot_name,
            description=description or "Snapshot manual"
        )
        console.print(f"[green]✅ Snapshot criado: ID={snapshot_id}, Nome={snapshot_name}[/green]")
        
    except PtsError as e:
        console.print(f"[red]❌ Erro ao criar snapshot: {e}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('snapshot_id')
@click.option('--yes', '-y', is_flag=True, help="Assume yes para confirmação")
@click.pass_context
def rollback(ctx, snapshot_id, yes):
    """Restaura um snapshot anterior"""
    if not yes:
        confirm = click.confirm(f"Restaurar snapshot {snapshot_id}? Esta ação é irreversível")
        if not confirm:
            console.print("[yellow]Operação cancelada[/yellow]")
            return
    
    try:
        db_path = ctx.obj.get('db_path')
        db = Database(db_path) if db_path else Database()
        snapman = SnapshotManager(db)
        snapman.restore(snapshot_id)
        console.print(f"[green]✅ Snapshot {snapshot_id} restaurado com sucesso[/green]")
        
    except PtsError as e:
        console.print(f"[red]❌ Erro ao restaurar snapshot: {e}[/red]")
        sys.exit(1)

@cli.command()
@click.pass_context
def snapshot_list(ctx):
    """Lista todos os snapshots disponíveis"""
    try:
        db_path = ctx.obj.get('db_path')
        db = Database(db_path) if db_path else Database()
        snapman = SnapshotManager(db)
        snapshots = snapman.list_all()
        
        if not snapshots:
            console.print("[yellow]Nenhum snapshot encontrado[/yellow]")
            return
        
        table = Table(title="Snapshots Disponíveis")
        table.add_column("ID", style="cyan")
        table.add_column("Nome", style="green")
        table.add_column("Data", style="yellow")
        table.add_column("Descrição", style="white")
        
        for snap in snapshots:
            table.add_row(
                str(snap['id']),
                snap['name'],
                snap['created_at'],
                snap.get('description', '')
            )
        console.print(table)
        
    except PtsError as e:
        console.print(f"[red]❌ Erro ao listar snapshots: {e}[/red]")
        sys.exit(1)

@cli.command()
@click.pass_context
def status(ctx):
    """Mostra o estado atual do sistema"""
    console.print("[bold]Estado do Proteus Tool Suite[/bold]")
    console.print(f"Versão: {__version__}")
    try:
        adapter = get_adapter()
        console.print(f"Distribuição: {type(adapter).__name__}")
    except:
        console.print("Distribuição: Não detectada")
    console.print("Banco de dados: Ativo")
    console.print("[green]Snapshots: OK[/green]")

if __name__ == "__main__":
    cli()
