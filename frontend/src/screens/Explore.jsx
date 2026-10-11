import { useEffect, useRef, useState } from "react";
import { addObservation, reflect } from "../api.js";
import { getStoredObservations, saveStoredObservation } from "../storage.js";

function useElapsedMinutes() {
  const start = useRef(Date.now());
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 15000);
    return () => clearInterval(timer);
  }, []);

  return Math.max(1, Math.round((now - start.current) / 60000));
}

async function compressPhoto(file) {
  if (!file.type.startsWith("image/")) {
    throw new Error("Please select an image file.");
  }

  if (file.size > 15 * 1024 * 1024) {
    throw new Error("Choose a photo smaller than 15 MB.");
  }

  const imageUrl = URL.createObjectURL(file);

  try {
    const image = new Image();
    image.src = imageUrl;
    await image.decode();

    const maxDimension = 1400;
    const scale = Math.min(
      1,
      maxDimension / Math.max(image.naturalWidth, image.naturalHeight)
    );

    const canvas = document.createElement("canvas");
    canvas.width = Math.max(1, Math.round(image.naturalWidth * scale));
    canvas.height = Math.max(1, Math.round(image.naturalHeight * scale));

    const context = canvas.getContext("2d");
    if (!context) throw new Error("Could not process this photo.");

    context.drawImage(image, 0, 0, canvas.width, canvas.height);

    const blob = await new Promise((resolve, reject) => {
      canvas.toBlob(
        (result) =>
          result
            ? resolve(result)
            : reject(new Error("Could not compress this photo.")),
        "image/jpeg",
        0.78
      );
    });

    return await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(new Error("Could not read this photo."));
      reader.readAsDataURL(blob);
    });
  } finally {
    URL.revokeObjectURL(imageUrl);
  }
}

