"""Browser acceptance test against a running local app; all created work is simulation."""
from __future__ import annotations

import argparse
import json
import platform
import re
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--channel", default="")
    parser.add_argument("--screenshots", default=".runtime/screenshots")
    args = parser.parse_args()
    folder = Path(args.screenshots)
    folder.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, **({"channel": args.channel} if args.channel else {}))
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(args.url, wait_until="domcontentloaded")
        page.get_by_role("heading", name="Klarheit. Dann Umsetzung.").wait_for()
        page.get_by_text("Company Pulse", exact=True).wait_for()
        page.screenshot(path=str(folder / "dashboard.png"), full_page=True)

        routes = {
            "office": "Willkommen im Office.", "organization": "Eine Firma. Acht Verantwortlichkeiten.",
            "departments": "Abteilungen", "agents": "Dein Agententeam", "skills": "Skill Registry",
            "knowledge": "Wissen, das bleibt.", "models": "Modelle & Routing", "settings": "Einstellungen",
            "processes": "Geschäftsprozesse", "runs": "Prozessläufe", "approvals": "Freigaben & Recovery",
            "retrospectives": "Retrospektiven-Räume",
        }
        for route, title in routes.items():
            page.goto(f"{args.url}/#/{route}", wait_until="domcontentloaded")
            page.get_by_role("heading", name=title, exact=True).wait_for()
            if route in {"office", "agents", "processes"}:
                page.screenshot(path=str(folder / f"{route}.png"), full_page=True)
            assert page.locator(".global-error").count() == 0

        page.goto(f"{args.url}/#/office")
        page.locator(".office-actor").nth(8).wait_for()
        performance = page.evaluate("""async () => {
            const actors = [...document.querySelectorAll('.office-actor')];
            const clones = [];
            for (let i=actors.length; i<50; i++) {
                const clone = actors[i % actors.length].cloneNode(true);
                clone.setAttribute('aria-hidden','true');
                clone.style.opacity = '.6';
                actors[0].parentNode.appendChild(clone); clones.push(clone);
            }
            const frames=[]; let previous=performance.now();
            await new Promise(resolve => {
                function frame(time) { frames.push(time-previous); previous=time;
                    if(frames.length<90) requestAnimationFrame(frame); else resolve(); }
                requestAnimationFrame(frame);
            });
            clones.forEach(c=>c.remove());
            const elapsed=frames.slice(10).reduce((a,b)=>a+b,0);
            return { rendered_actors:50, fps:Math.round(1000/(elapsed/(frames.length-10))) };
        }""")
        assert performance["fps"] >= 30, performance

        page.goto(f"{args.url}/#/processes")
        page.get_by_role("button", name="Prozess vorbereiten").first.click()
        dialog = page.get_by_role("dialog")
        dialog.get_by_label("Ausführung").select_option("simulation")
        dialog.get_by_label("Deine Produktidee").fill("UI-Verifikation: mechanische Uhr mit messbarem Ziel, ohne externe Aktionen")
        dialog.get_by_label("Arbeitstitel").fill("Browser-Smoke · Simulation")
        dialog.get_by_role("button", name="Prozess starten", exact=True).click()
        page.wait_for_url("**/#/runs/*")
        page.get_by_role("heading", name="Browser-Smoke · Simulation").wait_for()
        page.get_by_role("button", name="Freigeben", exact=True).wait_for(timeout=30000)
        run_id = page.url.split("/runs/")[1]
        page.screenshot(path=str(folder / "approval.png"), full_page=True)
        page.get_by_role("button", name="Freigeben", exact=True).click()
        page.get_by_role("heading", name="production approval", exact=True).wait_for(timeout=30000)
        page.get_by_role("button", name="Freigeben", exact=True).click()
        page.locator(".page-heading .badge.completed").wait_for(timeout=30000)
        page.screenshot(path=str(folder / "run.png"), full_page=True)

        page.get_by_role("link", name="Retrospektive vorbereiten").click()
        page.get_by_role("button", name="Retrospektive starten").click()
        page.wait_for_url("**/#/retrospectives/*")
        page.get_by_role("button", name="Freigeben", exact=True).wait_for(timeout=30000)
        page.get_by_role("button", name="Freigeben", exact=True).click()
        page.get_by_role("button", name="Manuelles Sandbox-Experiment starten").wait_for(timeout=30000)
        page.get_by_role("button", name="Manuelles Sandbox-Experiment starten").click()
        page.get_by_label("Ergebnisbelege").fill("Nur Demonstrationsdaten; keine reale Baseline vorhanden.")
        page.get_by_label("Begründung im Vergleich zur Baseline").fill("Ohne echte Baseline ist das Ergebnis nicht eindeutig.")
        page.get_by_role("button", name="Ergebnis dokumentieren").click()
        page.locator(".page-heading .badge.closed").wait_for(timeout=30000)
        page.screenshot(path=str(folder / "retrospective.png"), full_page=True)

        page.goto(f"{args.url}/#/agents/elena")
        page.get_by_role("heading", name="Elena Laurent", exact=True).wait_for()
        page.get_by_role("heading", name="So arbeitet Elena").wait_for()
        page.screenshot(path=str(folder / "elena.png"), full_page=True)

        page.set_viewport_size({"width": 390, "height": 844})
        page.goto(args.url)
        page.get_by_role("heading", name="Klarheit. Dann Umsetzung.").wait_for()
        page.screenshot(path=str(folder / "mobile.png"), full_page=True)
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        page.get_by_role("button", name="Navigation öffnen").click()
        page.get_by_role("navigation").get_by_role("link", name="Office", exact=True).click()
        page.get_by_role("heading", name="Willkommen im Office.").wait_for()
        page.get_by_role("link", name=re.compile(r"^Elena ")).wait_for()
        assert not errors, errors
        print(json.dumps({"browser_errors": errors, "simulation_run": run_id, "routes_verified": len(routes) + 1, "screenshots": str(folder), "office_performance": performance, "reference_environment": {"os": platform.platform(), "processor": platform.processor(), "browser": browser.version}}, ensure_ascii=False))
        browser.close()


if __name__ == "__main__":
    main()
