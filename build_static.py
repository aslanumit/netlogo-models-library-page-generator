from __future__ import annotations

import html
import re
from pathlib import Path

import markdown

ROOT_DIR = Path(__file__).resolve().parent
SITE_DIR = ROOT_DIR / "site"
MODELS_DIR = ROOT_DIR / "models"
OUTPUT_MODELS_DIR = SITE_DIR / "models"

INFO_RE = re.compile(r"<info><!\[CDATA\[(.*?)\]\]></info>", re.DOTALL | re.IGNORECASE)


def extract_info(model_path: Path) -> str:
    text = model_path.read_text(encoding="utf-8", errors="ignore")
    match = INFO_RE.search(text)
    if not match:
        return ""
    return match.group(1).strip()


def relative_image_path(model_rel: Path, prefix_to_site: str) -> str | None:
    png_path = MODELS_DIR / model_rel.with_suffix(".png")
    if png_path.exists():
        return f"{prefix_to_site}../models/{model_rel.with_suffix('.png').as_posix()}"
    return None


def netlogoweb_url(model_rel: Path) -> str:
    encoded_path = model_rel.as_posix().replace(" ", "%20")
    return (
        "https://netlogoweb.org/launch#"
        "https://netlogoweb.org/assets/modelslib/"
        f"{encoded_path}"
    )


def render_model_page(
    title: str,
    model_rel: Path,
    info_html: str,
    image_src: str | None,
    stylesheet_href: str,
    back_href: str,
    netlogo_url: str,
) -> str:
    escaped_title = html.escape(title)
    info_block = info_html if info_html else "<p><em>No info tab found.</em></p>"

    image_html = ""
    if image_src:
        image_html = (
            f"<img src=\"{html.escape(image_src)}\" "
            f"alt=\"Screenshot of {escaped_title}\" />"
        )

    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>{escaped_title}</title>
    <link rel=\"stylesheet\" href=\"{html.escape(stylesheet_href)}\" />
  </head>
  <body>
    <main class=\"model-page\">
      <a class=\"back-link\" href=\"{html.escape(back_href)}\">← Back to list</a>
      <div class=\"model-card\">
        <div class=\"model-header\">
          <h1>{escaped_title}</h1>
          <a class=\"run-button\" href=\"{html.escape(netlogo_url)}\" target=\"_blank\" rel=\"noopener\">Run on NetLogoWeb</a>
        </div>
        {image_html}
        <div class=\"model-info\">{info_block}</div>
      </div>
    </main>
  </body>
</html>
"""


def add_to_tree(tree: dict, parts: list[str], path: str) -> None:
    if len(parts) == 1:
        tree.setdefault("files", []).append({"name": parts[0], "path": path})
        return
    folder = parts[0]
    children = tree.setdefault("children", {})
    if folder not in children:
        children[folder] = {}
    add_to_tree(children[folder], parts[1:], path)


def render_tree(tree: dict, prefix: str = "", open_root: bool = False) -> str:
    folders = sorted((tree.get("children") or {}).items(), key=lambda item: item[0].lower())
    files = sorted(tree.get("files", []), key=lambda item: item["name"].lower())

    html_parts: list[str] = ["<ul>"]

    for folder, subtree in folders:
        open_attr = " open" if open_root else ""
        html_parts.append(
            f"<li><details{open_attr}><summary><span class=\"icon folder\">📁</span>{html.escape(folder)}</summary>"
        )
        html_parts.append(render_tree(subtree, prefix=f"{prefix}{folder}/"))
        html_parts.append("</details></li>")

    for file_item in files:
        name = file_item["name"].replace(".nlogox", "")
        html_parts.append(
            f"<li><a href=\"{html.escape(file_item['path'])}\" target=\"_blank\" rel=\"noopener\">"
            f"<img class=\"icon file-icon\" src=\"assets/model.png\" alt=\"\" />"
            f"{html.escape(name)}</a></li>"
        )

    html_parts.append("</ul>")
    return "\n".join(html_parts)


def render_index(tree: dict, count: int) -> str:
    tree_html = render_tree(tree, open_root=False)
    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>NetLogo Models</title>
    <link rel=\"stylesheet\" href=\"styles.css\" />
  </head>
  <body>
    <header class=\"header\">
      <div class=\"header__title\">
        <h1>NetLogo Models</h1>
      </div>
    </header>
    <main class=\"main\">
      <div class=\"stats-row\">
        <div class=\"stats\">{count} models</div>
        <div class=\"header__actions\">
          <button class=\"action-button\" type=\"button\" data-action=\"expand\">
            <span class=\"icon\">➕</span>Expand all folders
          </button>
          <button class=\"action-button\" type=\"button\" data-action=\"collapse\">
            <span class=\"icon\">➖</span>Collapse all folders
          </button>
        </div>
      </div>
      <div class=\"tree\">{tree_html}</div>
    </main>
    <script>
      const detailsNodes = () => Array.from(document.querySelectorAll(".tree details"));
      document.querySelectorAll(".action-button").forEach((button) => {{
        button.addEventListener("click", () => {{
          const expand = button.dataset.action === "expand";
          detailsNodes().forEach((node) => {{
            node.open = expand;
          }});
        }});
      }});
    </script>
  </body>
</html>
"""


def main() -> None:
    OUTPUT_MODELS_DIR.mkdir(parents=True, exist_ok=True)

    model_paths = sorted(MODELS_DIR.rglob("*.nlogox"))
    tree: dict = {}

    for model_path in model_paths:
        model_rel = model_path.relative_to(MODELS_DIR)
        title = model_rel.stem
        info_markdown = extract_info(model_path)
        info_html = markdown.markdown(
            info_markdown,
            extensions=["extra", "tables", "sane_lists"],
        )
        depth = len(model_rel.parts)
        prefix_to_site = "../" * depth
        stylesheet_href = f"{prefix_to_site}styles.css"
        back_href = f"{prefix_to_site}index.html"
        image_src = relative_image_path(model_rel, prefix_to_site)

        output_path = OUTPUT_MODELS_DIR / model_rel.with_suffix(".html")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        page_html = render_model_page(
            title,
            model_rel,
            info_html,
            image_src,
            stylesheet_href,
            back_href,
            netlogoweb_url(model_rel),
        )
        output_path.write_text(page_html, encoding="utf-8")

        link_path = f"models/{model_rel.with_suffix('.html').as_posix()}"
        add_to_tree(tree, [*model_rel.parts[:-1], model_rel.name], link_path)

    index_html = render_index(tree, len(model_paths))
    (SITE_DIR / "index.html").write_text(index_html, encoding="utf-8")


if __name__ == "__main__":
    main()
