# MagIC 6.3 counterpart notes (paper §F1, §F3)
# MagIC is the INDEPENDENT contrast implementation, not a parameter translation.
# Setup rules from the manuscript:
# - Use MagIC's own sample namelists and test cases for its setup.
# - ktops=2 + harmonic s_top entries specify an outer temperature/entropy
#   gradient: convert sign and normalization to physical outward heat flux.
# - Do NOT use MagIC's strat density-contrast parameter as a stable-layer
#   buoyancy frequency; set up stratification through MagIC's own interface.
# - MagIC diagnostics/extensions must be implemented separately.
# TODO(audit): pick the decisive-contrast cells to repeat in MagIC AFTER the
# XSHELLS pilot (paper §F6 order: XSHELLS first, MagIC on decisive contrasts).
