const samplePlanResponse = {
  text: "Driving from Košice to Bratislava lets you add four iconic breaks: panoramic Spišský hrad, modern art inside Oravská galéria, the craft heritage of Budatínsky hrad, and sunset views from Trenčiansky hrad. Each stop sits just off the main route, so you can visit them all within a single day.",
  context: {
    mode: "mock",
    query: "Plan a trip from Košice to Bratislava and include iconic stopovers.",
    tools_used: [
      {
        name: "PlacesSearchTool",
        arguments: {
          location: "Spišské Podhradie / Levoča",
          categories: ["unesco", "history"],
        },
        output: {
          places: [
            {
              name: "Spišský hrad (UNESCO)",
              category: "UNESCO",
              highlight: "The largest castle complex in Central Europe with sweeping views of Levoča and the High Tatras.",
              website: "https://www.spisskemuzeum.com/spissky-hrad/",
              coordinates: {
                lat: 48.9997,
                lon: 20.7686,
              },
              images: [
                "/Spis1.jpg",
                "/spis2.webp",
                "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1200&q=80",
              ],
            },
          ],
        },
      },
      {
        name: "PlacesSearchTool",
        arguments: {
          location: "Dolný Kubín / Ružomberok",
          categories: ["art", "gallery"],
        },
        output: {
          places: [
            {
              name: "Oravská galéria",
              category: "Art Gallery",
              highlight: "Modern and regional art displayed inside the historic County House right in Dolný Kubín.",
              website: "https://www.oravskagaleria.sk",
              coordinates: {
                lat: 49.2102,
                lon: 19.296,
              },
              images: [
                "/galeria1.jpg",
                "/galeria2.jpg",
                "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=1200&q=80",
              ],
            },
          ],
        },
      },
      {
        name: "PlacesSearchTool",
        arguments: {
          location: "Žilina",
          categories: ["history", "craft"],
        },
        output: {
          places: [
            {
              name: "Budatínsky hrad – Múzeum drotárstva",
              category: "History",
              highlight: "Renaissance castle at the confluence of the Váh and Kysuca rivers with a museum of master wire artisans.",
              website: "https://www.pmza.sk/budatinsky-hrad",
              coordinates: {
                lat: 49.2308,
                lon: 18.7444,
              },
              images: [
                "/badatin1.jpg",
                "/budatin2.jpg",
                "https://images.unsplash.com/photo-1470246973918-29a93221c455?auto=format&fit=crop&w=1200&q=80",
              ],
            },
          ],
        },
      },
      {
        name: "PlacesSearchTool",
        arguments: {
          location: "Trenčín / toward Bratislava",
          categories: ["castle", "viewpoint"],
        },
        output: {
          places: [
            {
              name: "Trenčiansky hrad",
              category: "Castle",
              highlight: "Dominant fortress of the Považie region with legends of Omar and Fatima plus commanding views over the whole city.",
              website: "https://www.muzeumtn.sk/",
              coordinates: {
                lat: 48.8945,
                lon: 18.0413,
              },
              images: [
                "/trencin1.jpg",
                "/trencin2.jpg",
                "https://images.unsplash.com/photo-1469474968028-3525cd0b379e?auto=format&fit=crop&w=1200&q=80",
              ],
            },
          ],
        },
      },
    ],
  },
};

export default samplePlanResponse;
