import { useEffect, useState } from "react";
import { createMission, getCities } from "../api.js";
import { downloadPack, loadPack } from "../offline.js";

const DURATIONS = [
  { value: 20, label: "20 min" },
  { value: 45, label: "45 min" },
  { value: 90, label: "90 min" },
  { value: 120, label: "2+ hours" },
];
const INTERESTS = [
  { value: "history", label: "🏛️ History" },
  { value: "architecture", label: "🏗️ Architecture" },
  { value: "nature", label: "🌿 Nature" },
  { value: "art", label: "🎨 Art & culture" },
  { value: "local_life", label: "🍜 Local life" },
  { value: "hidden_details", label: "🔎 Hidden details" },
  { value: "surprise", label: "🎲 Surprise me" },
];
const CITY = "mumbai";

function Choice({ active, onClick, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={`rounded-md border-2 px-3 py-2 text-left font-semibold transition-colors ${
        active ? "border-ink bg-ink text-wall" : "border-ink/25 hover:border-ink"
      }`}
    >
      {children}
    </button>
  );
}

export default function Setup({ onMission }) {
  const [areas, setAreas] = useState([]);
  const [area, setArea] = useState("");
  const [duration, setDuration] = useState(45);
  const [interest, setInterest] = useState("surprise");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [packState, setPackState] = useState(loadPack(CITY) ? "saved" : "none");

  useEffect(() => {
    getCities()
      .then((cs) => setAreas(cs.find((c) => c.city === CITY)?.areas ?? []))
      .catch(() => setAreas(loadPack(CITY)?.meta.areas ?? []));
  }, []);

  async function savePack() {
    setPackState("saving");
    try {
      await downloadPack(CITY);
      setPackState("saved");
    } catch {
      setPackState("none");
      setError("Couldn't download the Mumbai pack. Check your connection and try again.");
    }
  }

  async function go() {
    setBusy(true);
    setError("");
    try {
      onMission(
        await createMission({
          city: CITY,
          area: area || null,
          duration_minutes: duration,
          interest,
        })
      );
    } catch (e) {
      setError(`${e.message} Download the Mumbai pack while you're online to work without a connection.`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-8">
      <header>
        <p lang="hi" className="font-deva text-8xl leading-none text-sea">खोज</p>
        <h1 className="mt-3 text-4xl font-extrabold tracking-tight">Khoj</h1>
        <p className="mt-2 max-w-sm text-lg text-monsoon">
          Don't follow the map. Follow your curiosity.
        </p>
      </header>

      <section aria-labelledby="time">
        <h2 id="time" className="mb-2 font-semibold">How long do you have?</h2>
        <div className="grid grid-cols-4 gap-2">
          {DURATIONS.map((d) => (
            <Choice key={d.value} active={duration === d.value} onClick={() => setDuration(d.value)}>
              {d.label}
            </Choice>
          ))}
        </div>
      </section>

      <section aria-labelledby="style">
        <h2 id="style" className="mb-2 font-semibold">What do you want to notice?</h2>
        <div className="grid grid-cols-2 gap-2">
          {INTERESTS.map((i) => (
            <Choice key={i.value} active={interest === i.value} onClick={() => setInterest(i.value)}>
              {i.label}
            </Choice>
          ))}
        </div>
      </section>

      <section>
        <label htmlFor="area" className="mb-2 block font-semibold">Where in Mumbai?</label>
        <select
          id="area"
          value={area}
          onChange={(e) => setArea(e.target.value)}
          className="w-full rounded-md border-2 border-ink/25 bg-white px-3 py-2"
        >
          <option value="">Anywhere (surprise me)</option>
          {areas.map((a) => <option key={a}>{a}</option>)}
        </select>
      </section>

      {error && <p role="alert" className="rounded-md bg-taxi/30 p-3 text-sm">{error}</p>}

      <div className="space-y-3">
        <button
          type="button"
          onClick={go}
          disabled={busy}
          className="w-full rounded-md bg-taxi px-4 py-3 text-lg font-extrabold text-ink disabled:opacity-60"
        >
          {busy ? "Finding your mission…" : "Get my mission"}
        </button>
        <button
          type="button"
          onClick={savePack}
          disabled={packState === "saving"}
          className="w-full rounded-md border-2 border-sea px-4 py-2 font-semibold text-sea"
        >
          {packState === "saved" && "Mumbai pack saved on this device. Update it"}
          {packState === "saving" && "Downloading…"}
          {packState === "none" && "Download Mumbai pack for offline use"}
        </button>
      </div>
    </div>
  );
}
