#!/bin/bash
#
# ableton_backup.sh
# Copies installed plugins, Ableton templates, racks, M4L devices, and Serum
# presets from this machine to the "music" external drive.
# Never overwrites: skips any file or plugin bundle already at the destination,
# but looks inside existing folders for new files. Asks for confirmation
# per category before copying.
#
# Usage: ableton_backup.sh [--dry-run]
#   --dry-run  list what would be copied, copy nothing

set -u

DEST_ROOT="/Volumes/music"
DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

if [ ! -d "$DEST_ROOT" ]; then
    echo "Error: destination drive not found at $DEST_ROOT. Plug it in and retry."
    exit 1
fi

# name|source_path|dest_path
CATEGORIES=(
    "AU Plugins|/Library/Audio/Plug-Ins/Components|$DEST_ROOT/Plug-ins/Components"
    "VST3 Plugins|/Library/Audio/Plug-Ins/VST3|$DEST_ROOT/Plug-ins/VST3"
    "VST Plugins|/Library/Audio/Plug-Ins/VST|$DEST_ROOT/Plug-ins/VST"
    "Templates|$HOME/Music/Ableton/User Library/Templates|$DEST_ROOT/templates"
    "Audio Effect Racks|$HOME/Music/Ableton/User Library/Presets/Audio Effects/Audio Effect Rack|$DEST_ROOT/audio effect racks"
    "Instrument Racks|$HOME/Music/Ableton/User Library/Presets/Instruments/Instrument Rack|$DEST_ROOT/wobar-ableton-devices"
    "MIDI Effect Racks|$HOME/Music/Ableton/User Library/Presets/MIDI Effects/MIDI Effect Rack|$DEST_ROOT/MIDI Effects"
    "M4L Audio Effects|$HOME/Music/Ableton/User Library/Presets/Audio Effects/Max Audio Effect|$DEST_ROOT/Plug-ins/Max "
    "M4L MIDI Effects|$HOME/Music/Ableton/User Library/Presets/MIDI Effects/Max MIDI Effect|$DEST_ROOT/Plug-ins/Max "
    "M4L Instruments|$HOME/Music/Ableton/User Library/Presets/Instruments/Max Instrument|$DEST_ROOT/Plug-ins/Max "
    "Serum User Presets|/Library/Audio/Presets/Xfer Records/Serum 2 Presets/Presets/User|$DEST_ROOT/Presets/Serum"
    "Serum Packs|/Library/Audio/Presets/Xfer Records/Serum 2 Presets/Presets/Packs|$DEST_ROOT/Presets/Serum/Packs"
    "Serum User Tables|/Library/Audio/Presets/Xfer Records/Serum 2 Presets/Tables/User|$DEST_ROOT/Presets/Serum/Tables"
)

TOTAL_COPIED=0
TOTAL_SKIPPED=0

confirm() {
    # $1 = prompt text
    read -r -p "$1 [y/N] " reply
    case "$reply" in
        [yY][eE][sS]|[yY]) return 0 ;;
        *) return 1 ;;
    esac
}

# Plugin bundles are directories on disk but get copied whole, never merged.
is_bundle() {
    case "$1" in
        *.component|*.vst3|*.vst|*.clap|*.aaxplugin|*.bundle|*.app) return 0 ;;
        *) return 1 ;;
    esac
}

# walk SRC_DIR DEST_DIR REL_PREFIX
# Recurses into ordinary folders that already exist at the destination, so new
# files inside them are found. Folders missing at the destination are queued
# whole. Fills NEW_SRC / NEW_DST / NEW_LABEL and bumps SKIP_COUNT.
walk() {
    local s="$1" d="$2" rel="$3" item base n
    for item in "$s"/*; do
        [ -e "$item" ] || [ -L "$item" ] || continue
        base="${item##*/}"
        case "$base" in
            .*|SaveYour*.txt) continue ;;
        esac
        # top-level "Imported" folder is flattened into dest separately
        if [ -z "$rel" ] && [ "$base" = "Imported" ]; then
            continue
        fi
        if [ -d "$item" ] && [ ! -L "$item" ] && ! is_bundle "$base"; then
            if [ -d "$d/$base" ]; then
                walk "$item" "$d/$base" "$rel$base/"
            elif [ -e "$d/$base" ]; then
                SKIP_COUNT=$((SKIP_COUNT + 1))
            else
                n=$(find "$item" -type f ! -name '.*' | wc -l | tr -d ' ')
                NEW_SRC+=("$item"); NEW_DST+=("$d/$base")
                NEW_LABEL+=("$rel$base/  (new folder, $n files)")
            fi
        else
            if [ -e "$d/$base" ] || [ -L "$d/$base" ]; then
                SKIP_COUNT=$((SKIP_COUNT + 1))
            else
                NEW_SRC+=("$item"); NEW_DST+=("$d/$base")
                NEW_LABEL+=("$rel$base")
            fi
        fi
    done
}

process_category() {
    local label="$1" src="$2" dest="$3" i

    if [ ! -d "$src" ]; then
        return
    fi

    NEW_SRC=(); NEW_DST=(); NEW_LABEL=(); SKIP_COUNT=0

    walk "$src" "$dest" ""
    # files inside a top-level "Imported" subfolder land flat in dest
    if [ -d "$src/Imported" ]; then
        walk "$src/Imported" "$dest" "Imported/"
    fi

    echo ""
    echo "== $label =="
    echo "Source: $src"
    echo "Dest:   $dest"

    TOTAL_SKIPPED=$((TOTAL_SKIPPED + SKIP_COUNT))

    if [ ${#NEW_SRC[@]} -eq 0 ]; then
        echo "Nothing new to copy ($SKIP_COUNT already present)."
        return
    fi

    echo "New items to copy (${#NEW_SRC[@]}):"
    for i in "${!NEW_LABEL[@]}"; do
        echo "  - ${NEW_LABEL[$i]}"
    done
    echo "Already present, will skip: $SKIP_COUNT"

    if [ "$DRY_RUN" -eq 1 ]; then
        echo "(dry run: nothing copied)"
        TOTAL_COPIED=$((TOTAL_COPIED + ${#NEW_SRC[@]}))
        return
    fi

    if confirm "Copy these ${#NEW_SRC[@]} item(s) into \"$dest\"?"; then
        for i in "${!NEW_SRC[@]}"; do
            mkdir -p "$(dirname "${NEW_DST[$i]}")"
            cp -R "${NEW_SRC[$i]}" "${NEW_DST[$i]}"
        done
        echo "Copied ${#NEW_SRC[@]} item(s)."
        TOTAL_COPIED=$((TOTAL_COPIED + ${#NEW_SRC[@]}))
    else
        echo "Skipped."
        TOTAL_SKIPPED=$((TOTAL_SKIPPED + ${#NEW_SRC[@]}))
    fi
}

echo "Ableton production backup -> $DEST_ROOT"

for entry in "${CATEGORIES[@]}"; do
    IFS='|' read -r label src dest <<< "$entry"
    process_category "$label" "$src" "$dest"
done

echo ""
echo "== Done =="
if [ "$DRY_RUN" -eq 1 ]; then
    echo "Would copy: $TOTAL_COPIED (dry run)"
else
    echo "Copied:  $TOTAL_COPIED"
fi
echo "Skipped (already present or declined): $TOTAL_SKIPPED"
