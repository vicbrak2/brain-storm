"""CLI de fable-forge.

Uso (desde fable-forge/):

    python -m fable_forge new -m "no hay que mentir" -a "6-8 años" -t "humor tierno"
    python -m fable_forge new -m "pedir ayuda no es debilidad" -a "9-12" -t "aventura" --serie bosque-gris
    python -m fable_forge variant output/fables/20260705-....md --tipo verso
    python -m fable_forge series list
    python -m fable_forge series show bosque-gris

Requiere credenciales de Anthropic en el entorno (ANTHROPIC_API_KEY o un
perfil de `ant auth login`).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import client, prompts, storage


def _cmd_new(args: argparse.Namespace) -> int:
    serie_ctx = None
    if args.serie:
        serie_ctx = storage.load_series(args.serie)
        if serie_ctx:
            n = len(serie_ctx["fabulas"])
            print(
                f"Serie '{args.serie}': {n} fábula(s) previa(s), "
                f"{len(serie_ctx['personajes'])} personaje(s) conocido(s).",
                file=sys.stderr,
            )
        else:
            print(f"Serie '{args.serie}': nueva (primera entrega).", file=sys.stderr)

    user_prompt = prompts.build_user_prompt(
        moraleja=args.moraleja,
        audiencia=args.audiencia,
        tono=args.tono,
        idioma=args.idioma,
        longitud=args.longitud,
        serie=serie_ctx,
        extra=args.extra,
    )
    print("Generando fábula con claude-fable-5…", file=sys.stderr)
    fable = client.generate(prompts.SYSTEM_PROMPT, user_prompt, max_tokens=args.max_tokens)

    path = storage.save_fable(fable)
    if args.serie:
        storage.update_series(args.serie, fable)

    print(fable)
    print(f"\nGuardada en: {path}", file=sys.stderr)
    return 0


def _cmd_variant(args: argparse.Namespace) -> int:
    source = Path(args.archivo)
    if not source.exists():
        print(f"No existe el archivo: {source}", file=sys.stderr)
        return 1
    original = source.read_text(encoding="utf-8")

    user_prompt = prompts.build_variant_prompt(original, args.tipo)
    print(f"Generando variante '{args.tipo}' con claude-fable-5…", file=sys.stderr)
    result = client.generate(
        prompts.VARIANT_SYSTEM_PROMPT, user_prompt, max_tokens=args.max_tokens
    )

    path = storage.save_fable(result, suffix=args.tipo)
    print(result)
    print(f"\nGuardada en: {path}", file=sys.stderr)
    return 0


def _cmd_series(args: argparse.Namespace) -> int:
    if args.accion == "list":
        nombres = storage.list_series()
        if not nombres:
            print("No hay series todavía.")
        for nombre in nombres:
            print(nombre)
        return 0

    # show
    if not args.nombre:
        print("Falta el nombre de la serie: series show <nombre>", file=sys.stderr)
        return 1
    serie = storage.load_series(args.nombre)
    if serie is None:
        print(f"No existe la serie '{args.nombre}'.", file=sys.stderr)
        return 1
    print(f"Serie: {serie['nombre']}")
    if serie.get("escenario"):
        print(f"Escenario: {serie['escenario']}")
    print("\nPersonajes:")
    for p in serie["personajes"]:
        rasgos = ", ".join(p.get("rasgos", []))
        print(f"  - {p.get('nombre')} ({p.get('especie')}): {rasgos}")
    print("\nFábulas:")
    for i, f in enumerate(serie["fabulas"], 1):
        print(f"  {i}. {f.get('titulo')}")
        if f.get("moraleja"):
            print(f"     Moraleja: {f['moraleja']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fable-forge",
        description="Generador de fábulas interactivas con claude-fable-5.",
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p_new = sub.add_parser("new", help="Generar una fábula nueva")
    p_new.add_argument("-m", "--moraleja", required=True, help="Moraleja o tema")
    p_new.add_argument("-a", "--audiencia", required=True, help='Audiencia (ej. "6-8 años")')
    p_new.add_argument("-t", "--tono", required=True, help='Tono (ej. "humor tierno")')
    p_new.add_argument("--idioma", help="Idioma de la fábula (default: español neutro)")
    p_new.add_argument("--longitud", help='Longitud pedida (ej. "muy corta")')
    p_new.add_argument("--serie", help="Nombre de serie con personajes recurrentes")
    p_new.add_argument("--extra", help="Indicaciones adicionales libres")
    p_new.add_argument("--max-tokens", type=int, default=client.DEFAULT_MAX_TOKENS)
    p_new.set_defaults(func=_cmd_new)

    p_var = sub.add_parser("variant", help="Reformatear una fábula existente")
    p_var.add_argument("archivo", help="Ruta al .md de la fábula original")
    p_var.add_argument(
        "--tipo",
        required=True,
        choices=sorted(prompts.VARIANTS),
        help="Tipo de variante",
    )
    p_var.add_argument("--max-tokens", type=int, default=client.DEFAULT_MAX_TOKENS)
    p_var.set_defaults(func=_cmd_variant)

    p_ser = sub.add_parser("series", help="Consultar series")
    p_ser.add_argument("accion", choices=["list", "show"])
    p_ser.add_argument("nombre", nargs="?", help="Nombre de la serie (para show)")
    p_ser.set_defaults(func=_cmd_series)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except client.RefusalError as exc:
        print(f"Pedido declinado: {exc}", file=sys.stderr)
        return 2
    except client.FableForgeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