export default function Explore({ session, onFinish }) {
  const minutes = useElapsedMinutes();
  const fileInput = useRef(null);
  const [done, setDone] = useState({});
  const [observations, setObservations] = useState([]);
  const [text, setText] = useState("");
  const [question, setQuestion] = useState("");
  const [photo, setPhoto] = useState(null);
  const [saving, setSaving] = useState(false);
  const [finishing, setFinishing] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    getStoredObservations(session.session_id)
      .then((saved) => {
        if (active) setObservations(saved);
      })
      .catch(() => {
        if (active) {
          setError("Previous local observations could not be loaded.");
        }
      });

    return () => {
      active = false;
    };
  }, [session.session_id]);

  async function choosePhoto(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    setError("");

    try {
      const dataUrl = await compressPhoto(file);
      setPhoto({
        data_url: dataUrl,
        name: file.name,
        mime_type: "image/jpeg",
      });
    } catch (err) {
      setError(err.message || "Could not prepare this photo.");
    }

    event.target.value = "";
  }

  async function save(event) {
    event.preventDefault();
    if ((!text.trim() && !photo) || saving) return;

    setSaving(true);
    setError("");

    try {
      const pos = await new Promise((resolve) => {
        if (!navigator.geolocation) return resolve({});

        navigator.geolocation.getCurrentPosition(
          (p) =>
            resolve({
              lat: p.coords.latitude,
              lon: p.coords.longitude,
            }),
          () => resolve({}),
          { timeout: 2000 }
        );
      });

      const payload = {
        text: text.trim(),
        question: question.trim() || null,
        ...pos,
      };

      const saved = await addObservation(session, payload);

      const observation = {
        ...saved,
        ...payload,
        id: saved.id || `o-${Date.now()}`,
        photo: photo,
        created_at: Date.now(),
        offline: Boolean(saved.offline || session.session_id.startsWith("local-")),
      };

      await saveStoredObservation(session.session_id, observation);
      setObservations((items) => [
        observation,
        ...items.filter((item) => item.id !== observation.id),
      ]);

      setText("");
      setQuestion("");
      setPhoto(null);
    } catch (err) {
      setError(
        err.name === "QuotaExceededError"
          ? "Device storage is full. Remove some photos and try again."
          : err.message || "Could not save this observation on this device."
      );
    } finally {
      setSaving(false);
    }
  }

  async function finish() {
    if (finishing) return;

    setFinishing(true);
    setError("");

    try {
      const journal = await reflect(session, observations, minutes);

      onFinish({
        ...journal,
        observations,
        actual_minutes: minutes,
        planned_minutes: session.duration_minutes,
      });
    } catch {
      setError("Could not prepare the journal. Your saved observations remain on this device.");
      setFinishing(false);
    }
  }

  return (
    <div className="space-y-6">
      <header className="flex items-baseline justify-between gap-3">
        <h1 className="text-2xl font-extrabold">{session.mission.title}</h1>
        <p className="text-monsoon" aria-live="polite">{minutes} min out</p>
      </header>

      <ul className="space-y-2">
        {session.mission.objectives.map((objective, index) => (
          <li key={index}>
            <label className="flex cursor-pointer items-start gap-3">
              <input
                type="checkbox"
                className="mt-1.5 h-5 w-5 accent-sea"
                checked={!!done[index]}
                onChange={() =>
                  setDone((current) => ({
                    ...current,
                    [index]: !current[index],
                  }))
                }
              />
              <span className={done[index] ? "text-monsoon line-through" : ""}>
                {objective.text}
              </span>
            </label>
          </li>
        ))}
      </ul>

      <form
        onSubmit={save}
        className="space-y-3 rounded-md border-2 border-ink/20 p-4"
      >
        <label htmlFor="obs" className="font-semibold">
          What did you notice?
        </label>
        <textarea
          id="obs"
          rows={3}
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="Describe what you actually saw or heard..."
          className="w-full rounded-md border-2 border-ink/25 bg-white p-2"
        />

        <label htmlFor="q" className="font-semibold">
          A question about it (optional)
        </label>
        <input
          id="q"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="What are you curious about?"
          className="w-full rounded-md border-2 border-ink/25 bg-white p-2"
        />

        <div className="space-y-2">
          <label htmlFor="observation-photo" className="font-semibold">
            Add a photo (optional)
          </label>
          <input
            ref={fileInput}
            id="observation-photo"
            type="file"
            accept="image/*"
            capture="environment"
            onChange={choosePhoto}
            className="block w-full text-sm"
          />

          {photo && (
            <div className="space-y-2">
              <img
                src={photo.data_url}
                alt="Preview of the photo attached to this observation"
                className="max-h-64 w-full rounded-md border object-contain"
              />
              <button
                type="button"
                onClick={() => setPhoto(null)}
                className="text-sm font-semibold text-sea underline"
              >
                Remove photo
              </button>
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={saving || (!text.trim() && !photo)}
          className="rounded-md bg-taxi px-4 py-2 font-extrabold disabled:opacity-50"
        >
          {saving ? "Saving..." : "Save observation"}
        </button>
      </form>

      {error && (
        <p role="alert" className="rounded-md border border-red-700 p-3 text-sm">
          {error}
        </p>
      )}

      {observations.length > 0 && (
        <section className="space-y-3">
          <h2 className="font-semibold">
            Your observations ({observations.length})
          </h2>

          {observations.map((observation) => (
            <article
              key={observation.id}
              className="space-y-2 border-l-4 border-sea pl-3"
            >
              {observation.photo?.data_url && (
                <img
                  src={observation.photo.data_url}
                  alt={`Photo attached to observation: ${observation.text}`}
                  className="max-h-64 w-full rounded-md object-cover"
                />
              )}

              <p>{observation.text}</p>

              {observation.question && (
                <p className="text-sm text-monsoon">
                  Question: {observation.question}
                </p>
              )}

              {observation.explanation && (
                <p className="font-story text-monsoon">
                  AI explanation: {observation.explanation}
                </p>
              )}

              {observation.offline && (
                <p className="text-sm text-monsoon">
                  Saved on this device; not synced to the server.
                </p>
              )}
            </article>
          ))}
        </section>
      )}

      <button
        type="button"
        onClick={finish}
        disabled={finishing}
        className="w-full rounded-md bg-ink px-4 py-3 text-lg font-extrabold text-wall disabled:opacity-60"
      >
        {finishing ? "Writing your journal..." : "Finish and see my journal"}
      </button>
    </div>
  );
}

