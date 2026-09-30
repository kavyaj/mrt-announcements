// Singapore MRT network data used by index.html.
// Coordinates follow the layout of the official system map (1092 px square).
// [x, y, label side: r/l/t/b]
const ST = {
  "Jurong East": [182, 592, "b"], "Bukit Batok": [190, 527, "r"], "Bukit Gombak": [190, 478, "r"],
  "Choa Chu Kang": [190, 420, "r"], "Yew Tee": [190, 361, "l"], "Kranji": [190, 306, "l"],
  "Marsiling": [215, 241, "l"], "Woodlands": [275, 228, "l"], "Admiralty": [348, 228, "t"],
  "Sembawang": [392, 228, "b"], "Canberra": [436, 228, "t"], "Yishun": [482, 242, "r"],
  "Khatib": [505, 271, "r"], "Yio Chu Kang": [505, 306, "r"], "Ang Mo Kio": [505, 339, "r"],
  "Bishan": [505, 378, "t"], "Braddell": [505, 404, "r"], "Toa Payoh": [505, 434, "r"],
  "Novena": [492, 472, "r"], "Newton": [470, 500, "b"], "Orchard": [430, 551, "r"],
  "Somerset": [490, 585, "r"], "Dhoby Ghaut": [525, 627, "t"], "City Hall": [575, 705, "r"],
  "Raffles Place": [575, 738, "r"], "Marina Bay": [590, 787, "l"], "Marina South Pier": [620, 817, "r"],

  "Pasir Ris": [925, 378, "r"], "Tampines": [930, 410, "r"], "Simei": [925, 437, "l"],
  "Tanah Merah": [913, 460, "b"], "Bedok": [850, 460, "b"], "Kembangan": [800, 483, "r"],
  "Eunos": [765, 515, "r"], "Paya Lebar": [733, 548, "r"], "Aljunied": [709, 578, "l"],
  "Kallang": [686, 600, "r"], "Lavender": [660, 623, "r"], "Bugis": [637, 650, "r"],
  "Tanjong Pagar": [486, 752, "t"], "Outram Park": [445, 704, "l"], "Tiong Bahru": [405, 681, "l"],
  "Redhill": [385, 657, "l"], "Queenstown": [362, 634, "r"], "Commonwealth": [342, 614, "r"],
  "Buona Vista": [320, 592, "r"], "Dover": [275, 592, "b"], "Clementi": [238, 592, "t"],
  "Chinese Garden": [148, 592, "t"], "Lakeside": [113, 592, "b"], "Boon Lay": [79, 557, "l"],
  "Pioneer": [79, 527, "r"], "Joo Koon": [79, 498, "r"], "Gul Circle": [79, 468, "r"],
  "Tuas Crescent": [79, 438, "r"], "Tuas West Road": [79, 409, "r"], "Tuas Link": [79, 380, "r"],
  "Expo": [975, 493, "b"], "Changi Airport": [1032, 493, "b"],

  "HarbourFront": [435, 792, "b"], "Chinatown": [483, 678, "r"], "Clarke Quay": [503, 655, "r"],
  "Little India": [546, 558, "r"], "Farrer Park": [548, 527, "r"], "Boon Keng": [548, 497, "r"],
  "Potong Pasir": [560, 465, "r"], "Woodleigh": [595, 435, "r"], "Serangoon": [624, 402, "r"],
  "Kovan": [655, 377, "l"], "Hougang": [680, 354, "l"], "Buangkok": [700, 333, "l"],
  "Sengkang": [712, 312, "l"], "Punggol": [756, 262, "r"], "Punggol Coast": [784, 242, "r"],

  "Bras Basah": [588, 657, "b"], "Esplanade": [632, 706, "r"], "Promenade": [696, 722, "r"],
  "Nicoll Highway": [720, 688, "r"], "Stadium": [738, 657, "r"], "Mountbatten": [742, 623, "r"],
  "Dakota": [744, 590, "r"], "MacPherson": [716, 500, "l"], "Tai Seng": [700, 463, "r"],
  "Bartley": [672, 433, "r"], "Lorong Chuan": [575, 383, "t"], "Marymount": [458, 390, "t"],
  "Caldecott": [420, 409, "l"], "Botanic Gardens": [345, 467, "t"], "Farrer Road": [318, 510, "l"],
  "Holland Village": [318, 546, "l"], "one-north": [315, 623, "l"], "Kent Ridge": [322, 657, "l"],
  "Haw Par Villa": [330, 686, "l"], "Pasir Panjang": [348, 712, "l"], "Labrador Park": [372, 740, "l"],
  "Telok Blangah": [398, 764, "l"], "Bayfront": [652, 763, "r"],

  "Bukit Panjang": [266, 339, "r"], "Cashew": [266, 357, "r"], "Hillview": [266, 376, "r"],
  "Hume": [266, 392, "r"], "Beauty World": [266, 408, "r"], "King Albert Park": [266, 425, "r"],
  "Sixth Avenue": [266, 442, "l"], "Tan Kah Kee": [298, 467, "b"], "Stevens": [420, 467, "b"],
  "Rochor": [580, 590, "r"], "Downtown": [615, 773, "r"], "Telok Ayer": [548, 740, "b"],
  "Fort Canning": [480, 641, "l"], "Bencoolen": [598, 628, "l"], "Jalan Besar": [620, 605, "r"],
  "Bendemeer": [650, 572, "l"], "Geylang Bahru": [672, 548, "l"], "Mattar": [700, 522, "l"],
  "Ubi": [757, 475, "r"], "Kaki Bukit": [790, 448, "r"], "Bedok North": [800, 425, "l"],
  "Bedok Reservoir": [845, 413, "t"], "Tampines West": [888, 413, "b"], "Tampines East": [970, 437, "r"],
  "Upper Changi": [970, 462, "r"],

  "Woodlands North": [268, 194, "r"], "Woodlands South": [320, 250, "r"], "Springleaf": [350, 270, "r"],
  "Lentor": [368, 292, "r"], "Mayflower": [386, 313, "r"], "Bright Hill": [402, 335, "r"],
  "Upper Thomson": [420, 374, "l"], "Napier": [420, 497, "l"], "Orchard Boulevard": [420, 524, "l"],
  "Great World": [420, 583, "l"], "Havelock": [420, 613, "r"], "Maxwell": [486, 724, "r"],
  "Shenton Way": [548, 775, "t"], "Gardens by the Bay": [720, 762, "r"], "Tanjong Rhu": [780, 709, "r"],
  "Katong Park": [805, 688, "r"], "Tanjong Katong": [825, 667, "r"], "Marine Parade": [847, 647, "r"],
  "Marine Terrace": [865, 627, "r"], "Siglap": [882, 607, "r"], "Bayshore": [905, 587, "r"],
};

