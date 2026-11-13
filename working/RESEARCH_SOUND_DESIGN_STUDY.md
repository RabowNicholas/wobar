---
title: Sound design study — how the people ahead actually build their sound
version: 1.0
last_updated: 2026-10-28
status: reference
scope: What comp artists have said or shown about their own sound design, plus where to watch and learn more, ranked by how much you'd learn. Sound only. Companion to [[working/RESEARCH_ARTIST_PACKS]] (what source material can be bought).
---

# Sound design study map

**Method (2026-10-28, all in Claude in Chrome):** YouTube searched for every artist (3 queries each) plus their own channels. Read through transcripts: STVSH (Ableton Podcast ep199), Leotrix & elide (ep201), INZO & Blookah (ep191), Eprom's "The Cat" breakdown, dêtre (Poducer ep8), Ternion Sound's sound design Q&A, and a Tsuruda stream. Written interviews read: G Jones (EDM.com), Ivy Lab (MusicRadar/Computer Music), Tsuruda (FUXWITHIT), MYTHM (Heard It Here First).

**Ground-truth rule:** **First-party** means the artist showing or explaining their own process. **Third-party** means someone else's recreation. Recreations are useful but are someone else's guess. Study first-party, then use recreations to practise.

---

## 1. What they actually do: patterns across artists

Each pattern comes up independently from several artists. These are the moves to learn.

**1. Resample destructively, then print and clean.** This is the most repeated idea.
- **STVSH:** He moves Serum's knobs by hand and records the result into long "Mud Pies" audio files, saved in a folder he reuses across tracks. He keeps the sound by saving the audio, not the patch. He resamples the MIDI performance to audio, then cuts and cleans the clip so it plays the same every time.
- **Ternion Sound (Jack):** Each print of a sound becomes a new sample with new artifacts. Pitch a snare way up, distort it, resample, then pitch it back down: the distortion shifts down two octaves with it. Bit-reduction leaves a sharp high-frequency cliff that moves when you re-pitch. Add reverb, then shorten the sampler's volume envelope to keep only the first chunk of reverb as texture.
- **Leotrix & elide:** They resample their own released songs and drop them into Serum's noise oscillator or use them as a bassline source, describing that as "infinite textures."
- **INZO & Blookah:** They resample the whole track without drums back in as a chop, and resample several parts into one.

**2. Don't make the low end from the patch. Use a dedicated sub.**
- **STVSH:** On a main bass he cuts the low end from the resampled audio and writes a separate sub on the same notes. He keeps the patch's own sub only for fills.
- **INZO:** The sub always gets its own track.
- **Eprom:** Layer a midrange growl over a clean sub, then add a little reverb.

**3. Distortion is the instrument, but it's controlled.**
- **STVSH:**
  - Uses Serum 2's oscillator-level distortion and band-split effects (a tip from Tim Underbelly).
  - Tries delay both before and after distortion.
  - His answer to "how do you keep it clean?" is **"I just turn it down"**, plus the dedicated sub.
  - Go-to Ableton devices: Roar (on everything), Amp, Vinyl Distortion.
- **Leotrix & elide:**
  - Run heavy OTT, then shape transients or clip after it to tighten the back end.
  - Ableton Saturator in soft-clip or waveshaper mode is their favourite clipper.
  - They get most of the way there with just multiband dynamics, EQ Eight and Saturator.
  - Also use Dynamic Tube, Vinyl Distortion, and a phaser/flanger duplicated against itself as a phase-based comb filter.
- **Ableton Podcast host (tip given to STVSH):** use the saturation knob on Color Limiter (Creative Extensions pack), not the limiting.
- **Tsuruda:** Drum Buss, Corpus and Saturator. He moved from sampling to his own digital synthesis, which he then resamples.

**4. FM for wobbles, snares and growls, mostly in Operator.**
- **Eprom ("The Cat"):**
  - The growl is a Reese bass with a pitch envelope rising, peaking and levelling off.
  - The wobble is basic Operator FM with the modulator tuned to 3× the carrier.
  - The modular FM riser is one oscillator slowly pitching up while FM-ing a steady one.
- **Ternion:** Snares start as a single sine, then get FM from other operators, followed by distortion, reverb and delay, and finally many resampling rounds.
- **dêtre (counterpoint):** His "harmonic distortion" basses use **no FM**. He stacks upper harmonics and distorts them together, which he calls additive. One whole tune was a single Vital patch, heavily automated. He moved to Vital deliberately because his sound design had become too sample-driven.

