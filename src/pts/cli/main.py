#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import click
from rich.console import Console

from .. import __version__

console = Console()

@click.group()
@click.version_option(version=__version__, prog_name="pts")
def cli():
    """Proteus Tool Suite - Gerenciador de pacotes universal"""
    pass

@cli.command()
@click.argument('packages', nargs=-1, required=True)
def install(packages):
    """Instala um ou mais pacotes"""
    console.print(f"[green]Instalando: {', '.join(packages)}[/green]")

@cli.command()
@click.argument('packages', nargs=-1, required=True)
def remove(packages):
    """Remove pacotes"""
    console.print(f"[yellow]Removendo: {', '.join(packages)}[/yellow]")

@cli.command()
@click.option('--name', help="Nome do snapshot")
def snapshot_create(name):
    """Cria um snapshot"""
    console.print(f"[green]Snapshot criado: {name or 'sem nome'}[/green]")

@cli.command()
@click.argument('snapshot_id')
def rollback(snapshot_id):
    """Restaura um snapshot"""
    console.print(f"[yellow]Restaurando snapshot: {snapshot_id}[/yellow]")

if __name__ == "__main__":
    cli()
