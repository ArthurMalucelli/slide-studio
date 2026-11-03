# Mapas (67)

Todos os tratamentos de mapa encontrados.

Ordem: qualidade, depois deck. ★★★ é a referência a copiar. Copie a técnica, nunca o conteúdo nem as cores do deck de origem.

## ★★★ Funnel wedge from map to colour-keyed cluster bars
- **Origem:** 3R Petroleum, p. 19
- **Recorte:** `crops/m_funnel_wedge_clusters.jpg`
- **Peça pronta:** `pecas_mapas_a.py::funnel_clusters`
- **Função:** Zooms geography into portfolio, so each coloured state becomes a labelled bar that continues into a reserves donut.
- **Serve para:** Portfolio or segment breakdown tied to geography; historical overview above a timeline.
- **Como montar:** Geography: Brazil by state in 4-5 greys; only cluster states take the brand colours (navy, green, dark teal). Wedge: solid green triangle, apex at the map's east edge and base at the full panel height, gradient running to grey at the apex. Panel: light grey rectangle behind three stacked bars, one per cluster, each with a darker skewed parallelogram on its right so it looks folded; donut in the same colours and a dashed total box to the right. Order: panel, wedge, map, bars, donut. No labels on the map; colour is the only key.

## ★★★ Mini-map coin selector
- **Origem:** 3R Petroleum, p. 20, 21, 22
- **Recorte:** `crops/m_coin_selector.jpg`
- **Peça pronta:** `pecas_mapas_a.py::coin_selector`
- **Função:** Uses mini-maps as tabs: the active cluster stays in full colour and the others fade, so a repeated page shows where you are.
- **Serve para:** Repeating a template across clusters, regions or projects.
- **Como montar:** Geography: Brazil by state inside a circle. Active: dark-green circle, pale map, active state bright green, solid arrow to bold cluster name. Inactive: pale sage circle, near-white map, pale arrow and faded label. Build all three, then swap the active style per page. Order: circle, map, highlight, arrow, label.

## ★★★ Silhouette with radial glow gradient and route lines
- **Origem:** Alupar, p. 13, 14, 17, 18
- **Recorte:** `crops/m_gradient_silhouette_route.jpg`
- **Peça pronta:** `pecas_mapas_a.py::silhouette`
- **Função:** Gives a plain country outline drama with one gradient and thin route lines, leaving the data card to carry the numbers.
- **Serve para:** Single-project or single-country pages; repeatable project template.
- **Como montar:** Geography: one country as a single shape, no internal borders (Peru, Colombia). Colour: radial gradient, royal blue centre to near-black navy edge. Overlays: thin blue-to-cyan polylines with small ring nodes for each transmission route; tiny legend of line swatches at bottom left; Python logo floating top left to flag analysis. Order: silhouette, routes, nodes, legend. Paired with a framed term-sheet card on the right. Page 18 uses a small variant.

## ★★★ Dense route network with dashed cluster ellipses
- **Origem:** Alupar, p. 12
- **Recorte:** `crops/m_network_dashed_ellipses.jpg`
- **Peça pronta:** `pecas_mapas_a.py::network`
- **Função:** Shows a whole country's transmission network and uses thin dashed ellipses to group it into the areas that matter, with no labels on the map.
- **Serve para:** Grouping a dense network into regions.
- **Como montar:** Geography: Peru as one shape, radial gradient from royal blue centre to near-black navy edge. Overlays: many thin cyan-to-white polylines with small ring nodes, voltage legend of line swatches at lower left, dark dashed ellipses drawn around 4 clusters, Python logo floating top left. Container: pale-blue gradient panel with a blue border, KPI row and two underlined plan headings on top. Order: panel, silhouette, lines, nodes, ellipses, legend.

## ★★★ Twin state choropleths with counts and independent scales
- **Origem:** BTG Pactual, p. 87
- **Recorte:** `crops/m_twin_state_counts.jpg`
- **Peça pronta:** `pecas_mapas_a.py::twin_counts`
- **Função:** Compares two firms' office networks with the actual number printed on every state.
- **Serve para:** Footprint contrast between two companies.
- **Como montar:** Geography: two Brazil state maps, BTG and XP. Colour: grey for zero, pale blue to strong teal for count. Labels: integer centred on each state with at least one office, and a small title above each map. Legend: thin vertical gradient bar beside each map, labelled max and 1. Each map has its own scale (60 vs 302), which fits footprint shape but not absolute size, so state that next to the slide. Rebuild: Excel or PowerPoint filled-map chart, whose 'Powered by Bing' credit stays visible, or freeform states.

## ★★★ Portrait leaders into a map
- **Origem:** BTG Pactual, p. 62
- **Recorte:** `crops/m_portrait_leader_map.jpg`
- **Peça pronta:** `pecas_mapas_a.py::portrait_leaders`
- **Função:** Credits primary research geographically by running a line from each interviewee's face to their country.
- **Serve para:** Interview evidence by geography.
- **Como montar:** Geography: Latin America; operating countries near-black navy, Brazil mid blue, rest grey. Left: circular portrait, name, role, italic date. Leaders: thin black line from a small diamond above the name straight to the country. Right: dark grey quote boxes with cyan emphasis. Order: map, leaders, portraits, text.

## ★★★ Dark-slide outline map with glowing corridor states and two-sided orthogonal leaders
- **Origem:** CSN (Liability Management), p. 24
- **Recorte:** `crops/m_dark_outline_glow_leaders.jpg`
- **Peça pronta:** `pecas_mapas_a.py::dark_glow`
- **Função:** Turns a logistics footprint into the whole slide, with eight assets labelled around a map that stays readable on navy.
- **Serve para:** Logistics or asset footprint as a showpiece slide; a change of pace in a light deck.
- **Como montar:** Geography: Brazil by state, full slide. Colour: navy gradient background; all states no fill with white hairline outline; only MG/SP/RJ and RS filled with a blue gradient that brightens at the centre. Labels: outside the map, five on the right and three on the left, bold white name plus grey one-line spec. Overlays: white freeform rail lines; 1 pt bright-blue elbow connectors running only horizontal and vertical, ending in a small arrow at the label; framed KPI box top left with numbered circles. Order: background, state outlines, active fills, rail, connectors, labels, KPI box. Collision control: all text is off the map and leaders never cross.