**5. Make lots of variations and pick the best.**
- **Eprom:** Kick = a distorted 808 plus a time-stretched cymbal through distortion, saturated together in one group. He bounces 10–15 variations and picks one.
- **Ternion:** Resampled one FM snare into **2,000** variations, auditioned them all, and kept about 100.
- **G Jones:** Long live takes jamming on a Moog Sub37 while turning knobs, recording everything, then chopping only the good parts into the arrangement.
- **Ivy Lab:** "We find the best four things and work with them. Don't mourn the loss."

**6. The sampler is a character tool, not just playback.**
- **Ivy Lab:** Bounce a synth into a sampler, chop off the release and reverb, then play it up and down the keyboard. Pitch and time stay linked, so it gets an Akai/MPC feel. They prefer limited tools: "fewer knobs… you can get on with composing."
- **Ternion:** The same pitch-and-time link is what moves distortion artifacts around.
- **Eprom:** Breakdown drums are chopped breaks, sequenced randomly with Ableton follow actions. He uses the Pitch Drop Max for Live device on transients, and Grain Delay 100% wet with high spray on effects.

**7. Groove and wonk by hand.**
- **Ivy Lab:** "We tend to do most of the wonkiness by hand. You could get a plugin to do it, but that just doesn't feel right." Squarepusher is their template. Off-grid timing started as incidental and became core to their sound.
- **dêtre:** Every synth on one tune was quarter-note syncopation.

**8. Mixing and mastering: fewer chains, more clipping.**
- **STVSH:** No master chain. He clips Ableton's output, so the mixdown becomes the master. It made production "so much more fun" and the kicks and snares "smack."
  - Sidechain: two GM Ducker devices in one rack, one keyed from the kick and one from the snare.
  - Ring-mod distortion sidechained to the whole drum bus (shown to him by Nyquist). The plugin name is garbled in the transcript.
- **INZO:** Glue Compressor into a clipper (Pro-L or similar) with oversampling. They recommend the plugin Standard Clip and A/B'ing it against KClip.
- **G Jones:** "A good idea that is mixed poorly is way more valuable than a well-mixed, mediocre idea." He writes on laptop speakers to avoid engineering too early.

**9. Small workflow fixes.**
- **STVSH:**
  - Turn warp **off** on resampled bass. Beats mode damages it; keep Beats only for percussion or loops.
  - Reverse-reverb sweep: resample the sound, put reverb on it, reverse it. He uses TAL Reverb, which is free.
  - Hybrid Reverb with a vocal sample loaded as the impulse response, on a pluck or bass (a Mr. Bill trick he passed on).
- **Eprom:** Push sounds back with reverb and delay in the build, then remove them at the drop so it "zooms up in your face."
- **G Jones:** Make horrible noise on purpose. Exploring beats aiming for a specific sound.

---

## 2. Watch first: first-party, ranked

