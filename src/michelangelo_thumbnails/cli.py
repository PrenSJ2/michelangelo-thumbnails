"""argparse-driven CLI for michelangelo-thumbnails."""

from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import pathlib
import sys
import time
import typing
from typing import get_args, get_type_hints

from michelangelo_thumbnails.config import Config
from michelangelo_thumbnails.generator import generate

log = logging.getLogger(__name__)


def _is_literal(t) -> bool:
    return typing.get_origin(t) is typing.Literal


def _add_config_flags(parser: argparse.ArgumentParser) -> None:
    """Auto-derive a --flag for every Config field."""
    hints = get_type_hints(Config)
    for f in dataclasses.fields(Config):
        flag = '--' + f.name.replace('_', '-')
        t = hints.get(f.name, str)

        # Bool: --flag / --no-flag
        if t is bool:
            parser.add_argument(flag, dest=f.name, action='store_true', default=None)
            parser.add_argument('--no-' + f.name.replace('_', '-'), dest=f.name, action='store_false')
            continue

        # Literal: choices
        if _is_literal(t):
            choices = list(get_args(t))
            parser.add_argument(flag, dest=f.name, choices=choices, default=None)
            continue

        # Optional[Literal[...]]
        type_str = str(t)
        if 'Literal' in type_str:
            inner = get_args(t)
            literal = next((a for a in inner if _is_literal(a)), None)
            if literal is not None:
                choices = list(get_args(literal))
                parser.add_argument(flag, dest=f.name, choices=choices, default=None)
                continue

        # int / Optional[int]
        if t is int or 'int' in type_str.lower():
            parser.add_argument(flag, dest=f.name, type=int, default=None)
            continue

        # float / Optional[float]
        if t is float or 'float' in type_str.lower():
            parser.add_argument(flag, dest=f.name, type=float, default=None)
            continue

        # Default: string
        parser.add_argument(flag, dest=f.name, type=str, default=None)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='michelangelo')
    subs = parser.add_subparsers(dest='cmd', required=True)
    g = subs.add_parser('generate', help='Generate a thumbnail')
    g.add_argument('--config', help='JSON file with Config fields (CLI flags override)')
    g.add_argument('--output', '-o', help='Output PNG path')
    g.add_argument('-v', '--verbose', action='count', default=0)
    _add_config_flags(g)
    return parser


def _merge_args(args: argparse.Namespace) -> Config:
    data: dict = {}
    if args.config:
        data.update(json.loads(pathlib.Path(args.config).read_text()))
    for f in dataclasses.fields(Config):
        v = getattr(args, f.name, None)
        if v is not None:
            data[f.name] = v
    return Config.from_dict(data)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.WARNING - 10 * args.verbose,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        stream=sys.stderr,
    )
    if args.cmd == 'generate':
        try:
            cfg = _merge_args(args)
        except TypeError as e:
            print(f'config error: {e}', file=sys.stderr)
            return 2
        output_path = args.output or f'./michelangelo-{int(time.time())}.png'
        try:
            generate(cfg, output_path=output_path)
        except Exception as e:
            log.exception('generation failed')
            print(f'error: {e}', file=sys.stderr)
            return 1
        print(str(pathlib.Path(output_path).resolve()))
        return 0
    return 2


if __name__ == '__main__':
    sys.exit(main())