## ★★★ Per-country black-to-red gradient map with plant dots, under an active tab bar
- **Origem:** CSN - ArcelorMittal, p. 26
- **Recorte:** `crops/m_europe_gradient_plants_tabs.jpg`
- **Peça pronta:** `pecas_mapas_a.py::europe_tabs`
- **Função:** Shows a regional network with the two target assets lifted out of an otherwise dark, dense field.
- **Serve para:** Target or acquisition assets inside a wider network; multi-asset sections needing navigation.
- **Como montar:** Geography: Europe by country, cut to the network. Colour: each country its own black-to-red diagonal gradient with white borders; the target countries (Germany, Portugal) in a lighter rose so they read first. Overlays: red dots for network, black for recycling, blue with white ring for target assets; thin elbow rule from each target to a label of name, capacity, type. Legend: one horizontal row above the map. Tabs above: three dark gradient bars; active tab has a dashed red double frame. Order: tabs, legend, countries, highlights, dots, leaders, labels. Labels sit in the white margin off the map.

## ★★★ Map between chamfered gradient panels with rail network
- **Origem:** CSN - ArcelorMittal, p. 23
- **Recorte:** `crops/m_chamfer_panels_rail_map.jpg`
- **Peça pronta:** `pecas_mapas_a.py::chamfer_rail`
- **Função:** Makes the map the hinge of the slide, joining an acquisition history on the left to the rationale on the right.
- **Serve para:** Serial M&A or footprint build-up told as history, map and thesis on one slide.
- **Como montar:** Geography: Brazil by state in very pale grey with white borders. Panels: left and right rosy-grey-to-white gradient shapes whose inner edges are cut diagonally around the map, leaving a hexagonal opening; solid dark-red triangles on the diagonal seams give depth. Overlays: thin dark-red freeform rail lines, dark-red plant dots clustered in the Southeast; large red '27 units' and KPI text at the base. Left panel: year-stamped rows of target logo, swap arrows, acquirer logo, one-line rationale. Right panel: rationale bullets plus a browser-chrome news card. Order: panels, triangles, map, lines, dots, text.

## ★★★ Black-to-red cutout with dashed leaders to logo rows
- **Origem:** Cosan, p. 8
- **Recorte:** `crops/m_gradient_cutout_logo_rows.jpg`
- **Peça pronta:** `pecas_mapas_a.py::cutout_rows`
- **Função:** Assigns each concession to its state and reads like a table, because every leader ends in an aligned row.
- **Serve para:** Concessions, subsidiaries or brands by territory with a metric per row.
- **Como montar:** Geography: only the served coastal and southern states, cut out and enlarged. Colour: black-to-red gradient per state with white borders. Labels: right column of 7 rows, each a logo, share %, vertical rule, volume in mm/day; underlined column header 'Volume m3'. Leaders: black dashed elbow connectors from state to logo, staggered so they don't cross. Order: map, connectors, logos, numbers.

## ★★★ Silhouette on a 100% share bar with stems
- **Origem:** Cury Construtora, p. 13
- **Recorte:** `crops/m_state_on_share_bar.jpg`
- **Peça pronta:** `pecas_mapas_a.py::state_share_bar`
- **Função:** Connects a stacked share bar physically to the geography it splits.
- **Serve para:** Regional allocation of a landbank or asset base.
- **Como montar:** Geography: Sao Paulo and Rio de Janeiro joined as one shape in a blue gradient with darker edge and soft shadow. Below: horizontal 100% bar, SP 72% and RJ 28%, in two blues. Overlays: thin vertical stems with a small foot rising from each segment into the map. Order: bar, stems, map. Labels live inside the bar, so the map stays clean.

## ★★★ Staggered street-map zoom pair with heat overlay on a folded panel
- **Origem:** Intelbras, p. 9
- **Recorte:** `crops/m_staggered_raster_heat_fold.jpg`
- **Peça pronta:** `pecas_mapas_a.py::staggered_heat`
- **Função:** Goes from metro to city in two overlapping maps, showing primary location data rather than a generic footprint.
- **Serve para:** Proprietary spatial analysis of distribution density.
- **Precisa de material real:** peça ao usuário; nunca invente.
- **Como montar:** Geography: real road-map rasters, metro and city. Heat: Google API heat map, blue through green and yellow to red, generated in code and captured as an image. Overlays: star markers for rivals with a small legend; framed label boxes with a diamond-end rule pointing at each map; green dashed callout overlapping the corner. Container: pale grey panel with a chamfered 3D fold into a second panel with KPIs and a dark code screenshot with Python logo. Order: panel, metro raster, city raster offset down-right, stars, labels, callout.

## ★★★ Grey wedge from map into a funnel, with region values
- **Origem:** Nubank, p. 13
- **Recorte:** `crops/m_region_values_wedge_funnel.jpg`
- **Peça pronta:** `pecas_mapas_a.py::wedge_funnel`
- **Função:** Narrows a national population map down to the addressable market in one reading motion.
- **Serve para:** TAM funnels with regional context.
- **Como montar:** Geography: Brazil by state lines, filled by 5-region purple ramp, Northeast darkest. Labels: bold value on each region, white on dark and dark on light. Wedge: grey gradient shape from the map's east edge opening right, fading to white. Funnel: five lilac blocks of shrinking width, each with an italic label and bold number. Order: wedge, map, region values, funnel. Values sit on large regions, so no leaders are needed.

