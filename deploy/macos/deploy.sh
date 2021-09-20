#!/bin/bash

#############################
# Create DMG
#############################

if [[ $GITHUB_REF == refs/heads/* ]] ;
then
    VERSION=${GITHUB_REF#refs/heads/}
else
	if [[ $GITHUB_REF == refs/tags/* ]] ;
	then
		VERSION=${GITHUB_REF#refs/tags/}
	else
		exit 1
	fi
fi

rm pigcel*dmg

PIGCEL_DMG=pigcel-${VERSION}-macOS-amd64.dmg
hdiutil unmount /Volumes/pigcel -force -quiet
sleep 5
./deploy/macos/create-dmg --background "./deploy/macos/resources/dmg/dmg_background.jpg" \
                                                     --volname "pigcel" \
									             	 --window-pos 200 120 \
										 			 --window-size 800 400 \
										 			 --icon pigcel.app 200 190 \
										 			 --hide-extension pigcel.app \
										 			 --app-drop-link 600 185 \
										 			 "${PIGCEL_DMG}" \
										 			 ./dist
