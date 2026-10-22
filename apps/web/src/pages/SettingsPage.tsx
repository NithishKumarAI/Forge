import { useEffect, useState } from "react";
import { api } from "../services/api";
import type { PlannerSettings } from "../types/adaptive";

export function SettingsPage() {
  const [form, setForm] = useState<PlannerSettings>({
    daily_study_target: 300,
    python_daily_minimum: 45,
    sql_daily_minimum: 30,
    dsa_daily_minimum: 30,
    max_review_topics: 10,
    desired_retention: 0.9,
    study_timezone: "Asia/Kolkata",
  });
  const [message, setMessage] = useState("");

  useEffect(() => {
    api
      .plannerSettings()
      .then(setForm)
      .catch((e) => setMessage(String(e)));
  }, []);

  async function save() {
    try {
      setForm(await api.updatePlannerSettings(form));
      setMessage("Preferences saved successfully.");
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Save failed");
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <h1 className="display text-3xl font-extrabold text-slate-900">Settings</h1>
        <p className="mt-2 text-slate-600">
          Personalize your spaced repetition intervals and timezone. Forge operates offline with deterministic scoring and requires no external API keys.
        </p>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          void save();
        }}
        className="rounded-3xl border border-slate-200 bg-white p-7 shadow-sm space-y-6"
      >
        <div>
          <h2 className="display text-xl font-bold text-slate-900">Study Preferences</h2>
          <p className="mt-1 text-xs text-slate-500">
            Forge follows a concept-by-concept progression. You advance by solving exercises and demonstrating recall, never by logging arbitrary daily hours.
          </p>
        </div>

        <div className="grid gap-5 sm:grid-cols-2">
          <label className="block text-sm font-semibold text-slate-700">
            Study Timezone
            <input
              required
              value={form.study_timezone}
              onChange={(e) => setForm({ ...form, study_timezone: e.target.value })}
              className="mt-2 w-full rounded-xl border border-slate-200 p-3 text-sm focus:border-accent focus:outline-none"
            />
            <span className="mt-1 block text-xs text-slate-400">
              Standard IANA name (e.g. Asia/Kolkata, UTC, America/New_York). Spaced recall uses UTC elapsed time.
            </span>
          </label>

          <label className="block text-sm font-semibold text-slate-700">
            FSRS Desired Retention
            <input
              required
              type="number"
              min={0.7}
              max={0.97}
              step={0.01}
              value={form.desired_retention}
              onChange={(e) => setForm({ ...form, desired_retention: Number(e.target.value) })}
              className="mt-2 w-full rounded-xl border border-slate-200 p-3 text-sm focus:border-accent focus:outline-none"
            />
            <span className="mt-1 block text-xs text-slate-400">
              Recommended: 0.90 (90% target retention rate for spaced repetition scheduling).
            </span>
          </label>

          <label className="block text-sm font-semibold text-slate-700 sm:col-span-2">
            Maximum Review Topics per Batch
            <input
              required
              type="number"
              min={1}
              max={30}
              step={1}
              value={form.max_review_topics}
              onChange={(e) => setForm({ ...form, max_review_topics: Number(e.target.value) })}
              className="mt-2 w-full rounded-xl border border-slate-200 p-3 text-sm focus:border-accent focus:outline-none"
            />
            <span className="mt-1 block text-xs text-slate-400">
              Limits how many due review topics are surfaced together in the spaced repetition queue.
            </span>
          </label>
        </div>

        <div className="border-t border-slate-100 pt-5 flex items-center justify-between">
          <button
            type="submit"
            className="rounded-xl bg-accent px-6 py-3 font-semibold text-white shadow-sm transition hover:bg-violet-700"
          >
            Save Preferences
          </button>
          {message && (
            <p role="status" className="text-sm font-semibold text-emerald-700">
              {message}
            </p>
          )}
        </div>
      </form>
    </div>
  );
}
