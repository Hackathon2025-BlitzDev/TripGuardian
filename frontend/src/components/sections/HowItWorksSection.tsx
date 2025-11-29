const steps = [
  {
    title: "Set your parameters",
    description:
      "Tell the assistant where you start, when you travel, preferred attraction types, transport, and trip length.",
    icon: "1.",
  },
  {
    title: "AI builds the route",
    description:
      "The algorithm finds relevant attractions, restaurants, and highlights to craft the optimal itinerary.",
    icon: "2.",
  },
  {
    title: "Enjoy the journey",
    description:
      "Receive recommendations, alerts, and dynamic replanning while you travel.",
    icon: "3.",
  },
];

const HowItWorksSection = () => {
  return (
    <section className="bg-white py-20">
      <div className="mx-auto max-w-5xl px-6 text-center">
        <span className="text-sm font-semibold uppercase tracking-[0.3em] text-amber-500">
          How it works
        </span>
        <h2 className="mt-4 text-3xl font-semibold text-slate-900">Three simple steps to a perfect trip</h2>
        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {steps.map((step) => (
            <div
              key={step.title}
              className="rounded-3xl border border-slate-100 bg-white px-6 py-8 text-left shadow-[0_25px_45px_rgba(15,23,42,0.08)]"
            >
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-50 text-lg font-semibold text-amber-500">
                {step.icon}
              </div>
              <h3 className="text-lg font-semibold text-slate-900">{step.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-slate-500">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