## ★★★ Income contour map with sized pins
- **Origem:** Nubank, p. 25
- **Recorte:** `crops/m_smoothed_income_pins.jpg`
- **Peça pronta:** `pecas_mapas_a.py::income_contour`
- **Função:** Overlays bank branches on income to show visually who the branches ignore.
- **Serve para:** Demand-vs-supply white space.
- **Precisa de material real:** peça ao usuário; nunca invente.
- **Como montar:** Geography: Mexico City with smoothed contours rather than administrative lines. Colour: lilac to deep purple. Overlays: black teardrop pins in 4 sizes by branch concentration; stacked pin-size legend; horizontal gradient bar 'Income level' with 5 ticks. Dark code card with lilac Python tile overlapping top right. Order: contours, pins, legends, code card. Contours need code output or GIS, inserted as an image; pins can stay native.

## ★★★ Staircase chips on hairline leaders
- **Origem:** Nubank, p. 23
- **Recorte:** `crops/m_staircase_pill_leaders.jpg`
- **Peça pronta:** `pecas_mapas_a.py::staircase_chips`
- **Função:** Places each country's metrics in steps down the slide that follow the geography from Mexico to Brazil.
- **Serve para:** Few-country metrics over time.
- **Como montar:** Geography: Latin America, three active countries purple, rest pale grey, no borders emphasised. Labels: lilac rounded chips with 23'/25' and dark purple value pills, each moved down and right to match its country. Leaders: thin grey horizontal lines from country to chip. Flag-and-pill 'Deposits' card below. Order: map, leaders, chips, card.

## ★★★ Region-tint map with white pins and dashed count leaders
- **Origem:** RD Saude, p. 25
- **Recorte:** `crops/m_region_tint_pins_dashed_counts.jpg`
- **Peça pronta:** `pecas_mapas_a.py::region_tint`
- **Função:** Reports store count by region with no legend, because each number takes its region's colour.
- **Serve para:** Capillarity or footprint where the regional total is the message.
- **Como montar:** Geography: Brazil by state, grouped into 5 regions, each a different green, Southeast darkest. Overlays: one white teardrop pin per state. Labels: bold store count outside the map in the region's own colour, joined by a dashed horizontal leader. Left: dashed-frame fact box. Right: pale grey panel with a diagonal edge starting at the map, holding before/after bar pairs. Order: panel, map, pins, leaders, labels.

## ★★★ Small-multiple maps in each competitor's brand hue
- **Origem:** RD Saude, p. 11
- **Recorte:** `crops/m_triptych_brand_maps.jpg`
- **Peça pronta:** `pecas_mapas_a.py::triptych`
- **Função:** Compares regional strength across chains side by side using nothing but each brand's own colour ramp.
- **Serve para:** Competitive footprint comparison.
- **Como montar:** Geography: three identical Brazil maps by state or region. Colour: each map uses one chain's hue, strongest where the chain is strongest (coral with a red Northeast; mint with a dark Southeast; grey with a blue South). Labels: logo centred above each map; rounded chip with total stores at its bottom left, in the same hue. Bars below reuse the hues. Order: logo, map, chip.

## ★★★ Street-map popup with pin legend on a trapezoid connector
- **Origem:** RD Saude, p. 14, 15
- **Recorte:** `crops/m_street_popup_trapezoid_legend.jpg`
- **Peça pronta:** `pecas_mapas_a.py::street_popup`
- **Função:** Shows local competition at street level as a zoom-in that sits on top of the dimmed parent slide.
- **Serve para:** Field research on local competition.
- **Precisa de material real:** peça ao usuário; nunca invente.
- **Como montar:** Geography: real neighbourhood street raster in a green dashed frame. Overlays: teardrop pins by chain (about 45 on p14 in four colours; p15 turns small drugstores black). Legend: green dashed box on the left with coloured pins and chain names in matching colour, joined to the map by a grey trapezoid with dashed green edges. Callout: dashed box at right on p15. Popup: parent slide copied and dimmed under a white shadowed card. Order: dimmed slide, card, connector, raster, pins, legend.

## ★★★ World score choropleth with hatched exclusion and overlapping criteria card
- **Origem:** Restaurant Brands International, p. 38
- **Recorte:** `crops/m_world_score_hatched_criteria.jpg`
- **Peça pronta:** `pecas_mapas_a.py::world_score`
- **Função:** Shows a proprietary score worldwide, and hatching keeps the home market clearly out of the ranking rather than scored low.
- **Serve para:** Market prioritisation scoring.
- **Como montar:** Geography: world by country. Colour: white through pink to deep red; grey for unscored; diagonal hatch (Pattern Fill) for North America. Legend: horizontal gradient bar Low-Medium-High with caption. Overlay: white rounded shadowed card with red square tiles numbered in roman numerals and a Python logo, covering the empty Pacific and part of North America. Order: map, hatch, legend, card.

## ★★★ Stacked before/after dot maps beside stat cards
- **Origem:** Restaurant Brands International, p. 21, 22
- **Recorte:** `crops/m_dot_map_before_after.jpg`
- **Peça pronta:** `pecas_mapas_a.py::dot_maps`
- **Função:** Shows store growth over time through density alone, with the number on the card and the pattern on the map.
- **Serve para:** Unit growth over time.
- **Como montar:** Geography: USA by state in very faint grey lines. Overlays: thousands of tiny dark-red dots, exported from code. Cards: white rounded shadowed cards on the left with a red year and red counts, touching the map's west side; grey double chevron between the two rows. Order: map, dots, card.

## ★★★ Twin choropleths with dashed min/max leaders and icon rail
- **Origem:** Sabesp, p. 3
- **Recorte:** `crops/m_twin_dashed_minmax_icon_rail.jpg`
- **Peça pronta:** `pecas_mapas_a.py::twin_minmax`
- **Função:** Shows two indicators by state, then ties them to the regulatory regimes below.
- **Serve para:** Paired indicators where only the extremes matter.
- **Como montar:** Geography: two Brazil state maps in a blue ramp. Labels: only best and worst values, bold italic, on dashed curved leaders. Legend: one shared horizontal gradient bar between the maps, 0% to 100%. Overlays: cyan stems drop from each map's base with a small cap into a pale-cyan panel holding three diamond icons on a horizontal rail with captions. Order: panel, rail, maps, leaders, values, legend, stems.

