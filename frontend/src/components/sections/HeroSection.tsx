import { useAuth } from "react-oidc-context";
import { useNavigate } from "react-router-dom";

const highlights = [
  "Automated planning",
  "Personalized recommendations",
  "Real-time updates",
];

const HeroSection = () => {
  const auth = useAuth();
  const navigate = useNavigate();

  const handlePrimaryAction = () => {
    if (auth.isAuthenticated) {
      navigate("/dashboard");
      return;
    }

    auth.signinRedirect();
  };

  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-slate-50 to-white pt-16 pb-20">
      <div className="mx-auto flex max-w-6xl flex-col gap-12 px-6 lg:flex-row lg:items-center">
        <div className="flex-1 text-slate-900">
          <span className="inline-flex items-center gap-2 rounded-full bg-yellow-100 px-4 py-1 text-sm font-medium text-yellow-800 shadow-sm">
            <span className="h-2 w-2 rounded-full bg-yellow-500" />
            AI trip planning
          </span>
          <h1 className="mt-6 text-4xl font-semibold leading-tight text-slate-900 sm:text-5xl">
            Plan your perfect trip in minutes
          </h1>
          <p className="mt-4 text-lg text-slate-600">
            Automated, intelligent, and flexible travel planning. AI builds the optimal route,
            suggests attractions, and adapts in real time.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <button
              onClick={handlePrimaryAction}
              className="rounded-full bg-white px-10 py-3 text-base font-semibold text-slate-900 shadow-[0_18px_48px_rgba(251,191,36,0.45)] ring-1 ring-white/70 transition hover:-translate-y-0.5 hover:shadow-[0_24px_65px_rgba(251,191,36,0.55)]"
            >
              Start planning
            </button>
          </div>
          <div className="mt-10 flex flex-wrap gap-x-8 gap-y-3 text-sm font-medium text-slate-500">
            {highlights.map((item) => (
              <div key={item} className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                {item}
              </div>
            ))}
          </div>
        </div>
        <div className="flex-1">
          <div className="rounded-3xl border border-slate-100 bg-white p-3 shadow-[0_30px_60px_rgba(15,23,42,0.12)]">
            <img
              src="/banner.png"
              alt="Trip planning map"
              className="h-full w-full rounded-[28px] object-cover"
            />
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
