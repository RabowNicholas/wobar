# Goal / peer / bad labels as confirmed by the artist 2026-11-11, with Beatport ids found by search + catalogue check.
GOAL = {
 'Deadbeats': [69987, 87982, 71774, 109144, 73263, 121309, 75157, 69996],
 'Wormhole Music Group': [68217],
 'Bassrush': [65158, 207471, 65920, 99892],
 'Jadu Dala': [72037, 187265],
 'UKF': [18130],
 'Deep Dark & Dangerous': [43229],
 'Wakaan': [110315],
 'Disciple': [373903, 32070],
 'Circus Records': [126878, 105054],
 'Cyclops Recordings': [78866],
 'Drama Club Recordings': [78868, 292245],
 'Subsidia': [90526],
 'Good Society': [113575],
 'Memory Palace': [115076],
 'Local Void': [129124],
}
PEER_GOOD = {'Wubaholics': [109502], 'DUPLOC': [47581, 91973, 105490], 'Locus Sound': [68422], 'Infernal Sounds': [73029],
             'SubCarbon Records': [40841], 'Odyzey Music': [90781], 'Trippy Bee Records': [150059]}
PEER_BAD = {'Outertone': [131548], 'Space Yacht': [90395], 'Create Music Group': [74695], 'DistroKid': [66449]}
GOAL_IDS = {i for v in GOAL.values() for i in v}
PEER_IDS = {i for v in PEER_GOOD.values() for i in v}

# Artist override 2026-11-11: 'I don't believe they are really trap.' Beatport's Trap tags ignored for these labels only.
GENRE_OVERRIDE = {90781, 150059}

# Artist decisions 2026-11-11 (after first report)
ACTIVITY_WAIVE = {90781}            # Odyzey: missed the 60-day rule by one day; artist said include
ARTIST_REJECT = {110914: 'too small (artist call)'}  # Bad Medic Records
# Killed after listening to the label-study playlists, 2026-11-11: Port Zero, Sounds Of Mayhem, Neoluminum
for _i in (131258, 112736, 103220): ARTIST_REJECT[_i] = 'not a fit after listening (artist call)'
SEND_SET_EXCLUDE = {23412, 24539}   # Monstercat, Gravitas: 4/12 in genre; stay on List B, out of send set
