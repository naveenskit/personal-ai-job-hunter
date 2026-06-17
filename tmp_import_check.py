import importlib
import traceback

try:
    m = importlib.import_module('app.matching.routes')
    print('imported', m)
    print('has bp', hasattr(m, 'bp'))
except Exception:
    traceback.print_exc()