| # | Artist | What | Link |
|---|---|---|---|
| 1 | STVSH | Ableton Podcast ep199 (1:01): bass sound design, Mud Pies, Roar, no master chain | https://www.youtube.com/watch?v=mzHs-KXQfsw |
| 2 | Eprom | "The Cat" track breakdown (1:17): sound by sound, FM, kicks, breaks | https://www.youtube.com/watch?v=0C7m_m5_NnM |
| 3 | Eprom | Sound Design + First Stream (35m); Sound Design + Breakbeat Choppage (20m) | https://www.youtube.com/watch?v=FP9tn6DCtyo · https://www.youtube.com/watch?v=V4lVZRl3w-4 |
| 4 | Leotrix & elide | Ableton Podcast ep201 (1:26): resampling, OTT, clipping, comb filtering | https://www.youtube.com/watch?v=-qua8bKcRms |
| 5 | Ternion Sound | Sound design Q&A (1:07): FM snares and a full resampling loop | https://www.youtube.com/watch?v=a2MNztZD-zQ |
| 6 | INZO & Blookah | Ableton Podcast ep191 (1:09): layering, resampling the track, clip/master | https://www.youtube.com/watch?v=jAxqA6ujdSA |
| 7 | Tsuruda | Archived Twitch streams, e.g. making a beat from scratch (54m). Mostly chat, so **watch the screen** rather than listen | https://www.youtube.com/watch?v=aeTjq4uHCmY |
| 8 | dêtre | Poducer ep8 (1:35). Mostly career talk; the Vital and harmonic-distortion part is the gold | https://www.youtube.com/watch?v=N79DohqVE7A |
| 9 | Virtual Riot | "making brostep & other sounddesign stuff" (3:35 stream); "mixing and mastering a drop" (42m); "3 ways to make a reese" | https://www.youtube.com/watch?v=Z296qcZlKAE · https://www.youtube.com/watch?v=0T9EhySSWzU · https://www.youtube.com/watch?v=dAXysNzeRd0 |
| 10 | Mr. Bill | "Fastest resampling technique ever"; "Mr. Bill uses Live 12's Roar" | https://www.youtube.com/watch?v=sD-EGOHJ8sY · https://www.youtube.com/watch?v=morMndyQ72o |
| 11 | PhaseOne | Own project breakdowns: "DISAPPEAR", "Reign of Malice" | https://www.youtube.com/watch?v=HeqgvU99Vjs · https://www.youtube.com/watch?v=IJxUlhVaQZg |
| 12 | Au5 | Ableton Podcast ep193 (1:48); "The OG Growl" | https://www.youtube.com/watch?v=WU13MIfB7vI · https://www.youtube.com/watch?v=-okW7lKNZ1Q |
| 13 | Ivy Lab | Computer Music Producer Masterclass pt 1 (video of the MusicRadar piece) | https://www.youtube.com/watch?v=hkZwOqzkyUc |
| 14 | Mind Splitter | icantproduce podcast ep35 (1:46) | https://www.youtube.com/watch?v=_CF6RQdVS8o |
| 15 | Stylust | Wub Theory 005 with track breakdown (1:00) | https://www.youtube.com/watch?v=Y6C4e9vhRpc |
| 16 | Shades (Alix Perez & Eprom) | Livestream 2020 (2:53) | https://www.youtube.com/watch?v=PM0BOfE1-mU |
| 17 | Chee | Bitwig demo-song walkthrough "Hey Now" (17m) | https://www.youtube.com/watch?v=V4mvT4Tbc3s |

More Ableton Podcast episodes worth watching: COPYCATT (2 eps, sound design/Mud Pies workflow) https://www.youtube.com/watch?v=NjEFjYFqHM0 · https://www.youtube.com/watch?v=VoyCFl6clps; AHEE (bass mixing, Serum 2) https://www.youtube.com/watch?v=BN_XXUiELQo; Mr. Bill ep81 https://www.youtube.com/watch?v=oKbHNFufjP8.

Written first-party: G Jones on EDM.com (Sub37 jams, exploration, mix-later) https://edm.com/interviews/g-jones-interview/; Ivy Lab on MusicRadar (sampler character, wonk by hand) https://www.musicradar.com/news/producer-masterclass-ivy-lab-these-days-the-average-plugin-sometimes-feels-a-bit-over-the-top; Tsuruda on FUXWITHIT 2019 (Drum Buss, Corpus, moving to synthesis) https://fuxwithit.com/2019/12/30/tsuruda-interview/.

## 3. Practise with: third-party recreation channels

These channels cover almost the whole lane. Use them to rebuild sounds, not as the truth about how the artist does it.

| Channel | Covers (lane artists) | Format |
|---|---|---|
| **BRAINWAVEZ** | STVSH, dêtre, Blurrd Vzn, OkayJake, Gunpoint, Daggz/Chmura, Comisar, Super Future, Tape B (43m), Distinct Motive, LSDREAM, INZO, Of The Trees, Lumasi, SAKA, Ternion, Eprom, G Jones "Helix", CharlesTheFirst | 10–20 min Serum 2/Vital "like X" recreations. Has a Patreon with the projects |
| **Bunting** | Blurrd Vzn, Shades, Of The Trees, MYTHM, Tipper (×4), Ivy Lab, CharlesTheFirst, CloZee, Tsuruda, Ternion, G Jones/Eprom | Vital + Ableton sound design and arrangement |
| **Dripment** | Distinct Motive (×2), Tape B (×3), Of The Trees (×2), LSDREAM, Lumasi, FLY, CharlesTheFirst, PhaseOne, Svdden Death, Tipper | "How to make X like Y" |
| **AMBSHN** | INZO miniseries ("World Building"), LSDREAM owl bass, Of The Trees "Spanish Moss" | Serum deep dives |
| **SWOMP** | Of The Trees (50m full project breakdown), CharlesTheFirst & Supertask | Full project breakdowns with free downloads |
| **SEPHROS** | G Jones/Eprom (two 1.5h streams), Eprom/Shades bass, Ivy Lab rhythm | Long streams |
| **Munchkin Kat** | LSDREAM × INZO "Faceplant on the Galaxy" (3 parts), LSZEE/Shlump "Mirage × Starchild" | Hot Key long-form breakdowns |

