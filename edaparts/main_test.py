import pathlib

from kiutils.symbol import SymbolLib
from kiutils.footprint import Footprint
from kiutils.utils import sexpr


expression = sexpr.parse_sexp(
    pathlib.Path("/home/pablintino/Downloads/SparkFun-Aesthetic.kicad_sym").read_text(
        encoding="utf-8"
    )
)
lib_type = expression[0]
if lib_type == "kicad_symbol_lib":
    symbol_lib = SymbolLib().from_sexpr(expression)
    print(symbol_lib)
footprint_lib_name = "Capacitor_SMD"
footprint_lib_models = (
    pathlib.Path("/usr/share/kicad/footprints")
    .joinpath(footprint_lib_name + ".pretty")
    .glob("*.kicad_mod")
)
for footprint_lib_model in [
    Footprint().from_file(path) for path in footprint_lib_models
]:
    print(footprint_lib_model)
