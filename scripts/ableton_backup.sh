#!/bin/bash
#
# ableton_backup.sh
# Copies installed plugins, Ableton templates, racks, M4L devices, and Serum
# presets from this machine to the "music" external drive.
# Skips anything that already exists at the destination. Asks for confirmation
# per category before copying.

set -u

DEST_ROOT="/Volumes/music"

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

process_category() {
    local label="$1" src="$2" dest="$3"

    if [ ! -d "$src" ]; then
        return
    fi

    local -a new_items=()
    local -a existing_items=()
    local item base

    for item in "$src"/*; do
        [ -e "$item" ] || continue
        base=$(basename "$item")
        case "$base" in
            .*|Imported|SaveYour*.txt) continue ;;
        esac
        if [ -e "$dest/$base" ]; then
            existing_items+=("$base")
        else
            new_items+=("$base")
        fi
    done

    # also pick up files inside an "Imported" subfolder, if present, flattened
    if [ -d "$src/Imported" ]; then
        for item in "$src/Imported"/*; do
            [ -e "$item" ] || continue
            base=$(basename "$item")
            case "$base" in .*) continue ;; esac
            if [ -e "$dest/$base" ]; then
                existing_items+=("$base (from Imported)")
            else
                new_items+=("$base|IMPORTED")
            fi
        done
    fi

    echo ""
    echo "== $label =="
    echo "Source: $src"
    echo "Dest:   $dest"

    if [ ${#new_items[@]} -eq 0 ]; then
        echo "Nothing new to copy (${#existing_items[@]} already present)."
        TOTAL_SKIPPED=$((TOTAL_SKIPPED + ${#existing_items[@]}))
        return
    fi

    echo "New items to copy (${#new_items[@]}):"
    for item in "${new_items[@]}"; do
        echo "  - ${item%%|IMPORTED}"
    done
    if [ ${#existing_items[@]} -gt 0 ]; then
        echo "Already present, will skip (${#existing_items[@]}):"
        for item in "${existing_items[@]}"; do
            echo "  - $item"
        done
    fi

    if confirm "Copy these ${#new_items[@]} item(s) into \"$dest\"?"; then
        mkdir -p "$dest"
        for item in "${new_items[@]}"; do
            if [[ "$item" == *"|IMPORTED" ]]; then
                base="${item%%|IMPORTED}"
                cp -R "$src/Imported/$base" "$dest/$base"
            else
                cp -R "$src/$item" "$dest/$item"
            fi
        done
        echo "Copied ${#new_items[@]} item(s)."
        TOTAL_COPIED=$((TOTAL_COPIED + ${#new_items[@]}))
        TOTAL_SKIPPED=$((TOTAL_SKIPPED + ${#existing_items[@]}))
    else
        echo "Skipped."
        TOTAL_SKIPPED=$((TOTAL_SKIPPED + ${#existing_items[@]}))
    fi
}

echo "Ableton production backup -> $DEST_ROOT"

for entry in "${CATEGORIES[@]}"; do
    IFS='|' read -r label src dest <<< "$entry"
    process_category "$label" "$src" "$dest"
done

echo ""
echo "== Done =="
echo "Copied:  $TOTAL_COPIED"
echo "Skipped (already present or declined): $TOTAL_SKIPPED"