## 4. Learn directly from artists

| Artist | What | Price | Where |
|---|---|---|---|
| **OkayJake** | 1:1 production lessons. Reviewers say he opens his Ableton projects and runs through how he builds his sound | $75 / 60 min · $100 / 90 min | okayjake.setmore.com |
| **Daggz** | 3-hr production lesson block | $200 / 3 hrs | calendly.com/daggzmusic |
| **MYTHM** | Private mentorship (deep 140 / riddim) via Future Sound Academy | Not shown; booking request | futuresoundacademy.com/artist-development/work-with/mythm |
| Mr. Bill | Membership: 80+ project files, 150+ tutorials | $20/mo | mrbillstunes.com |
| Comisar | Patreon: packs, Serum presets, resources | Tiers unreadable | patreon.com/comisar |

## 5. Nothing first-party found

These artists have only third-party recreations or DJ sets: Blurrd Vzn, OkayJake (lessons only), Gunpoint, Crucial, highrollr, Chmura, Comisar (Patreon only), En:vy (one 4-min origin story), Super Future, Yoko, Potions, Jungle Rootz (two old studio-session clips), Tape B (career interviews only), Ero808, SAKA, FLY, Coka Cobra, SPOONE, Noctiil, Distinct Motive (third-party only), Caspa (old interviews), Of The Trees ("15 years in the making" bio video only), LSDREAM (story video only), Alex Unger, Lumasi ("How Lumasi Found His Sound" is bio), Mesck, Tipper, Space Laces, Yheti, Charlesthefirst (festival interviews only), Bleep Bloop, Svdden Death (one old live stream on a third-party channel), Eptic (old "in the studio" clips), Zebbler.

**Name flags:**
- "Shades" in dubstep results is **Alix Perez & Eprom's duo**. If that's not who you meant, the other Shades has no footprint.
- "MythMusic" / "Myth" track breakdowns are a **different producer** from MYTHM.

## 6. How to study one comp (repeatable)

1. Pick one sound from one of their tracks, e.g. the main bass of a drop.
2. Watch the first-party source if it exists (§2). Write down every device and move they name.
3. Rebuild the sound in a 4–8 bar loop using their stated method, not a recreation's.
4. Then watch the BRAINWAVEZ/Bunting recreation (§3) and note where it differs from what the artist said.
5. A/B against the original at matched loudness. Write the gap in one sentence.
6. Make 10+ variations and keep one (pattern 5).
7. Book one lesson (OkayJake or Daggz) once you have a specific gap you can't close. Bring the project.

---

## 7. EAZYBAKED: deep dive (added 2026-11-02)

**Why:** Nick named EAZYBAKED as the reference for where he's pushing his sound. EAZYBAKED is Eric Ray and Andrew Principe, from Orlando and now based in Denver.

**Method:** Read in Claude in Chrome. First-party transcripts: Lizzy Jane Podcast #69 (2022, around *Intertwined*), Audio Eats documentary with interview (2025), Poducer at Sound Haven (2024). Written: Beatportal Q&A (*Respawn*), Melodic Mag, Magnetic Mag (2026). Third-party recreations: BRAINWAVEZ "Free Form Bass like EAZYBAKED", Dripment "Psychedelic Dubstep like EAZYBAKED" (rebuilds *Sapped*).

### First-party: what they say they do

