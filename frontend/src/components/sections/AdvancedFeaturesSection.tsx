const features = [
  {
    title: "Detailed daily itinerary",
    description: "Clear daily agenda with time blocks and estimated travel durations.",
  },
  {
    title: "Real-time monitoring",
    description: "Monitor weather, attraction availability, and transit constraints during the trip.",
  },
  {
    title: "Dynamic replanning",
    description: "Automatically adjust the route whenever conditions change—closures, traffic, or capacity limits.",
  },
  {
    title: "Flexible route editing",
    description: "Add preferences, favorite spots, or reorder stops manually with drag & drop.",
  },
];

const AdvancedFeaturesSection = () => {
  return (
    <section className="bg-gradient-to-b from-indigo-600 via-indigo-500 to-purple-500 py-20 text-white">
      <div className="mx-auto max-w-6xl px-6">
        <div className="text-center">
          <span className="text-sm font-semibold uppercase tracking-[0.35em] text-white/70">
            Advanced features
          </span>
          <h2 className="mt-4 text-3xl font-semibold">Everything you need for a worry-free trip</h2>
        </div>
        <div className="mt-12 grid gap-6 md:grid-cols-2">
          {features.map((feature) => (
            <article
              key={feature.title}
              className="rounded-3xl border border-white/10 bg-white/5 px-6 py-6 shadow-[0_20px_45px_rgba(15,23,42,0.25)] backdrop-blur"
            >
              <h3 className="text-xl font-semibold text-white">{feature.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-white/70">{feature.description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

export default AdvancedFeaturesSection;
