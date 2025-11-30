const samplePlanResponse = {
  text: "Na základe vyhľadávania som našiel niekoľko zaujímavých miest v Prešove a Levoči, ktoré by ste mohli navštíviť počas vašej cesty.\n\n### Zaujímavé miesta v Prešove:\n1. **Banská Bystrica – Námestie SNP**: Toto historické centrum je známe farebnými meštianskymi domami a remeselnými kaviarňami. Môžete sa tu prejsť a vychutnať si atmosféru mesta.\n2. **Motorest Zubor (Zvolen)**: Ak máte chuť na domáce jedlá, tento motorest ponúka rýchle obedy a je skvelým miestom na zastávku.\n\n### Zaujímavé miesta v Levoči:\n1. **Bazilika sv. Jakuba**: Gotická dominanta s najvyšším dreveným oltárom na svete.\n2. **Mestská radnica**: Renesančná budova so známou klietkou hanby.\n\n### Odporúčania na cestu:\n- Zastavte sa v Prešove a ochutnajte lokálnu kávu.\n- Pokračujte do Levoče a spoznajte UNESCO pamiatky.\n- Využite prestávku na obed v Motoreste Zubor.",
  context: {
    mode: "mock",
    query: "Idem z Košíc do Bratislavy, mám 2 hodiny navyše, odporuč mi zaujímavé zastávky.",
    tools_used: [
      {
        name: "PlacesSearchTool",
        arguments: {
          location: "Prešov",
          categories: ["culture", "cafe"],
        },
        output: {
          places: [
            {
              name: "Banská Bystrica – Námestie SNP",
              category: "Historic center",
              highlight: "Farebné meštianske domy, kaviarne a pokojná atmosféra historického jadra.",
              website: "https://www.visitbanskabystrica.sk",
              images: [
                "https://images.unsplash.com/photo-1528901166007-3784c7dd3653?auto=format&fit=crop&w=900&q=80",
                "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=900&q=80",
              ],
            },
            {
              name: "Motorest Zubor",
              category: "Food",
              highlight: "Domáce špeciality, rýchle obedy a parkovanie pri hlavnej trase.",
              website: "https://motorestzubor.sk",
              images: [
                "https://images.unsplash.com/photo-1555992336-cbfdbcad1cf1?auto=format&fit=crop&w=900&q=80",
                "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80",
              ],
            },
          ],
        },
      },
      {
        name: "PlacesSearchTool",
        arguments: {
          location: "Levoča",
          categories: ["culture", "architecture"],
        },
        output: {
          places: [
            {
              name: "Bazilika sv. Jakuba",
              category: "Culture",
              highlight: "Gotický chrám s dielami Majstra Pavla a panoramatickým výhľadom na mesto.",
              website: "https://www.levoca.sk/bazilika-sv-jakuba",
              images: [
                "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=900&q=80",
                "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=900&q=80",
              ],
            },
            {
              name: "Mestská radnica Levoča",
              category: "Architecture",
              highlight: "Renesančná stavba s klietkou hanby a výhľadom na historické jadro Levoče.",
              website: "https://www.levoca.sk/mestska-radnica",
              images: [
                "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=80",
                "https://images.unsplash.com/photo-1470246973918-29a93221c455?auto=format&fit=crop&w=900&q=80",
              ],
            },
          ],
        },
      },
    ],
  },
};

export default samplePlanResponse;
