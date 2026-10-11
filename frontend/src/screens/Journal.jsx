export default function Journal({ journal, onAgain }) {
  const actualMinutes = journal.actual_minutes ?? journal.minutes;
  const plannedMinutes = journal.planned_minutes;
  const observations = journal.observations ?? [];

  const plannedDuration =
    plannedMinutes == null
      ? null
      : plannedMinutes >= 120
        ? "2+ hours"
        : `${plannedMinutes} minutes`;

  const summary =
    observations.length === 0
      ? "You spent time exploring, but didn't save any written observations. Next time, capture a detail that catches your attention."
      : `You recorded ${observations.length} ${
          observations.length === 1 ? "observation" : "observations"
        } during ${actualMinutes} ${
          actualMinutes === 1 ? "minute" : "minutes"
        } of exploration. Your notes below preserve what you chose to record, along with any questions you had.`;

  return (
    <article className="space-y-6">
      <header>
        <p className="text-monsoon">
          Your Khoj · {actualMinutes}{" "}
          {actualMinutes === 1 ? "minute" : "minutes"} spent
          {" · "}
          {observations.length}{" "}
          {observations.length === 1 ? "observation" : "observations"}
        </p>

        {plannedDuration && (
          <p className="mt-1 text-sm text-monsoon">
            Planned exploration: {plannedDuration}
          </p>
        )}

        <h1 className="mt-1 text-4xl font-extrabold leading-tight tracking-tight">
          {journal.title}
        </h1>
      </header>

      <section className="space-y-2 rounded-lg border-2 border-ink/15 p-4">
        <h2 className="text-xl font-extrabold">Your exploration, in summary</h2>
        <p className="font-story text-lg leading-relaxed">{summary}</p>
        {observations.length > 0 && (
          <p className="text-sm text-monsoon">
            This summary reflects your saved notes; it does not independently
            verify what was observed.
          </p>
        )}
      </section>

      <section className="space-y-4">
        <h2 className="text-2xl font-extrabold">Your field journal</h2>

        {observations.length === 0 ? (
          <p className="text-monsoon">
            No observations were saved for this exploration.
          </p>
        ) : (
          observations.map((observation, index) => (
            <article
              key={observation.id ?? index}
              className="space-y-3 rounded-lg border-2 border-ink/15 p-4"
            >
              {observation.photo?.data_url && (
                <img
                  src={observation.photo.data_url}
                  alt={`Photo attached to observation ${index + 1}`}
                  loading="lazy"
                  className="max-h-80 w-full rounded-md object-contain"
                />
              )}

              <p className="text-xs font-bold uppercase tracking-wide text-monsoon">
                Observation {observations.length - index}
              </p>

              <p className="text-lg leading-relaxed">{observation.text}</p>

              {observation.question && (
                <div className="rounded-md bg-ink/5 p-3">
                  <p className="text-sm font-semibold">Question you recorded</p>
                  <p className="mt-1">{observation.question}</p>
                </div>
              )}

              {observation.explanation && (
                <div className="border-l-2 border-sea pl-3">
                  <p className="text-sm font-semibold">AI explanation</p>
                  <p className="mt-1 font-story text-monsoon">
                    {observation.explanation}
                  </p>
                </div>
              )}

              {observation.offline && (
                <p className="text-sm text-monsoon">
                  Saved on this device; not synced to the server.
                </p>
              )}
            </article>
          ))
        )}
      </section>

      <button
        type="button"
        onClick={onAgain}
        className="w-full rounded-md bg-taxi px-4 py-3 text-lg font-extrabold"
      >
        Start another exploration
      </button>
    </article>
  );
}
