[out:json][timeout:180];
(
  area(3600062273)->.roi;
  area(3600156393)->.ni;
);
(
  nwr(area.roi)["place_of_worship"="holy_well"];
  nwr(area.ni)["place_of_worship"="holy_well"];
);
out meta;
