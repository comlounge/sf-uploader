from starflyer import Module, Application
from sfext.uploader import upload_module
import py.path


def pytest_funcarg__simple_app(request):
    """create the simplest app with uploader support ever"""

    class MyApp(Application):
        """test app with uploader"""
        modules = [
            upload_module(),
        ]

    return MyApp(__name__)


def pytest_funcarg__testimage(request):
    p = py.path.local(request.fspath)
    return p.dirpath().join("assets/logo.png")

