# Controlled values

Every value permitted in a controlled field. Nothing else is accepted —
not a synonym, not a variant, not a close match.

Companion to `INGEST_SPEC.md`. Hand both over together.

<!-- Generated from ksp/vocab/ - do not edit by hand. -->
<!-- Regenerate: python3 tools/render_vocab_doc.py -->

---

## Themes in scope

The system answers questions on these two only. Everything else is refused
as out of scope — which is not a reason to skip tagging it correctly.

| Theme | Pillar | P-1 cluster | P-2 focus area |
|---|---|---|---|
| **Pollution** | PLANET | Urban Liveability | Pollution |
| **Water & Waste** | PLANET | Urban Liveability | Water & Waste |

---

## Sub-pillar — the 4P taxonomy

Two levels. **Tag the P-2 focus area and its P-1 cluster together**, in one
cell: `Pollution;Urban Liveability`.

### PLANET

**Greenhouse Gas Mitigation** — Nature-based Solutions · Mitigation Solutions & Policy · Carbon Markets

> Reduced/removed GHG from human activity through nature-based and tech-based solutions, just transitions to clean energy, other carbon mitigation innovations and policies, and scaling up with carbon markets.

**Urban Liveability** — Urban Heat · Water & Waste · Pollution

> Enhanced urban liveability and quality of living environment through cooling technologies, systems and green cover to combat rising heat, clean water access, proper waste management, and the reduction of harmful pollution.

**Sustainable Natural Ecosystems** — Biodiversity & Ecosystem Balance · Sustainable Agriculture & Food · Oceans & Coastal Protection

> Improved sustainability of natural ecosystems on land and in oceans through biodiversity and ecological health, sustainable agriculture and food systems, and the protection of oceans and coastal habitats.

### PEOPLE

**Global Health** — Zoonotic Diseases · Vector-borne Diseases · Anti-Microbial Resistance

> Improved global health through surveillance, early detection, improved access to diagnostics, vaccines and therapeutics, and response planning for zoonotic and vector-borne diseases exacerbated by climate change and growing anti-microbial resistance.

**Lifelong Health & Well-being** — Maternity Health & Child Development · Mental Health · Nutrition & Healthspan

> Enhanced lifelong health and well-being through improved maternal, neonatal and infant health outcomes, and the reduction of disease burden with better mental health and adequate nutrition.

**Inclusive Development** — Basic Education & School Nutrition · Inclusive Access & Opportunities · Sustained Livelihoods

> Improved inclusive development through greater access to basic and life skills education, school nutrition, and training that enhances employability and entrepreneurship in emerging industries.

### PROGRESS

**Strong Institutions** — Governance & Ethics · Institutional Development · Multilateral Arrangements

> Strengthened institutions through ethics and good governance in leadership, institutional capabilities and development, and effective multilateral arrangements for local and global communities.

**Transformative Knowledge & Innovation** — Research & Development · Innovations for Scalable Impact · Insights for Systemic Change

> Generated transformative knowledge and innovation through research and development, strategic foresight and systems change for impact at scale.

**Catalytic Capital** — Catalytic Philanthropy · Impact/Blended Financing · Socio-Economic Enterprises

> Mobilised catalytic capital and innovative funding instruments that deliver sustained impact through blended finance, catalytic philanthropy, strategic partnerships, and social enterprises.

### PEACE

**Connected Communities** — Youth · Media · Leaders

> Enhanced connectedness between and among communities through youth networks, dialogue among leaders, and the constructive role of media in promoting mutual understanding.

**Engaged & Integrated Society** — Ground-up Mutual Support · Integration & Belonging · Support for Displaced Persons

> Increased engagement of society through ground-up mutual support, and enhanced integration of diverse communities including those displaced by climate, conflict or economic insecurity.

**Identity & Dignity** — Heritage, Culture, Arts · Sports · Dignity of the Vulnerable

> Strengthened sense of identity through the appreciation of and participation in one's own heritage, culture, arts and sports, and support for the dignity of lives of the vulnerable.

---

## Geography

Two levels plus Global. **Tag the country and its region together**, in one
cell: `Indonesia;Southeast Asia`. A document about a whole region carries
just the region. A worldwide document carries `Global` alone.

**Global** — for documents with no specific geography.

**Southeast Asia** — Indonesia, Malaysia, Singapore, Thailand, Vietnam, Philippines, Cambodia, Laos, Myanmar, Brunei, Timor-Leste

**South Asia** — India, Pakistan, Bangladesh, Sri Lanka, Nepal, Bhutan, Maldives, Afghanistan

**East Asia** — China, Japan, South Korea, Mongolia, Taiwan, Hong Kong SAR

**Central Asia** — (no countries listed)

**Oceania** — Australia, New Zealand, Papua New Guinea

**Sub-Saharan Africa** — Kenya, Nigeria, Ethiopia, Ghana, South Africa, Tanzania, Uganda, Rwanda

**Middle East & North Africa** — Egypt, Morocco, United Arab Emirates, Saudi Arabia

**Europe** — United Kingdom, Germany, Netherlands, France, Poland

**European Union** — (no countries listed)

**North America** — United States, Canada

**Latin America & Caribbean** — Brazil, Mexico, Colombia, Peru

---

## The remaining lists

### Pillar

`pillar` on sources.csv. Multi-select.

`PLANET`, `PEOPLE`, `PROGRESS`, `PEACE`

### Source type

`source_type` on sources.csv. Single value.

`Research`, `Policy`, `Media`, `Industry`, `Internal`

### Record type

`record_type` on sources.csv. Single value.

`Document`, `Folder`

### Actor form

`form` on actors.csv. Single value.

`Person`, `Organisation`

### Actor type

`actor_type` on actors.csv. Single value, optional.

`Researcher`, `Implementer`, `Funder`, `Government`, `Advocate`, `Other`

### Origin

`origin` on actors.csv. Single value.

`Manual`, `From LAB`

### Publisher

`publisher` on sources.csv. A publisher name, **or** one of these two:

- `Internal` — Produced internally. There is no external publisher.
- `Unknown` — We looked and could not establish the publisher.

`Not Found` is rejected. It makes *"there isn't one"* look identical to
*"we didn't look"*, and those are different facts.

