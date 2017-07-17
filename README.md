geanypy-emmet
=============

[Emmet](http://emmet.io/) Plugin for geany based on geanypy.

Plugin Base taken from https://github.com/sergeche/emmet-sublime which is used as submodule.


#### Recommendations
 - [**For Gtk2**]Please use [this](https://github.com/kugel-/geanypy/tree/proxy) *Keybindings* [Included in latest geany-plugins]

 - [**For Gtk3**]Please use [this](https://github.com/sagarchalise/geanypy/tree/proxy-gtk3) *Gtk3 Branch with keybindings*
[**Only applicable if you have installed `geany` building it yourself with `--enable-gtk3` flag.**]

#### Installations
Clone the repository somewhere feasible. [Any place will do]

* Copy/Install *editor.js* and *geanypy-emmet.py* in [*Geany Plugin Path*](#geany-plugin-path)

After  cloning the repository, from inside the repository do:

    `git submodule init`
    `git submodule update`

* then copy `emmet` from `emmet_base` folder in one of the [*Python Paths*](#python-paths).
* Also install python2 [PyV8](https://github.com/emmetio/pyv8-binaries) binaries compatible to your OS in one of the [*Python Paths*](#python-paths).

#### Geany Plugin Path
**use any one path**
    
* `$HOME/.config/geany/plugins`(Recommended)
* `/usr/lib/geany`
* `/usr/local/lib/geany`

#### Python Paths
**use any one path**

* [Geany Plugin Path](#geany-plugin-path)
* `geanypy` base path
* python site-packages path

[NOTE: You can find python site-packages path by following command]
    `python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`



