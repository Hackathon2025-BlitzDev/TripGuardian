const samplePlanResponse = [
  {
    tripId: "sample-trip",
    userId: "demo-user",
    status: "planned",
    generatedAt: "2025-11-30T10:15:23.000Z",
    basics: {
      start: "Košice",
      destination: "Bratislava",
      stops: ["Spišský hrad", "Oravská galéria", "Budatínsky hrad", "Trenčiansky hrad"],
      startDate: "2025-12-01",
      endDate: "2025-12-04",
      flexibleDates: false,
    },
    preferences: {
      categories: ["Culture", "Food"],
      transport: "car",
      budget: 500,
    },
    map: {
      markers: [
        {
          id: "start",
          name: "Košice",
          coordinates: { lat: 48.716386, lon: 21.261075 },
          type: "start",
        },
        {
          id: "destination",
          name: "Bratislava",
          coordinates: { lat: 48.148597, lon: 17.107748 },
          type: "destination",
        },
      ],
      routeLine: [
        { lat: 48.716386, lon: 21.261075 },
        { lat: 48.148597, lon: 17.107748 },
      ],
    },
    planResult: {
      summary:
        "Driving from Košice to Bratislava lets you add four iconic breaks: panoramic Spišský hrad, modern art inside Oravská galéria, the craft heritage of Budatínsky hrad, and sunset views from Trenčiansky hrad. Each stop sits just off the main route, so you can visit them all within a single day.",
      locations: [
        {
          location: "Spišské Podhradie / Levoča",
          places: [
            {
              name: "Spišský hrad (UNESCO)",
              category: "UNESCO",
              highlight: "The largest castle complex in Central Europe with sweeping views of Levoča and the High Tatras.",
              website: "https://www.spisskemuzeum.com/spissky-hrad/",
              coordinates: { lat: 48.9997, lon: 20.7686 },
              images: [
                "/Spis1.jpg",
                "/spis2.webp",
                "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1200&q=80",
              ],
            },
          ],
        },
        {
          location: "Dolný Kubín / Ružomberok",
          places: [
            {
              name: "Oravská galéria",
              category: "Art Gallery",
              highlight: "Modern and regional art displayed inside the historic County House right in Dolný Kubín.",
              website: "https://www.oravskagaleria.sk",
              coordinates: { lat: 49.2102, lon: 19.296 },
              images: [
                "/galeria1.jpg",
                "/galeria2.jpg",
                "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=1200&q=80",
              ],
            },
          ],
        },
        {
          location: "Žilina",
          places: [
            {
              name: "Budatínsky hrad – Múzeum drotárstva",
              category: "History",
              highlight: "Renaissance castle at the confluence of the Váh and Kysuca rivers with a museum of master wire artisans.",
              website: "https://www.pmza.sk/budatinsky-hrad",
              coordinates: { lat: 49.2308, lon: 18.7444 },
              images: [
                "/badatin1.jpg",
                "/budatin2.jpg",
                "https://images.unsplash.com/photo-1470246973918-29a93221c455?auto=format&fit=crop&w=1200&q=80",
              ],
            },
          ],
        },
        {
          location: "Trenčín / toward Bratislava",
          places: [
            {
              name: "Trenčiansky hrad",
              category: "Castle",
              highlight: "Dominant fortress of the Považie region with legends of Omar and Fatima plus commanding views over the whole city.",
              website: "https://www.muzeumtn.sk/",
              coordinates: { lat: 48.8945, lon: 18.0413 },
              images: [
                "/trencin1.jpg",
                "/trencin2.jpg",
                "https://images.unsplash.com/photo-1469474968028-3525cd0b379e?auto=format&fit=crop&w=1200&q=80",
              ],
            },
          ],
        },
      ],
    },
  },
];

export default samplePlanResponse;