1. **DAW: Reason, not Ableton.** They went from GarageBand on school iPads to a cracked copy of Reason, and they were still on Reason at the time of *Intertwined* (2022). They chose it for the visual rack and patch bay: *"it's a visual learning... hands-on."* They learned by trial and error because Reason had almost no tutorials back then, and they credit that with finding their own sound: they were *"break[ing] the rules"* without knowing what the rules were.
2. **They work from MIDI and stock synths, and resampling comes second.** *"We've always sampled, but... most of our sounds come from staying strictly MIDI and writing as much as we can, squeezing out as much of the stock synths."* **This is the opposite of pattern 1 in §1** (resample destructively, print, clean). They are the clearest counterexample in the study.
3. **The founding idea: build minimal tracks out of fill sounds.** *"I thought I could make minimal music using sounds that people use as fills... and just get really minimal and weird."* The wub fills are the material, not the decoration between sections.
4. **The sound came together around *Clone* (2017):** *"we were resampling things, we were figuring out what wubs were and implementing them."*
5. **Role split:** *"Andrew's better [at] sound design, I'm better at... arrangement and flow — but we could both do both."* Their best tracks come from sitting together and going *"start to finish"* in one sitting. Otherwise either of them starts an idea and hands it off.
6. **How they made the album:** they keep the ideas that *"stick,"* *"chip away"* at them over about two years, and decide early that a track belongs to the body of work. *Intertwined* deliberately merged EAZYBAKED with their mellow side project **The Bakers**: four-on-the-floor sections, guitar plucks, and foley/ambient detail (keys, birds) placed up front. *No* uses Andrew's daughter's vocals.
7. **Finishing:** a track is done when it plays through without anything demanding a fix. *"Trust yourself... it might never be done."*
8. **Volume over polish:** *"Make thousands of songs... if you're halfway through, finish it... fail fast."* In 2024 they were *"flipping a lot of stuff and putting it out on the cuff,"* and they put plenty of SoundCloud-only extras alongside the official releases.
9. **Lineage:** hip-hop beats first (Mac Miller, A$AP Rocky, Wiz), then bass-heavy trap (TroyBoi, Mr. Carmack, Bloom, LOUDPVCK, Slumberjack), then Ledge Kale (*"crazy drums, everything so loud"*). The beat-scene and hip-hop root is shared with Wobar's rap-flip register.
10. ***Respawn* (2025)** was a deliberate move toward a mellower, more personal sound: *"scary! but also very freeing."* Their stance: *"never want to feel limited or boxed in."*
11. **Sets:** 70–75% original. They build around a *"sense of story,"* balancing heavy moments with mellow ones.

### Third-party: how their sound gets rebuilt (Serum/Vital/Ableton, not their method)

- **Tempo and drums:** 140 BPM, simple drums: kick, two layered snares, one texture layer, a hat loop. Snare reverb is automated on and off.
- **Sub:** a sine with a pitch-envelope drop at the start of each note. Every two bars it switches from sustained to a quarter-note tremolo. Dripment hand-draws a one-bar trigger LFO on the sub's level: *"it really is about catching a nice flow."*
- **Wubs:** a sine carrier with FM from a second oscillator (basic shapes or harmonic series, around 43%). One trigger LFO drives level, filter cutoff and FM amount. **Downsample distortion** gives the "yoy" vowel, with a post-filter to clean it. Then chorus and multiband, with the low end made mono below about 500 Hz.
- **Space:** a reverb-throw rack on the wub group, with throws that grow louder across the drop. Short, high-passed reverb on the bass.
- **Groove:** bass notes are nudged **about 28 ms late** against the downbeat.
- **Headroom:** *"this genre has a lot more headroom, you don't have to get super loud."*
- **Bed:** ambience pitched into key carries a lot of the track. A recording of keys being jingled is bitcrushed into a rhythmic pattern.

### What transfers to Wobar

- **Movement comes from modulation, not printed audio.** A wub is one playable patch whose character comes from LFO, FM and downsampling. That makes it fast to write, consistent with *"squeezing the stock synths,"* and repeatable across a track.
- **Space and headroom over density.** This lines up with SONIC's *sub + space, not maximalist* and *textures that breathe*.
- **Fills become the hook.** Write the drop out of what other producers would use as transitions.
- **Foley and ambience as a front-row layer, pitched into key.**

### Open

- **Register.** The vault files EAZYBAKED under Lane A psy-bass ([[working/RESEARCH_LABEL_MAP]] §Lane A), not under the wonky-140 centre of mass. Pushing toward them may shift the weighting in [[reference/WOBAR_SONIC]]'s register table. That isn't decided.
- **Their own sounds are for sale:** the *Transmissions* sample packs Vol 1–2 and the *Clone* pack (soundcloud.com/eazybakedbeats/sets/sample-packs). These are the nearest thing to first-party source material. Not yet in [[working/RESEARCH_ARTIST_PACKS]].
- **Not yet read:** EDM Identity *"Chats About EDC"* (6 min), TruePandaLIVE "Featured artist" (2014), Instagram/TikTok studio clips. No first-party studio walkthrough or project breakdown was found.
