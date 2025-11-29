import HeroSection from "../components/sections/HeroSection";
import HowItWorksSection from "../components/sections/HowItWorksSection";
import AdvancedFeaturesSection from "../components/sections/AdvancedFeaturesSection";
import CallToActionSection from "../components/sections/CallToActionSection";

export default function Home() {
  return (
    <main className="bg-white text-slate-900">
      <HeroSection />
      <HowItWorksSection />
      <AdvancedFeaturesSection />
      <CallToActionSection />
    </main>
  );
}