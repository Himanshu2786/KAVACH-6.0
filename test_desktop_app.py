"""Root compatibility shim for tests/test_desktop_app.py"""
import runpy, sys, os
sys.path.insert(0, os.path.dirname(__file__))
runpy.run_path(os.path.join(os.path.dirname(__file__), "tests", "test_desktop_app.py"), run_name="__main__")