## ★★★ Terrain tile on a plinth with dotted leaders into a chart
- **Origem:** Sabesp, p. 33
- **Recorte:** `crops/m_terrain_tile_plinth_leaders.jpg`
- **Peça pronta:** `pecas_mapas_a.py::terrain_plinth`
- **Função:** Explains an operating conflict by physically linking places on a real map to the chart series below.
- **Serve para:** Single-asset case studies.
- **Precisa de material real:** peça ao usuário; nunca invente.
- **Como montar:** Geography: real road and terrain raster of the reservoir system. Overlays: red and navy teardrop pins with bold place names, red dotted distance line labelled 9.32 km, small white note box on the map, pin legend row above. Container: grey panel with a trapezoid plinth narrowing down to a chart. Leaders: dotted blue lines from the pins to each series' legend entry. Order: panel, raster, pins, distance line, plinth, chart, leaders.

## ★★★ Municipal choropleth pair breaking out of a grey panel
- **Origem:** Sabesp, p. 24, 25
- **Recorte:** `crops/m_municipal_pair_panel_breakout.jpg`
- **Peça pronta:** `pecas_mapas_a.py::municipal_pair`
- **Função:** Shows two municipal variables stacked so the viewer sees the same places light up, ahead of the regression that proves it.
- **Serve para:** Proving a geographic correlation.
- **Como montar:** Geography: Sao Paulo state by municipality. Colour: about 8 blue classes plus pale grey for not operated. Container: grey panel with shadow; the map rises out of its top right. Inside the panel: small swatch legend and a bold insight sentence; Python badge at the corner. Stacked twice, with a regression scatter (R2 and p-value boxes) on p24 and a torn-paper news clip on p25. Municipal shapes need GeoJSON and code or a filled-map chart, exported as SVG for editing.

## ★★★ Phased rollout map with status chips and ranked bars
- **Origem:** Vasta, p. 23
- **Recorte:** `crops/m_phased_rollout_card.jpg`
- **Peça pronta:** `pecas_mapas_a.py::phased_rollout`
- **Função:** Sequences market entry in one view, with phase on the map and the score ranking beside it in the same order.
- **Serve para:** Expansion roadmaps.
- **Como montar:** Geography: pale coast shape, sea white, in a rounded card, with italic region name, compass and scale bar. Overlays: magenta pin (entry), magenta dots (pilot), lilac dot (M&A), dark pin (second wave), dotted arc from first to last. Labels: bold city plus coloured status chip, set to the right of each point in a loose column. Beside it: numbered round badges and bars in matching colours, then a table. Order: card, basemap, arc, points, labels, ranking.

## ★★ Pills colour-keyed to states, no leaders
- **Origem:** 3R Petroleum, p. 2
- **Recorte:** `crops/m_pill_chips_cluster_card.jpg`
- **Peça pronta:** `pecas_mapas_b.py::pill_cluster_card`
- **Função:** Avoids all leader clutter by making the colour of the pill the only link to the state.
- **Serve para:** At-a-glance with up to about 4 categories.
- **Como montar:** Geography: Brazil by state in greys, 3 cluster areas in navy, green, dark teal. Labels: stacked rounded pills to the right, same colours, white text. Container: grey card with dark top rule and right shadow bar.

## ★★ Flow arrows out of a highlighted country
- **Origem:** AB InBev, p. 35
- **Recorte:** `crops/m_flow_arrows_expansion.jpg`
- **Peça pronta:** `pecas_mapas_b.py::flow_arrows_country`
- **Função:** Signals planned expansion with hand-drawn looking arrows, showing direction rather than data.
- **Serve para:** Geographic expansion plans.
- **Como montar:** Geography: Latin America by country in grey with white lines, Brazil solid yellow. Overlays: four black curved arrows from inside Brazil outward (Curved Connector or Scribble, with arrowhead); mascot icon on Brazil; thin grey elbow to a dashed box with chevron bullets; italic grey caption over the map. Order: map, highlight, arrows, icon, callout.

## ★★ Coverage circles over a municipal silhouette
- **Origem:** AB InBev, p. 33
- **Recorte:** `crops/m_city_coverage_circles.jpg`
- **Peça pronta:** `pecas_mapas_b.py::city_coverage_circles`
- **Função:** Documents field coverage with translucent circles beside the numbers and photos that prove the visits.
- **Serve para:** Primary-research coverage.
- **Como montar:** Geography: one flat grey municipal shape, no internal lines. Overlays: 8 yellow circles at about 50-60% transparency in varied sizes, which get stronger where they overlap. Paired with a dashed-rule band of huge yellow numbers (27, 10+) and a store photo collage.

## ★★ Code card beside a dot map
- **Origem:** AB InBev, p. 124, 125
- **Recorte:** `crops/m_code_plus_dot_map_us.jpg`
- **Peça pronta:** `pecas_mapas_b.py::code_plus_dot_map`
- **Função:** Proves the data is self-collected by placing the Python script next to the plotted result.
- **Serve para:** Appendix evidence of proprietary data work.
- **Como montar:** Geography: country by state or province in pale blue-grey with white lines (USA with Alaska and Hawaii insets; India). Overlays: orange dots, hundreds on p124 and about 20 larger ones on p125. Left: dark rounded code screenshot with syntax colours. Order: code card, base map, dots. Export the dots from code as a transparent image above a native map.

## ★★ Map clipped by a card, with long rule labels
- **Origem:** Alupar, p. 3
- **Recorte:** `crops/m_map_clipped_rule_labels.jpg`
- **Peça pronta:** `pecas_mapas_a.py::clipped_rules`
- **Função:** Uses a cropped map as a backdrop for three business lines instead of as a data display.
- **Serve para:** Company overview where the map is texture.
- **Como montar:** Geography: east half of Brazil in navy gradient, the rest hidden behind the white company card that sits in front. Overlays: white squiggle freeforms for lines. Labels: three bold-italic headings, each on a long navy rule starting at the map and ending in a small marker, with a grey sub-line underneath. Order: map, white lines, card in front, rules, labels.

