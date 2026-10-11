export default function Mission({ session, onStart, onBack }) {
  const { mission, duration_minutes, source } = session;
  return (
    <div className="space-y-6">
      <button type="button" onClick={onBack} className="font-semibold text-sea underline">
        Change setup
      </button>
      <header>
        <p className="text-monsoon">
          {duration_minutes >= 120 ? "2+ hours" : `${duration_minutes} minutes`}
	{source === "curated" ? " · hand-written mission" : " · written by Gemma"}        </p>
        <h1 className="mt-1 text-4xl font-extrabold leading-tight tracking-tight">{mission.title}</h1>
        {mission.intro && <p className="mt-3 font-story text-xl">{mission.intro}</p>}
      </header>
      <ol className="list-decimal space-y-3 pl-6 text-lg marker:font-bold marker:text-sea">
        {mission.objectives.map((o, i) => <li key={i}>{o.text}</li>)}
      </ol>
      <button
        type="button"
        onClick={onStart}
        className="w-full rounded-md bg-ink px-4 py-3 text-lg font-extrabold text-wall"
      >
        Go outside
      </button>
      <p className="text-center text-sm text-monsoon">
        {mission.closing || "Put your phone away and start exploring."}
      </p>
    </div>
  );
}
