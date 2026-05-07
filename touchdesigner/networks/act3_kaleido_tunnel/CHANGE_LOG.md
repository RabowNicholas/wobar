# CHANGE LOG — act3_kaleido_tunnel

Act 3 kaleidoscope tunnel — Option B architecture (tunnel then mirror).
Core feedback loop → GLSL N-fold kaleidoscope applied post-feedback → color grade → glitch post.

Structural diff from act3_tunnel_mirror reference: Flip/mirror system replaced with GLSL kaleidoscope TOP. Fold applied to feedback output so mirror seams shift with tunnel motion — impossible geometry quality.

## Move History
- move_001: base_act3_kaleido COMP + core feedback tunnel loop (noise → feedback → xform → lvc → comp_main → null_out)
- move_002: edge content masking (circle_mask + comp_edge + null_content); noise tz animation
- move_003: GLSL kaleidoscope (ctrl_kaleido CHOP, glsl_kaleido TOP with uniform vec4 kaleido_ctrl, null_kaleido)
- move_004: portrait resolution 720×1280; explicit res on all chain nodes; feedback buffer reset
- move_005: corner bleed fix (const_black + comp_bg composite; null_final output cap)
- move_006: Act 3 color grade — hsv_desat (sat×0.15, val×0.8) → lvc_color (blacklevel 0.08, gamma 0.75, contrast 1.35) → lookup_act3 ← ramp_act3 (5-stop purple palette) → hsv_warm_kill → null_grade