## ★★ Diamond markers with overlapping dark plates
- **Origem:** BTG Pactual, p. 120, 121
- **Recorte:** `crops/m_diamond_plates.jpg`
- **Peça pronta:** `pecas_mapas_b.py::diamond_plates`
- **Função:** Attaches a compact mini-profile directly to each country, keeping it on the map instead of in a side table.
- **Serve para:** International entries with a date or licence.
- **Como montar:** Geography: South America; Brazil strong teal-blue, other countries pale blue tints or grey. Overlays: navy diamond on the country's coast, dark grey plate overlapping the land, white title, cyan subtitle. Plain sentence set beneath each plate on the white space. Order: map, plate, diamond in front.

## ★★ Corridor zoom with thick brand-colour rail and dashed stems
- **Origem:** CSN (Liability Management), p. 27
- **Recorte:** `crops/m_corridor_zoom_brand_rail.jpg`
- **Peça pronta:** `pecas_mapas_b.py::corridor_zoom_rail`
- **Função:** Lets the subject company's own yellow take over the slide on a blue state cutout.
- **Serve para:** Single-asset profiles in the asset's own branding.
- **Como montar:** Geography: southeastern states, active blue gradient, neighbours grey. Overlays: thick bright-yellow rail lines. Labels: three stacked corridor blocks (name in olive-yellow, characteristics, impact), joined to the rail by dashed grey vertical stems. Order: states, rail, stems, labels.

## ★★ Full-bleed gradient band with highlighted countries
- **Origem:** CSN (Liability Management), p. 11
- **Recorte:** `crops/m_band_panel_highlight_country.jpg`
- **Peça pronta:** `pecas_mapas_b.py::band_highlight_country`
- **Função:** Stages a regional map on a band that runs off the slide, with the two non-core countries bright against dark.
- **Serve para:** Non-core or target assets abroad.
- **Como montar:** Geography: Europe by country, navy gradient; Germany bright blue, Portugal mid blue. Container: pale-blue horizontal gradient band from the slide's left edge, with blue rule at bottom. Labels: plant name on a rule, blue capacity below, placed in the Atlantic and above.

## ★★ Framed tile with asset-type dots and internal text
- **Origem:** CSN (Liability Management), p. 16
- **Recorte:** `crops/m_framed_tile_asset_dots.jpg`
- **Peça pronta:** `pecas_mapas_b.py::framed_tile_asset_dots`
- **Função:** Combines map, legend and short explanatory lists in one framed exhibit above a production-chain strip.
- **Serve para:** Asset base with a process explanation.
- **Como montar:** Geography: Brazil grey with white state lines, neighbours white with thin outline. Container: pale-blue gradient tile with navy left and bottom edge. Overlays: 3 dot types by asset type; legend box top right; two pale text panels in the Atlantic. Beneath: 3 chain boxes linked by pale bands.

## ★★ Single-diagonal gradient corridor cutout
- **Origem:** CSN - ArcelorMittal, p. 30
- **Recorte:** `crops/m_corridor_cutout_red.jpg`
- **Peça pronta:** `pecas_mapas_b.py::corridor_cutout`
- **Função:** Cuts the country down to only the states of the rail corridor, so the map becomes the shape of the argument.
- **Serve para:** Regional infrastructure next to a valuation table.
- **Como montar:** Geography: only the corridor states, enlarged. Colour: dark red to near black. Overlays: white dashed rail freeform, red dots with dark ring, legend top left, red KPI text beside it. Tab bar with dashed active frame above.

## ★★ Operating-states-only cutout with elbow labels
- **Origem:** CSN - ArcelorMittal, p. 6
- **Recorte:** `crops/m_states_only_elbow_labels.jpg`
- **Peça pronta:** `pecas_mapas_b.py::states_only_elbow`
- **Função:** Omits every irrelevant state so the shape itself says where the company operates.
- **Serve para:** Industrial footprint with plant specs.
- **Como montar:** Geography: only operating states, navy, white borders, others absent. Overlays: blue dots with white ring. Labels: bold-italic blue plant name plus 2 spec lines with thin grey elbow leaders, all placed in the white space where the missing states would be.

## ★★ Per-state gradient with owner dot clusters and bleeding plates
- **Origem:** Cury Construtora, p. 24
- **Recorte:** `crops/m_gradient_dot_clusters_plates.jpg`
- **Peça pronta:** `pecas_mapas_a.py::dot_clusters`
- **Função:** Compares two players' locations in metro clusters while KPIs and a table share the same space.
- **Serve para:** Peer footprint where KPIs must sit on the map.
- **Como montar:** Geography: Brazil by state, navy in the north to mid blue in the south, white borders. Overlays: dark dots vs bright blue dots packed tightly at each metro; legend pair on top. Plates: three translucent pale-blue rectangles bleeding off the right edge over the map. Table: small framed region table overlapping lower left. Order: map, dots, table, plates.

## ★★ Tier choropleth and table in one tile, with dashed callout
- **Origem:** Cury Construtora, p. 7
- **Recorte:** `crops/m_tier_choropleth_table_tile.jpg`
- **Peça pronta:** `pecas_mapas_b.py::tier_choropleth_tile`
- **Função:** Pairs a regional map with its numbers and calls out the one concentration that matters.
- **Serve para:** Market concentration by region.
- **Como montar:** Geography: Brazil by state in 4-5 blues, darkest in the Southeast. Container: pale-blue tile with thin border holding both the map and a borderless table. Callout: dashed elbow from SP/RJ to a small dashed box with the takeaway. Order: tile, map, table, callout.

## ★★ Three-tier choropleth with legend squares
- **Origem:** Intelbras, p. 2
- **Recorte:** `crops/m_three_tier_legend_squares.jpg`
- **Peça pronta:** `pecas_mapas_b.py::three_tier_legend`
- **Função:** Shows service-centre density in three classes at very small size, without a label on the map.
- **Serve para:** At-a-glance slides.
- **Como montar:** Geography: Brazil by state, three brand tiers (dark green, mid green, pale yellow-green). Legend: a row of three squares with class ranges underneath. No leaders. Sits in a column between a dashed text box and a framed KPI list with diamond bullets.

