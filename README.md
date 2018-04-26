# osm_to_glb
Blender addon used to export glb models, along with metadata required by [3d_tileset_converter](https://github.com/wiped1/3d_tileset_converter). Buildings can be imported from any source, ex. [blender-osm](https://github.com/vvoovv/blender-osm). Each blender node is exported to its own directory, with \*.glb and \*.meta files, which can later be converted to tilesets supported by [cesium](https://cesiumjs.org/)

![Ui](/screenshots/ui.png?raw=true "Addon interface")

# Requires
- Blender 2.78.0
- Installed [glTF-Blender-Exporter](https://github.com/KhronosGroup/glTF-Blender-Exporter)

# Installing
- Move content of `osm_to_glb` repository to `scripts/addons/` directory
- Enable addon in user-preferences

# Usage
- Output - specifies directory in which exported hierarchy will be created
- Root - blender object that's used as root element in export hierarchy.

In order to be able to convert hierarchy to cesium-supported tilesets, the Scene has to have `lon` and `lat` properties which can be added in blender scene properties.

![Scene-props](/screenshots/scene_props.png?raw=true "Scene props")

# License
Licensed under MIT license (see [LICENSE.md](LICENSE.md))
