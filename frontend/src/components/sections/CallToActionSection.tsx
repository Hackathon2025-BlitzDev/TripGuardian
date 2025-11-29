const CallToActionSection = () => {
  return (
    <section className="bg-white py-20">
      <div className="mx-auto max-w-4xl rounded-3xl border border-slate-100 bg-slate-50 px-8 py-12 text-center shadow-[0_35px_65px_rgba(15,23,42,0.08)]">
        <span className="text-sm font-semibold uppercase tracking-[0.35em] text-amber-500">
          Ready for an adventure?
        </span>
        <h2 className="mt-4 text-3xl font-semibold text-slate-900">
          Start planning your next trip today with AI superpowers
        </h2>
        <button className="mt-8 rounded-full bg-slate-900 px-10 py-3 text-base font-semibold text-white shadow-[0_20px_35px_rgba(15,23,42,0.35)] transition hover:-translate-y-0.5 hover:bg-slate-800">
          Create a new trip
        </button>
      </div>
    </section>
  );
};

export default CallToActionSection;