## ★★ Gold-halo bubbles on a grey world
- **Origem:** Kering - Moncler, p. 8, 11, 15
- **Recorte:** `crops/m_gold_halo_bubbles_pair.jpg`
- **Peça pronta:** `pecas_mapas_b.py::gold_halo_bubbles`
- **Função:** Puts a regional figure (revenue share on pp. 11 and 15, growth on p. 8) on a world map while staying inside a luxury palette of grey and gold.
- **Serve para:** Regional revenue mix.
- **Como montar:** Geography: world in flat mid grey on off-white, no borders. Bubbles: dark grey circle sized by share, soft gold glow ring (Glow effect, about 8 pt), white % inside; very small values become a dot in a ring (p8). Labels: bold caps region under each bubble on p15, none on p11. Section header with rule above. Stacked twice on p15 for two brands. Print the % inside every bubble, because the size alone is hard to read.

## ★★ Greyscale class map with dark table panel
- **Origem:** Meliuz, p. 106, 107
- **Recorte:** `crops/m_greyscale_classes_dark_table.jpg`
- **Peça pronta:** `pecas_mapas_b.py::greyscale_dark_table`
- **Função:** A sober accent-free map for backup data, where the dark table bleeding off the slide provides the weight.
- **Serve para:** Appendix and data-heavy pages.
- **Como montar:** Geography: Brazil by state in 5 greys, top class (SP and RJ) black. Legend: dashed box at lower left in the empty Pacific side, 5 swatches. Right: dark charcoal panel bleeding off the edge holding a white-lined table and totals. Order: map, legend, panel.

## ★★ Translucent proportional city circles
- **Origem:** Meliuz, p. 4, 5, 6, 7
- **Recorte:** `crops/m_proportional_city_bubbles.jpg`
- **Peça pronta:** `pecas_mapas_b.py::proportional_city_bubbles`
- **Função:** Shows reach by city in a small card, with overlaps naturally darkening the dense Southeast.
- **Serve para:** Reach or penetration by city.
- **Como montar:** Geography: Brazil white with hairline state outlines. Overlays: pink circles at about 50% transparency sized by value. Card 02 of three numbered cards; pink KPIs under. On pp. 4-6 the same slide reveals one card at a time.

## ★★ Brand-colour world with stacked numbers
- **Origem:** Meliuz, p. 88
- **Recorte:** `crops/m_world_brand_kpi_stack.jpg`
- **Peça pronta:** `pecas_mapas_b.py::world_brand_stack`
- **Função:** Gives a simple presence map character by placing three big numbers and the logo in empty ocean.
- **Serve para:** Acquired-company or international presence.
- **Como montar:** Geography: world by country, orange active with thin borders, white land with thin dark outline. Labels: number-plus-word stack (44, 19, 9) at lower left; logo at lower right. No legend.

## ★★ Raster heatmap pair in a navy frame
- **Origem:** Mercado Libre, p. 14, 85
- **Recorte:** `crops/m_raster_heat_frame.jpg`
- **Função:** Presents the team's own distribution-centre analysis as a framed exhibit next to an executive quote.
- **Serve para:** Logistics coverage, especially with interviews.
- **Precisa de material real:** peça ao usuário; nunca invente.
- **Como montar:** Geography: two road-map rasters (southeast South America, Mexico) with pale-blue sea. Heat: blue through green to red blobs. Overlays: red teardrop pins on key cities, dark grey label plates beside them. Container: navy rounded rectangle bleeding off the slide edge, with an italic white caption, short rule and white Python tile. Order: frame, rasters, heat, pins, plates, caption.

## ★★ Ring-percent circles straddling the coast
- **Origem:** Mercado Libre, p. 2
- **Recorte:** `crops/m_latam_ring_percent.jpg`
- **Peça pronta:** `pecas_mapas_b.py::ring_percent_circles`
- **Função:** Reads revenue share per country at once using oversized numbers placed just off the land.
- **Serve para:** Revenue by geography.
- **Como montar:** Geography: Latin America; Brazil near-black navy, Mexico and Argentina mid blues, rest pale lilac. Labels: white circles with black ring carrying the %, sitting on each country's coast. Grey text plate with a left rule and notch runs behind the southern cone. Order: plate, map, circles.

## ★★ Screening cards with flag and magnifier on hairline leaders
- **Origem:** Nubank, p. 44
- **Recorte:** `crops/m_screen_country_cards.jpg`
- **Peça pronta:** `pecas_mapas_b.py::screening_cards`
- **Função:** Explains why each market was rejected with a mini-card anchored directly on the country.
- **Serve para:** Market screening.
- **Como montar:** Geography: Latin America, screened countries purple, rest grey. Cards: rounded pale grey, circular flag, name, magnifier icon, two friction lines with purple keywords. Leaders: thin grey straight lines. Cards sit in the Pacific and Atlantic, so nothing covers land. Filter pills top right.

## ★★ Map at the base of a tabbed summary card
- **Origem:** Nubank, p. 2
- **Recorte:** `crops/m_latam_in_summary_card.jpg`
- **Peça pronta:** `pecas_mapas_b.py::latam_summary_card`
- **Função:** Fills the lower half of a text card with geography so the text block looks finished.
- **Serve para:** At-a-glance slides.
- **Como montar:** Geography: Latin America, active countries purple, rest pale grey, no labels. Container: lilac card with rounded bottom, purple title tab with folded corners. Order: card, text, map.

## ★★ Coloured wedge drill-down holding a map copy
- **Origem:** RD Saude, p. 39
- **Recorte:** `crops/m_wedge_drilldown_map.jpg`
- **Peça pronta:** `pecas_mapas_a.py::wedge_drilldown`
- **Função:** Links one stack segment of a revenue chart to a detail panel that reuses the footprint map as evidence.
- **Serve para:** Revenue build-ups where one line depends on physical footprint.
- **Como montar:** Base: stacked column chart with the e-commerce series in teal and the rest pale grey. Wedge: solid teal shape from that segment opening right into a teal-framed panel. Panel: bars, bold takeaway, then a reduced copy of the region-tint map joined by a dotted frame and stem. Order: chart, wedge, panel, inner content.

