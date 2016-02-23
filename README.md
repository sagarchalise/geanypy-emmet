geanypy-emmet
=============

[Emmet](http://emmet.io/) Plugin for geany based on geanypy.

Plugin Base taken from https://github.com/sergeche/emmet-sublime which is used as submodule.


####Recommendations
[**For Gtk2**]Please use [this](https://github.com/kugel-/geanypy/tree/proxy) *Keybindings*

[**For Gtk3**]Please use [this](https://github.com/sagarchalise/geanypy/tree/proxy-gtk3) *Gtk3 Branch with keybindings*

####Installations

* Install `emmet` from `emmet_base` folder and [PyV8](https://github.com/emmetio/pyv8-binaries) to geanypy library path OR on Python site package directory:

    `python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`

_geanypy library path may be `/usr/local/lib/geany/geanypy` OR `/usr/lib/geany/geanypy` based on installation._

* Install *editor.js* and *geanypy-emmet.py* in system geany plugin path [/usr/local/lib/geany]
