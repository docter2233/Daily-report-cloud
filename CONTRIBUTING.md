# Contributing

Thanks for contributing to `Embodied AI Daily Report Cloud`.

## Good First Contributions

- Improve paper-source diversity
- Improve GitHub repo triage rules
- Improve Chinese summary quality
- Improve mobile page layout
- Add more legal open-access discovery paths
- Add more delivery channels

## Before You Open A PR

- Keep the project mobile-first
- Prefer Chinese-readable output over raw source dumping
- Do not add piracy-based download integrations
- Preserve the cloud-first workflow: the digest should still run with the laptop turned off

## Local Dev

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/research_briefing.py collect --days 1 --max-papers 4 --max-repos 3 --public-base-url "https://example.com/"
python scripts/research_briefing.py run --days 1 --max-papers 3 --max-repos 3 --push-provider pushplus --dry-run --token dummy --public-base-url "https://example.com/"
```

## PR Checklist

- Explain what changed and why
- Mention whether the change affects collection, ranking, rendering, or delivery
- Include example output when UI or content structure changes
- Confirm `python -m compileall scripts/research_briefing.py scripts/mobile_digest_helpers.py` passes
- Confirm at least one dry-run digest still works

## Content Rules

- Do not invent formulas, metrics, or claims that are not supported by the source
- If a paper is not open access, keep to legal landing pages only
- If a repo is only weakly relevant, do not force it into the default digest

## Discussions

If you want to propose larger changes to source selection, ranking, or delivery topology, open an issue first.
