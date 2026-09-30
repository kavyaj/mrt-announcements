// Real on-board announcements we have so far.
// kind: "next" = "Next station, X"   |   "arrive" = "X, please mind the platform gap"
// To add a station: drop the mp3 in audio/stations/ and add a line here.
const RECORDINGS = {
  "Farrer Road":      { file: "stations/CC20-farrer-road.mp3",     kind: "arrive" },
  "Holland Village":  { file: "stations/CC21-holland-village.mp3", kind: "arrive" },
  "Beauty World":     { file: "stations/DT5-beauty-world.mp3",     kind: "next" },
  "King Albert Park": { file: "stations/DT6-king-albert-park.mp3", kind: "arrive" },
};
