"""
End-to-end real browser learning journey verification using isolated Playwright Chromium
and a disposable SQLite database.
"""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
PLAYWRIGHT_MODULE = r"C:\Users\nithi\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\playwright"

sys.path.insert(0, str(ROOT / "scripts"))
from verify_launcher import powershell


def free_port():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def main():
    scratch_dir = ROOT / "scratch"
    scratch_dir.mkdir(exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix="learning-path-browser-", dir=scratch_dir)).resolve()
    db_path = temp_dir / "learner.db"
    runtime_dir = temp_dir / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)

    print(f"Disposable test environment: {temp_dir}")

    environment = {
        **os.environ,
        "FORGE_VERIFY_NO_NETWORK": "1",
        "FORGE_PLAYWRIGHT_MODULE": PLAYWRIGHT_MODULE,
    }

    # 1. Prepare disposable database
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/prepare_browser_fixture.py"), "--database", str(db_path)],
        cwd=ROOT,
        env=environment,
        check=True,
    )

    port = free_port()
    print(f"Launching Forge on isolated port {port}...")

    # 2. Launch Forge server on isolated loopback port
    powershell(
        "open-forge.ps1",
        "-NoBrowser",
        "-RuntimeDir", runtime_dir,
        "-DatabasePath", db_path,
        "-SnapshotPath", temp_dir / "snapshots",
        "-BackupPath", temp_dir / "backups",
        "-PortStart", port,
        "-PortEnd", port,
        "-PreferredPort", port,
    )

    state = json.loads((runtime_dir / "forge-runtime.json").read_text(encoding="utf-8-sig"))
    base_url = state["url"].rstrip("/")
    print(f"Forge server running at: {base_url}")

    journey_js = f"""
const {{ chromium }} = require({json.dumps(PLAYWRIGHT_MODULE)});
const assert = require('node:assert/strict');

async function run() {{
    const browser = await chromium.launch({{ headless: true }});
    const context = await browser.newContext({{ viewport: {{ width: 1280, height: 900 }} }});
    const page = await context.newPage();
    page.setDefaultTimeout(30000);

    const errors = [];
    page.on('pageerror', err => errors.push(String(err)));

    console.log('--- Step 1: Open Dashboard ---');
    await page.goto('{base_url}/');
    await page.getByRole('heading', {{ name: 'Welcome back to Forge.' }}).waitFor();
    console.log('PASS: Dashboard welcome heading rendered');

    console.log('--- Step 2: Verify Removal of Manual Daily Planning ---');
    const oldPlan = await page.getByRole('heading', {{ name: "Today’s study plan", exact: true }}).count();
    assert.equal(oldPlan, 0, 'Old study plan panel must be absent from learner dashboard');

    const regenBtn = await page.getByRole('button', {{ name: 'Regenerate plan safely', exact: true }}).count();
    assert.equal(regenBtn, 0, 'Regenerate plan button must be absent');

    const unallocText = await page.getByText('unallocated minutes', {{ exact: false }}).count();
    assert.equal(unallocText, 0, 'Unallocated minutes message must be absent');
    console.log('PASS: Legacy manual planner controls cleanly removed from dashboard');

    console.log('--- Step 3: Verify Continue Learning Hero Card ---');
    await page.getByText('Continue Learning', {{ exact: false }}).first().waitFor();
    const startLink = page.getByRole('link', {{ name: /Start|Resume|Continue/i }}).first();
    await startLink.waitFor();
    const initialActionHref = await startLink.getAttribute('href');
    console.log('PASS: Continue Learning action ready, linking to:', initialActionHref);

    console.log('--- Step 3b: Verify Concept Teaching View (/concepts/step-py-values-1) ---');
    await page.goto('{base_url}/concepts/step-py-values-1');
    await page.getByRole('heading', {{ name: 'Values, variables and basic types', exact: false }}).waitFor();
    await page.getByText('Concept Meaning & Mental Model', {{ exact: false }}).first().waitFor();
    await page.getByText('Mental Intuition', {{ exact: false }}).first().waitFor();
    await page.getByText('Real-World Analogy', {{ exact: false }}).first().waitFor();
    await page.getByText('Syntax & Mechanics', {{ exact: false }}).first().waitFor();
    await page.getByText('Step-by-Step Execution Trace', {{ exact: false }}).first().waitFor();
    await page.getByText('Common Mistakes & Fixes', {{ exact: false }}).first().waitFor();
    await page.getByText('Key Takeaways Checklist', {{ exact: false }}).first().waitFor();
    console.log('PASS: Concept teaching view renders mental model, trace, mistakes, and checklist');

    console.log('--- Step 4: Test Focus Subject Switcher ---');
    await page.goto('{base_url}/');
    const sqlButton = page.getByRole('button', {{ name: /SQL/i }}).first();
    await sqlButton.click();
    await page.waitForTimeout(500);
    console.log('PASS: Switched focus to SQL');

    const pyButton = page.getByRole('button', {{ name: /Python/i }}).first();
    await pyButton.click();
    await page.waitForTimeout(500);
    console.log('PASS: Switched focus back to Python');

    async function setEditorContent(page, source) {{
        const editor = page.locator('.monaco-editor').first();
        await editor.waitFor({{ state: 'visible', timeout: 30000 }});
        await editor.click({{ position: {{ x: 100, y: 30 }} }});
        await page.keyboard.press('Control+A');
        await page.keyboard.insertText(source);
    }}

    console.log('--- Step 5: Solve Python Beginner Exercise ---');
    await page.goto('{base_url}/arena/exercises/py-first-print-message');
    await page.getByRole('heading', {{ name: 'Print a message', exact: false }}).waitFor();
    await page.getByText('say_hello()', {{ exact: false }}).first().waitFor();

    await setEditorContent(page, 'def say_hello():\\n    return "Hello, Forge!"');
    await page.getByRole('button', {{ name: /Submit/i }}).click();

    await page.getByText(/All test cases passed|100%/i).first().waitFor();
    console.log('PASS: Python beginner exercise solved with isolated worker verification');

    console.log('--- Step 6: Verify Coding Arena 5-Stage Hierarchy ---');
    await page.goto('{base_url}/arena');
    await page.getByRole('heading', {{ name: 'Coding Arena', exact: false }}).waitFor();
    await page.getByText('First Steps', {{ exact: false }}).first().waitFor();
    await page.getByText('Beginner', {{ exact: false }}).first().waitFor();
    await page.getByText('Developing', {{ exact: false }}).first().waitFor();
    await page.getByText('Intermediate', {{ exact: false }}).first().waitFor();
    await page.getByText('Challenging', {{ exact: false }}).first().waitFor();
    console.log('PASS: All 5 progressive exercise stages visible in Coding Arena');

    console.log('--- Step 7: Solve SQL Beginner Exercise with PGlite ---');
    await page.goto('{base_url}/arena/exercises/sql-first-select-constant');
    await page.getByRole('heading', {{ name: 'SELECT a constant', exact: false }}).waitFor();

    // First test bad query
    await setEditorContent(page, 'SELECT 99 AS answer;');
    await page.getByRole('button', {{ name: /Submit/i }}).click();
    await page.getByText(/0\\/1|mismatch|failed|Result mismatch/i).first().waitFor();
    console.log('PASS: Wrong SQL query rejected by PGlite comparison');

    // Submit correct query
    await setEditorContent(page, 'SELECT 42 AS answer;');
    await page.getByRole('button', {{ name: /Submit/i }}).click();
    await page.getByText(/All test cases passed|100%|Query executed successfully/i).first().waitFor();
    console.log('PASS: Correct SQL query accepted by PGlite with 100% score');

    console.log('--- Step 8: Curriculum All Topics Access ---');
    await page.goto('{base_url}/curriculum');
    await page.getByText('Placement Foundations', {{ exact: false }}).first().waitFor();
    console.log('PASS: Curriculum syllabus and topics freely accessible');

    console.log('--- Step 9: Mobile Responsive & Keyboard Focus ---');
    await page.setViewportSize({{ width: 390, height: 844 }});
    await page.goto('{base_url}/');
    await page.getByRole('heading', {{ name: 'Welcome back to Forge.' }}).waitFor();
    const isOverflowing = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    assert.equal(isOverflowing, false, 'Mobile viewport must not have horizontal scroll overflow');

    await page.keyboard.press('Tab');
    const focused = await page.evaluate(() => {{
        const el = document.activeElement;
        return el && el !== document.body;
    }});
    assert.equal(focused, true, 'Keyboard focus outline must be functional');
    console.log('PASS: Mobile responsive layout and keyboard focus verified');

    assert.equal(errors.length, 0, 'No unexpected browser console/page errors allowed: ' + errors.join('; '));

    await browser.close();
    console.log('=== REAL BROWSER LEARNING JOURNEY FULLY PASSED ===');
}}

run().catch(err => {{
    console.error('Browser journey failed:', err);
    process.exit(1);
}});
"""

    journey_file = temp_dir / "journey.cjs"
    journey_file.write_text(journey_js, encoding="utf-8")

    try:
        print("Executing browser journey with Playwright Chromium...")
        subprocess.run(["node", str(journey_file)], cwd=ROOT, env=environment, check=True, timeout=120)
    finally:
        print("Closing Forge server and cleaning up runtime...")
        powershell("close-forge.ps1", "-RuntimeDir", runtime_dir, expected=None)


if __name__ == "__main__":
    main()
