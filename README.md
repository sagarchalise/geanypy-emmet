geanypy-emmet
=============

[Emmet](http://emmet.io/) Plugin for geany based on geanypy.

Plugin Base taken from https://github.com/sergeche/emmet-sublime which is used as submodule.


####Recommendations
Please use [geanypy](https://github.com/sagarchalise/geanypy/tree/gtk3) *Gtk3 Branch*

**You can get gtk2 as well gtk3 compatible codebase as well as keybinding support by default.**

####Installations

* Install `emmet` from `emmet_base` folder and [PyV8](https://github.com/emmetio/pyv8-binaries) to geanypy library path OR on Python site package directory:

    `python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`

_geanypy library path may be `/usr/local/lib/geany/geanypy` OR `/usr/lib/geany/geanypy` based on installation._

* Install geanypy-emmet.py and editor.js on `$HOME/.config/geany/plugins/geanypy/plugins` OR `/your_geany_config_path/plugins/geanypy/plugins`