# Diagrams for the Video

Create 2-4 diagrams that explain what screenshots cannot: architecture, data
flow, data model, request sequence, timeline, or layer stack. One message per
diagram, 7-12 nodes max.

## Preferred: diagram-design skill

Install once (Codex marketplace):

```bash
codex plugin marketplace add cathrynlavery/diagram-design
codex plugin add diagram-design@diagram-design
```

Then ask it directly, e.g. "Make a slide-16x9 architecture diagram of this
repo: FastAPI gateway -> worker queue -> Postgres". Tell it the audience
(engineer/mixed/executive) and that the output feeds a 1080p video.

Type selection by need:

| Need                          | Type                  |
| ----------------------------- | --------------------- |
| System components + links     | Architecture          |
| Pipeline / role-scoped flow   | Data flow / Process   |
| Entities and relations        | ER / data model       |
| Messages over time            | Sequence              |
| Project history / milestones  | Timeline              |
| Abstractions stacked          | Layer stack           |
| Tradeoffs / positioning       | Quadrant              |

Export each diagram to PNG: ask the skill to export (`/diagram-design:export`),
or screenshot the self-contained HTML at 1920x1080 with the capture helper.
Keep the final PNG 1920x1080 with white/light background so text stays legible
on screen.

## Fallback: Mermaid or Graphviz

Mermaid (needs a browser for rendering):

```bash
npx -y @mermaid-js/mermaid-cli -i architecture.mmd -o diagrams/architecture.png -b white -w 1920 -H 1080 -s 2
```

Graphviz:

```bash
dot -Tpng -Gsize=19.2,10.8 -Gdpi=100 architecture.dot -o diagrams/architecture.png
```

## Design rules

- One accent color reserved for the 1-2 things the viewer should notice first.
- Consistent typography and spacing; no decorative clutter.
- Node labels readable at 1080p (>=12px effective font size at 1920 width).
- Every diagram in the video gets a caption telling the viewer what to look at.
