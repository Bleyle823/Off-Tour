# Sources

Facts used in the plan, with where they came from. Accessed 8 Oct 2026 unless noted.
Drone and unmanned-aircraft citations are **superseded**: they informed an earlier design
that is no longer the product. They are kept so the research trail stays honest.

## Nairobi National Park (active)
- Park rules (disturbance, visitor conduct): https://nairobipark.org/nairobi-national-park-rules/
- KWS park page: https://www.kws.go.ke/nairobi-national-park
- Self-drive and game drives are how visitors already move through the park (KWS / park visitor information; confirm the current circuit map with the warden before any rover runs).
- Draft management plan 2020-2030 (117 km2, fenced on three sides, species, visitor roads): https://conservationalliance.or.ke/publications/3-nairobi-national-park-draft-management-plan/file
- Wildlife (no resident elephants, rhino sanctuary): https://www.nairobinationalpark.com/wildlife
- Visitor numbers 2023-2025 (459,900 in 2025): https://masaimara.ke/masai-mara-tourism-decline/
- KWS conservation fee schedule, October 2025 (confirm which commercial and filming lines apply to a ground vehicle; the drone-day line is not the OFF TOUR tariff): https://www.kws.go.ke/sites/default/files/2025-12/KWS%20Conservation%20Fee%20October%202025.pdf

## Wildlife disturbance (active principle, ground application)
Viewing distance and speed caps in `sim/proximity.py` are **our** conservative defaults for a road vehicle, to be tuned with KWS scientists. They are not copied from aerial studies.

## Remote safari precedent
- PixCams Majete livestreams (free, donation-supported): https://pixcams.com/majete-wildlife-reserve/ and https://pixcams.com/fund-the-wildlife-support-pixcams/
- Majete Verifiable Nature Units (African Parks): https://www.africanparks.org/measuring-what-matters-intact-nature-currency-life

## peaq (docs via MCP, and peaq blog posts supplied by the project owner)
- peaqOS functions: Activate, Scale, Stream, Qualify, Verify, Monetize, Tokenize (docs: /peaqos/functions/*)
- Machine Credit Rating and trust levels (docs: /peaqos/concepts/machine-credit-rating, trust-levels)
- Machine NFT under Economics 2.0 (docs: /peaqos/concepts/machine-nft)
- ERC-8004 and omnichain Escrow (docs: /peaqchain/build/advanced-operations/erc-8004/)
- Roadmap and status caveats (docs: /roadmap)

## Superseded: aerial drones (not the product)
- KCAA, Unmanned Aircraft Systems page: https://kcaa.or.ke/safety-security-oversight/unmanned-aircraft-systems
- KCAA UAS Manual of Implementing Standards: https://kcaa.or.ke/sites/default/files/docs/uas/Manual%20of%20Implementing%20Standards%20(MIS).pdf
- Civil Aviation (UAS) Regulations, 2020: https://new.kenyalaw.org/akn/ke/act/ln/2020/42/eng@2020-04-03
- Civil Aviation (Remote Piloted Aircraft Systems) Regulations, 2017: https://new.kenyalaw.org/akn/ke/act/ln/2017/259/eng@2017-12-22
- AfriScan summary of later UAS regulations, **secondary source**: https://afri-scan.com/ke/drone-regulations
- Terrestrial mammalian responses to UAS approaches (Sci Rep, Botswana): https://www.nature.com/articles/s41598-019-38610-x
- Other drone-disturbance reviews consulted in the retired design are listed in git history of this file if needed.