## ★★ Mini region-tint map in a card
- **Origem:** RD Saude, p. 2
- **Recorte:** `crops/m_mini_region_tint_card.jpg`
- **Peça pronta:** `pecas_mapas_a.py::mini_tint`
- **Função:** Compresses the footprint for an at-a-glance card without dropping the regional counts.
- **Serve para:** At-a-glance slides.
- **Como montar:** Same recipe as the region-tint map at about a third of the size: 5 green regions, white pins, dashed leaders to counts in region colour, and a dark-green chip with total stores and distribution centres at bottom left. Sits in a framed card with a green top rule.

## ★★ Active states with dashed leaders to logos and a bracket
- **Origem:** Rede D'Or, p. 17
- **Recorte:** `crops/m_logo_leaders_bracket.jpg`
- **Peça pronta:** `pecas_mapas_a.py::logo_bracket`
- **Função:** Shows that local brands were kept by placing each logo beside its state.
- **Serve para:** Multi-brand or acquisition strategies by region.
- **Como montar:** Geography: Brazil by state; inactive states in 3-4 greys, active states navy. Labels: logos in a vertical right-hand column. Leaders: thin dashed horizontal lines from state to logo, then a dashed bracket from the column to the explanatory text. Order: map, leaders, logos, bracket.

## ★★ Mini active-state map, reused as a template
- **Origem:** Rede D'Or, p. 8, 9
- **Recorte:** `crops/m_active_states_mini.jpg`
- **Peça pronta:** `pecas_mapas_a.py::active_mini`
- **Função:** Marks where a company operates at a glance, and the same layout on the next page makes target and acquired company directly comparable.
- **Serve para:** Paired company profiles in M&A decks.
- **Como montar:** Geography: Brazil by state, inactive greys, active navy, no labels. Sits in a light grey tile under a numbered heading with a navy rule. Page 9 repeats the layout with the acquired company's states.

## ★★ Faint province map with proportional dots under a KPI card
- **Origem:** Restaurant Brands International, p. 32
- **Recorte:** `crops/m_canada_dots_kpi_card.jpg`
- **Peça pronta:** `pecas_mapas_b.py::canada_dots_kpi_strip`
- **Função:** Shows white-space cities as a screening result, with the filter outcome stated in a strip above.
- **Serve para:** City-level white-space screens.
- **Como montar:** Geography: Canada by province, faint outline only. Overlays: red circles of varying size along the populated south (the slide does not state the sizing variable). Card: white rounded shadow strip with 3 red KPI tiles and double chevrons, overlapping the top of the map, where there is no data. Above it: red question banner with Python badge and numbered criteria.

## ★★ Adjacency-tier municipal map
- **Origem:** Sabesp, p. 34
- **Recorte:** `crops/m_adjacency_tiers_breakout.jpg`
- **Peça pronta:** `pecas_mapas_b.py::adjacency_tier_map`
- **Função:** Maps network proximity, in tiers by how many municipalities away each one is, to argue the expansion is contiguous.
- **Serve para:** Adjacent expansion theses.
- **Como montar:** Geography: Sao Paulo state by municipality. Colour: navy for the existing network, cyan shades by distance from it, grey for others. Same panel breakout as the municipal pair, with a swatch legend and a bold sentence.

## ★★ Municipal footprint with corner chips
- **Origem:** Sabesp, p. 2
- **Recorte:** `crops/m_municipal_footprint_chips.jpg`
- **Peça pronta:** `pecas_mapas_b.py::municipal_footprint_chips`
- **Função:** Shows a concession footprint at municipal detail with two headline numbers tucked into the empty corners.
- **Serve para:** At-a-glance for regional concessions.
- **Como montar:** Geography: Sao Paulo state by municipality; served in bright cyan, unserved in grey. Container: grey card with a dark right and bottom bar. Overlays: two cyan rounded chips (375 cities, 58% coverage) at the lower corners.

## ★★ Map, grey wedge and bold state letter into block bars
- **Origem:** Sabesp, p. 7
- **Recorte:** `crops/m_wedge_state_to_blocks.jpg`
- **Peça pronta:** `pecas_mapas_b.py::wedge_state_blocks`
- **Função:** Moves from national concession blocks into the blocks inside one state.
- **Serve para:** Regulatory or regional drill-downs.
- **Como montar:** Geography: Brazil by state, cyan to navy, small vertical gradient legend. Connector: cyan dashed line from a framed text box to the map. Wedge: grey shape opening right from Sao Paulo, carrying a large bold 'SP'. Panel: horizontal bars by block with a cyan 'Unified' bracket. Order: panel, wedge, map, letter, bars.

## ★★ Neighbourhood thumbnails with polygon and rent
- **Origem:** Vasta, p. 23
- **Recorte:** `crops/m_neighbourhood_polygon_thumbs.jpg`
- **Peça pronta:** `pecas_mapas_b.py::neighbourhood_thumbs`
- **Função:** Backs the city choice with micro-location evidence, repeated as three uniform cards.
- **Serve para:** Micro-location or real-estate evidence.
- **Precisa de material real:** peça ao usuário; nunca invente.
- **Como montar:** Geography: pale street raster for each neighbourhood. Overlays: magenta pin and translucent pink polygon. Beside each: city chip, neighbourhood name, dotted rule, big R$ number per m2 per month. Three equal cards in a rounded container with a coloured heading.

## ★★ Five-region ramp with values outside in matching tint
- **Origem:** Vasta, p. 27
- **Recorte:** `crops/m_region_ramp_outside_values.jpg`
- **Peça pronta:** `pecas_mapas_b.py::region_ramp_values`
- **Função:** Labels regions with no leaders by colour-matching each number to its region.
- **Serve para:** Regional split in a compact space.
- **Como montar:** Geography: Brazil in 5 regions, violet ramp, Northeast darkest, white borders. Labels: bold percentage placed just outside each region in that region's tint, even when the tint is pale. Caption in italics at top. Thin line runs from the map to the neighbouring panel.

