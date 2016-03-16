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

* then copy `emmet` from `emmet_base` folder in one of the python paths.
* Also install [PyV8](https://github.com/emmetio/pyv8-binaries) in one of the python paths.

###Python Paths

Recommended is **geany config path** which is $HOME/.config/geany/plugins.

OR use geanypy installation path which may be `/usr/local/lib/geany/geanypy` OR `/usr/lib/geany/geanypy`.

OR use python site-packages path

[NOTE: You can find python site-packages path by following command]
    `python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`


* Install *editor.js* and *geanypy-emmet.py* in geany config path OR system geany plugin path [/usr/local/lib/geany]
