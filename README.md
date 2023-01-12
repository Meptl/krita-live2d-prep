# Live2D Prep plugin

  This plugin prepares the Krita document for use in Live2D Cubism.
  It does the following:
  <ul>
    <li>Merges all group layers that do not contain other groups.</li>
    <li>Maintains the group heirarchy.</li>
    <li>Saves every visible top-level node into a psd file of the same name</li>
  </ul>
Krita plugin that prepares a document for use in Live2D.

It does the following:
* Merges all layers that consist of only paint layers whilst maintaining group heirarchy
* Saves every visible top-level node into a psd file of the same name

## Usage
Navigate to `Tools > Scripts > Live2D Export`.

## Installation
See the
[Krita documentation](https://docs.krita.org/en/user_manual/python_scripting/install_custom_python_plugin.html)
on how to install Krita plugins.