## ★★ Pale map in a tinted tile with two-owner dots
- **Origem:** Vibra, p. 17
- **Recorte:** `crops/m_tile_two_owner_dots.jpg`
- **Peça pronta:** `pecas_mapas_b.py::two_owner_dots_tile`
- **Função:** Shows the combined portfolio's plants by owner in a before/after table layout.
- **Serve para:** Pro forma portfolio after a merger.
- **Como montar:** Geography: Brazil and neighbours in pale grey, no emphasis. Container: pale-green tile holding both map and table. Overlays: bright green vs black dots, legend box top left. Pre-Deal and Pro Forma tags on the boundary between map and table. Order: tile, map, dots, legend, table.

## ★★ Dot density with no outline
- **Origem:** Vibra, p. 23
- **Recorte:** `crops/m_dot_density_no_outline.jpg`
- **Peça pronta:** `pecas_mapas_b.py::dot_density_no_outline`
- **Função:** Lets several thousand stations draw the country on their own.
- **Serve para:** Very dense networks such as stations or stores.
- **Como montar:** Geography: none drawn; the outline emerges from the points. Overlays: small dark-green dots for one network, pale dots for the other, legend box lower left; green-framed text and data cards overlap the empty east. Rebuild: scatter of lat/lon in code exported as transparent PNG or SVG.

## ★★ Map breaking out of a card, with KPI strips over it
- **Origem:** Vibra, p. 27
- **Recorte:** `crops/m_map_breaks_card_kpi_strips.jpg`
- **Peça pronta:** `pecas_mapas_b.py::map_breaks_card_strips`
- **Função:** Adds energy to an A + B = C layout by letting the map escape the card frame.
- **Serve para:** Merger result summaries.
- **Como montar:** Geography: Brazil in grey with white state lines, overlapping the card's left edge and crossing the footer rule. Overlays: tiny markers for factories and distribution centres in two colours, legend box. KPI strips: pale translucent rows with big green numbers, overlapping the map's east side. Order: card, map, markers, strips.

## ★ Flat world fill with soft shadow
- **Origem:** AB InBev, p. 120
- **Recorte:** `crops/m_world_flat_fill_shadow.jpg`
- **Função:** Answers one question ('where?') at near full slide with no labels.
- **Serve para:** Appendix or ESG pages.
- **Como montar:** Geography: world by country, no ocean. Colour: brand yellow vs white with hairline. Effect: soft grey outer shadow on the whole map group gives slight lift. Rebuild with a single SVG of country shapes.

## ★ World highlight with no labels
- **Origem:** AB InBev, p. 51
- **Recorte:** `crops/m_world_highlight_bees.jpg`
- **Função:** Shows platform presence in a small panel under an interview.
- **Serve para:** Footprint in a secondary panel.
- **Como montar:** Geography: world by country; yellow active on mid-grey with white lines. Small italic caption above. No legend or labels.

## ★ Mini world in a framed card
- **Origem:** AB InBev, p. 4
- **Recorte:** `crops/m_mini_world_card_footprint.jpg`
- **Função:** Fills one of three at-a-glance cards with a yellow-grey world above a volume area chart.
- **Serve para:** At-a-glance slides.
- **Como montar:** Geography: world by country, yellow vs grey. Container: pale grey card with yellow top and bottom rule and a centred title on a dashed underline.

## ★ Grey world with per-country red gradient beside a treemap
- **Origem:** CSN - ArcelorMittal, p. 19
- **Recorte:** `crops/m_world_gradient_red.jpg`
- **Função:** Shows global footprint in a small panel, matching the reds of the adjacent regional treemap.
- **Serve para:** At-a-glance for global companies.
- **Como montar:** Geography: world grey, active countries with a black-to-red gradient per shape. No labels. Treemap beside it uses the same reds.

## ★ Aerial photo pair (reference, not a map)
- **Origem:** Cury Construtora, p. 14
- **Recorte:** `crops/m_aerial_photo_pair.jpg`
- **Função:** Compares two sites from above with captioned satellite-style images, the closest thing to a satellite map in the corpus.
- **Serve para:** Site-level comparisons.
- **Precisa de material real:** peça ao usuário; nunca invente.
- **Como montar:** Two equal images side by side with a coloured title and grey caption beneath. Needs real imagery.

## ★ State filled with its own flag, plus dashed bracket
- **Origem:** Intelbras, p. 17
- **Recorte:** `crops/m_flag_filled_state_bracket.jpg`
- **Função:** Turns a small supporting stat into a memorable mark by filling the state with its flag.
- **Serve para:** Small local-market panel.
- **Como montar:** Geography: Sao Paulo state as one shape. Fill: the actual state flag clipped to the shape (rebuild with a picture fill or Merge Shapes). Overlays: green dashed bracket from the sigma label to a dashed rounded note. Order: flag shape, bracket, note. This is a decorative choice and suits one small panel only.

## ★ Map in a rounded panel with flag legend
- **Origem:** Nubank, p. 43
- **Recorte:** `crops/m_latam_panel_flag_legend.jpg`
- **Função:** A clean supporting map where flags replace both legend and labels.
- **Serve para:** Share by country beside a main chart.
- **Como montar:** Geography: Latin America, active countries purple, rest pale grey. Container: huge rounded pale-grey panel bleeding right. Legend: flag rectangle and ~% rows at top right, in the empty Atlantic.

## ★ World crop bleeding off the slide with dashed selection box
- **Origem:** Vibra, p. 26
- **Recorte:** `crops/m_world_crop_selection_bleed.jpg`
- **Função:** Points to the international assets being sold using a small, cut-off map rather than a full panel.
- **Serve para:** Small supporting geography beside a table.
- **Como montar:** Geography: world crop cut by the right edge of the slide. Colour: USA bright green, Brazil dark green, rest pale grey. Overlays: dashed green box running across the top of the map from the USA toward Europe, thin rule from the table to the box. Order: map, box, rule.
