#!/usr/bin/env bash

function create_icns {
  # Create .icns from the given image
  local imagePath="$1"
  echo "imagePath: ${imagePath}"
  local iconsetPath="${2:-$HOME/Pictures/MyIcon.iconset}"
  echo "iconsetPath: ${iconsetPath}"

  mkdir -p ${iconsetPath}
  rm -Rf ${iconsetPath}/*

  sips -z 16 16     $imagePath --out ${iconsetPath}/icon_16x16.png
  sips -z 32 32     $imagePath --out ${iconsetPath}/icon_16x16@2x.png
  sips -z 32 32     $imagePath --out ${iconsetPath}/icon_32x32.png
  sips -z 64 64     $imagePath --out ${iconsetPath}/icon_32x32@2x.png
  sips -z 128 128   $imagePath --out ${iconsetPath}/icon_128x128.png
  sips -z 256 256   $imagePath --out ${iconsetPath}/icon_128x128@2x.png
  sips -z 256 256   $imagePath --out ${iconsetPath}/icon_256x256.png
  sips -z 512 512   $imagePath --out ${iconsetPath}/icon_256x256@2x.png
  sips -z 512 512   $imagePath --out ${iconsetPath}/icon_512x512.png

  cp ${imagePath} ${iconsetPath}/icon_512x512@2x.png
  iconutil -c icns ${iconsetPath}
}

create_icns $@
