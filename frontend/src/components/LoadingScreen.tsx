export default function LoadingScreen() {
  return (
    <div className="min-h-screen bg-loading text-white flex items-center justify-center px-6">
      <div className="flex flex-col items-center gap-4 rounded-3xl border border-white/10 bg-white/5 px-10 py-12 text-center shadow-[0_15px_50px_rgba(0,0,0,0.35)] backdrop-blur">
        <div className="relative h-16 w-16">
          <span className="absolute inset-0 rounded-full border-4 border-white/15" aria-hidden />
          <span className="absolute inset-0 rounded-full border-4 border-transparent border-t-primary border-primary animate-spin" aria-hidden />
        </div>
        <div>
          <p className="text-sm uppercase tracking-[0.45em] text-slate-400">TripGuardian</p>
          <p className="mt-2 text-sm text-slate-400">
            Loading please wait...
          </p>
        </div>
      </div>
    </div>
  );
}