// Lines: code prefix, colour, stops in order (numbers skipped where stations are not open).
const LINES = [
  { id: "NS", color: "#d42e12", stops: [[1,"Jurong East"],[2,"Bukit Batok"],[3,"Bukit Gombak"],[4,"Choa Chu Kang"],[5,"Yew Tee"],[7,"Kranji"],[8,"Marsiling"],[9,"Woodlands"],[10,"Admiralty"],[11,"Sembawang"],[12,"Canberra"],[13,"Yishun"],[14,"Khatib"],[15,"Yio Chu Kang"],[16,"Ang Mo Kio"],[17,"Bishan"],[18,"Braddell"],[19,"Toa Payoh"],[20,"Novena"],[21,"Newton"],[22,"Orchard"],[23,"Somerset"],[24,"Dhoby Ghaut"],[25,"City Hall"],[26,"Raffles Place"],[27,"Marina Bay"],[28,"Marina South Pier"]] },
  { id: "EW", color: "#009645", stops: [[1,"Pasir Ris"],[2,"Tampines"],[3,"Simei"],[4,"Tanah Merah"],[5,"Bedok"],[6,"Kembangan"],[7,"Eunos"],[8,"Paya Lebar"],[9,"Aljunied"],[10,"Kallang"],[11,"Lavender"],[12,"Bugis"],[13,"City Hall"],[14,"Raffles Place"],[15,"Tanjong Pagar"],[16,"Outram Park"],[17,"Tiong Bahru"],[18,"Redhill"],[19,"Queenstown"],[20,"Commonwealth"],[21,"Buona Vista"],[22,"Dover"],[23,"Clementi"],[24,"Jurong East"],[25,"Chinese Garden"],[26,"Lakeside"],[27,"Boon Lay"],[28,"Pioneer"],[29,"Joo Koon"],[30,"Gul Circle"],[31,"Tuas Crescent"],[32,"Tuas West Road"],[33,"Tuas Link"]] },
  { id: "CG", color: "#009645", stops: [[0,"Tanah Merah"],[1,"Expo"],[2,"Changi Airport"]] },
  { id: "NE", color: "#9900aa", stops: [[1,"HarbourFront"],[3,"Outram Park"],[4,"Chinatown"],[5,"Clarke Quay"],[6,"Dhoby Ghaut"],[7,"Little India"],[8,"Farrer Park"],[9,"Boon Keng"],[10,"Potong Pasir"],[11,"Woodleigh"],[12,"Serangoon"],[13,"Kovan"],[14,"Hougang"],[15,"Buangkok"],[16,"Sengkang"],[17,"Punggol"],[18,"Punggol Coast"]] },
  { id: "CC", color: "#fa9e0d", smooth: true, stops: [[1,"Dhoby Ghaut"],[2,"Bras Basah"],[3,"Esplanade"],[4,"Promenade"],[5,"Nicoll Highway"],[6,"Stadium"],[7,"Mountbatten"],[8,"Dakota"],[9,"Paya Lebar"],[10,"MacPherson"],[11,"Tai Seng"],[12,"Bartley"],[13,"Serangoon"],[14,"Lorong Chuan"],[15,"Bishan"],[16,"Marymount"],[17,"Caldecott"],[19,"Botanic Gardens"],[20,"Farrer Road"],[21,"Holland Village"],[22,"Buona Vista"],[23,"one-north"],[24,"Kent Ridge"],[25,"Haw Par Villa"],[26,"Pasir Panjang"],[27,"Labrador Park"],[28,"Telok Blangah"],[29,"HarbourFront"]] },
  { id: "CE", color: "#fa9e0d", stops: [[0,"Promenade"],[1,"Bayfront"],[2,"Marina Bay"]] },
  { id: "DT", color: "#005ec4", stops: [[1,"Bukit Panjang"],[2,"Cashew"],[3,"Hillview"],[4,"Hume"],[5,"Beauty World"],[6,"King Albert Park"],[7,"Sixth Avenue"],[8,"Tan Kah Kee"],[9,"Botanic Gardens"],[10,"Stevens"],[11,"Newton"],[12,"Little India"],[13,"Rochor"],[14,"Bugis"],[15,"Promenade"],[16,"Bayfront"],[17,"Downtown"],[18,"Telok Ayer"],[19,"Chinatown"],[20,"Fort Canning"],[21,"Bencoolen"],[22,"Jalan Besar"],[23,"Bendemeer"],[24,"Geylang Bahru"],[25,"Mattar"],[26,"MacPherson"],[27,"Ubi"],[28,"Kaki Bukit"],[29,"Bedok North"],[30,"Bedok Reservoir"],[31,"Tampines West"],[32,"Tampines"],[33,"Tampines East"],[34,"Upper Changi"],[35,"Expo"]] },
  { id: "TE", color: "#9d5b25", stops: [[1,"Woodlands North"],[2,"Woodlands"],[3,"Woodlands South"],[4,"Springleaf"],[5,"Lentor"],[6,"Mayflower"],[7,"Bright Hill"],[8,"Upper Thomson"],[9,"Caldecott"],[11,"Stevens"],[12,"Napier"],[13,"Orchard Boulevard"],[14,"Orchard"],[15,"Great World"],[16,"Havelock"],[17,"Outram Park"],[18,"Maxwell"],[19,"Shenton Way"],[20,"Marina Bay"],[22,"Gardens by the Bay"],[23,"Tanjong Rhu"],[24,"Katong Park"],[25,"Tanjong Katong"],[26,"Marine Parade"],[27,"Marine Terrace"],[28,"Siglap"],[29,"Bayshore"]] },
];
// Line colour by code prefix (CG/CE share their parent line's colour).
const COLOR = Object.fromEntries(LINES.map(l => [l.id, l.color]));

// station -> list of codes, e.g. "Dhoby Ghaut" -> ["NS24","NE6","CC1"] (branch junction stops numbered 0 are not codes)
const CODES = {};
for (const l of LINES) for (const [n, s] of l.stops) if (n > 0) (CODES[s] ??= []).push(l.id + n);
