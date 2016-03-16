geanypy-emmet
=============

[Emmet](http://emmet.io/) Plugin for geany based on geanypy.

Plugin Base taken from https://github.com/sergeche/emmet-sublime which is used as submodule.


####Recommendations
[**For Gtk2**]Please use [this](https://github.com/kugel-/geanypy/tree/proxy) *Keybindings* [Included in latest geany-plugins]

[**For Gtk3**]Please use [this](https://github.com/sagarchalise/geanypy/tree/proxy-gtk3) *Gtk3 Branch with keybindings*

####Installations
After  cloning the repository, from inside the repository do:

    `git submodule init`
    `git submodule update`

* then install `emmet` from `emmet_base` folder geanypy library path OR on Python site package directory or config path.
* Also install [PyV8](https://github.com/emmetio/pyv8-binaries) to geanypy library path OR on Python site package directory or config path.

[NOTE: You can find python site package path by following command]
    `python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`

_geanypy library path may be `/usr/local/lib/geany/geanypy` OR `/usr/lib/geany/geanypy` based on installation._

* Install *editor.js* and *geanypy-emmet.py* in system geany plugin path [/usr/local/lib/geany] or config path  i.e $HOME/.config/geany/plugins
