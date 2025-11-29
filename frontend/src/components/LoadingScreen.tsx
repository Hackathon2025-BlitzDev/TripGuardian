export default function LoadingScreen() {
  return (
    <div className="tg-auth">
      <div className="tg-auth__card" role="status" aria-live="polite">
        <div>
          <p className="tg-auth__badge">TripGuardian</p>
          <p className="tg-auth__title">Preparing your travel workspace</p>
          <p className="tg-auth__subtitle">Loading please wait...</p>
        </div>
        <div className="tg-auth__spinner" aria-hidden />
        <div>
          <p className="tg-auth__progress">Securely connecting to your dashboard.</p>
          <span className="tg-auth__highlight">Cognito protected login</span>
        </div>
      </div>
    </div>
  );
}