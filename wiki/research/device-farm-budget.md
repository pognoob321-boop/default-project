# Device Farm (App/QA Testing): Budget, Requirements & FAQ — Research Report

*Generated: 2026-09-30 | Sources: 25+ | Confidence: High (vendor pricing + published case studies)*

## Executive Summary

A "device farm" for app testing is a pool of real phones/tablets (physical lab) or rented cloud devices that run automated tests (Appium/Espresso/XCUITest/Maestro) in parallel. **Budget ranges from ~$1,200 (4-device DIY starter) to $500K+/year (enterprise)**. The two big cost drivers are (1) labor — 4-8 hrs/week maintenance is the hidden cost, bigger than hardware — and (2) testing volume: cloud wins under ~4 hrs/day of testing, building wins above it (breakeven 12-18 months at 10 devices). Safety is a real requirement: continuously-charged lithium batteries swell and can catch fire; Google publishes weekly inspection + 80% charge cap + thermal monitoring as its mitigations.

---

## 1. What It Is + Architecture Layers

A device farm = orchestrated pool of real devices + emulators connected to a test runner executing a suite across device/OS combos in parallel. Four layers ([dev.to guide](https://dev.to/bhawana127/how-to-build-a-device-farm-a-practical-guide-3gcf)):

1. **Device layer** — physical handsets, emulators, or mix
2. **Connectivity layer** — powered industrial USB hubs, ADB servers, or cloud device APIs
3. **Administration layer** — allocation/health software (open-source: DeviceFarmer/STF; commercial: AstroFarm, DeviceLab)
4. **Test framework + CI** — Appium/Maestro/Espresso/XCUITest + Jenkins/GitHub Actions/GitLab

Three build models:
- **Physical rack (DIY)** — used phones on shelves, USB hubs, cooling; full control, no subscription, you are the repair shop
- **Cloud device farm** — rent real devices per-minute/slot/parallel; zero hardware, live in minutes
- **Hybrid (most common at scale)** — 5-10 owned devices for daily/exploratory testing + cloud for breadth/CI regression

---

## 2. Budget

### 2A. Build your own — hardware (one-time)

| Lab size | Hardware cost | Sources |
|---|---|---|
| **4-device micro stack** (refurb phones, no automation server) | ~$1,200 upfront, <$100/mo | [IMC Grupo](https://www.imcgrupo.com/how-to-build-an-affordable-mobile-testing-stack/) |
| **10-device lab** (phones, industrial hub, Mac Mini, cables, rack, UPS) | $5,600–$14,000 | [DeviceLab cost analysis](https://devicelab.dev/blog/device-lab-cost-analysis), [build guide](https://devicelab.dev/blog/how-to-build-mobile-device-lab) |
| **20-device lab** | $10,600–$23,800 | [DeviceLab](https://devicelab.dev/blog/device-lab-cost-analysis) |
| **50-device lab** | $26,500–$60,500 | [DeviceLab](https://devicelab.dev/blog/device-lab-cost-analysis) |
| **Enterprise (100+ devices)** | $200,000–$500,000+/year (fleet refresh $50-150K + infra $20-50K + software $20-100K + 1-2 FTEs $100-200K) | [DeviceLab scaling](https://devicelab.dev/blog/scaling-mobile-test-infrastructure) |
| **Douyin case study** (5,918 devices, production-grade) | >$1M build; >$0.6M/yr replacements (avg device lifespan only 10 months); 15-engineer team | [MobiCom'23 virtual device farm paper](https://thucloud.com/zhenhua/papers/[MobiCom'23]%20High-Fidelity%20Virtual%20Device%20Farms.pdf) |

**10-device shopping list** ([DeviceLab build guide](https://devicelab.dev/blog/how-to-build-mobile-device-lab)):
- 3 iPhones (mix: e.g. iPhone 15 Pro $999 / iPhone 13 $599 / SE $429) ≈ $1,500
- 5 Android phones (flagship $799 / mid $449 / budget $199 tiers) ≈ $2,000
- 1 Android tablet + 1 iPad ≈ $1,100
- Mac Mini M2 (required for iOS/Xcode/Appium) $599–$799
- Industrial 20-port USB hub $200–$400 (Coolgear/SIIG) — **not** a consumer hub
- Certified cables $300, rack $150, dedicated WiFi router $100, UPS $150-300, misc $200
- **Total ≈ $6,300**

Budget tip: buy refurbished — screen scratches don't affect automated testing ([DeviceLab](https://devicelab.dev/blog/how-to-build-mobile-device-lab), [buildingadevicelab.com (Etsy)](http://buildingadevicelab.com/downloads/building-a-device-lab.pdf)).

### 2B. Ongoing costs (the real budget)

- **Labor is #1**: 4–6 hrs/week for a 10-device lab = $10,400–$31,200/yr at $50-100/hr ([DeviceLab cost analysis](https://devicelab.dev/blog/device-lab-cost-analysis)); ≥20% of an engineer's time if >20 devices ([dev.to](https://dev.to/bhawana127/how-to-build-a-device-farm-a-practical-guide-3gcf))
- Device refresh: 20–30%/yr ($1,000–$1,500 for 10 devices) — Douyin saw 10-month average lifespan under continuous testing ([MobiCom'23](https://thucloud.com/zhenhua/papers/[MobiCom'23]%20High-Fidelity%20Virtual%20Device%20Farms.pdf))
- Electricity $200–300/yr, cable replacement $100/yr
- **First-year total, 10 devices: $16,000–$29,000** ([DeviceLab](https://devicelab.dev/blog/device-lab-cost-analysis))

### 2C. Cloud pricing (rent instead of build)

| Platform | Pricing model | Entry price |
|---|---|---|
| AWS Device Farm | $0.17/device-min **or** $250/device-slot/mo unlimited | 1,000 free min; $250/mo per slot (=concurrency) |
| BrowserStack App Automate | per parallel session | $199/mo (1 parallel); ~$500-800/mo for 5 parallels |
| Sauce Labs Real Device Cloud | per parallel | $199/mo annual / $249 monthly (1 parallel) |
| LambdaTest | per parallel | $99–149/mo real devices |
| Firebase Test Lab | free tier + per-hour | 30 physical min/day free; then $5/physical device-hr |
| Perfecto | per parallel | $300/mo |
| Kobiton | minute bundles | $83/mo (500 min) |

Sources: [DeviceLab cloud calculator](https://devicelab.dev/blog/device-cloud-cost-calculator), [AWS Device Farm FAQ](https://aws.amazon.com/device-farm/faqs/), [AWS vs BrowserStack](https://devicelab.dev/blog/aws-device-farm-vs-browserstack), [Sauce Labs pricing via comparison](https://quashbugs.com/blog/best-aws-device-farm-alternatives)

Key pricing traps:
- AWS per-minute billing at heavy use = **$159K/yr** vs $30K/yr unmetered slots — always model minutes vs slots ([DeviceLab](https://devicelab.dev/blog/device-lab-cost-analysis))
- Per-minute billing explodes linearly; parallel-session pricing scales linearly with concurrency too (10 parallels BrowserStack ≈ $1,990/mo) ([AWS vs BrowserStack](https://devicelab.dev/blog/aws-device-farm-vs-browserstack))
- Firebase free tier is only 30 physical min/day — fine for smoke tests, not regression ([Firebase docs](https://firebase.google.com/docs/test-lab/android/get-started))

### 2D. Build vs cloud decision

| Scenario | Build | Cloud | Winner |
|---|---|---|---|
| 5 devices, light testing | $15K/yr | $5–10K/yr | Cloud |
| 10 devices, daily testing | $18K/yr | $15–25K/yr | Build after Y1 |
| 20 devices, heavy | $25K/yr | $40–80K/yr | Build |
| 50 devices | $50K/yr | $100K+/yr | Build |
| Security-critical/compliance | — | — | Build (data never leaves) |

Breakeven: **10 devices heavy → 10-14 months; 20 devices → 6-12 months; 50 devices → 3-6 months**. Inflection point ≈ 10 devices with 4+ hrs/day testing ([DeviceLab cost analysis](https://devicelab.dev/blog/device-lab-cost-analysis)).

**Recommended default for small teams: hybrid** — 4-8 physical devices for daily/exploratory/bug-repro (~$1,200-3,500) + cloud (Firebase free tier or AWS pay-as-you-go) for nightly regression. Total ~$1,200-2,500 upfront, <$100/mo ([IMC Grupo](https://www.imcgrupo.com/how-to-build-an-affordable-mobile-testing-stack/), [QAlogy](https://qalogy.com/how-to-set-up-a-mobile-device-lab-for-comprehensive-testing/)).

---

## 3. Requirements

### 3A. Hardware
- **Devices**: pick from production analytics (top 10 devices by traffic), mix iOS/Android, flagship/mid/budget tiers, current + previous OS, various screen sizes; start with 8-12 devices covering 70-80% of user base ([DeviceLab](https://devicelab.dev/blog/how-to-build-mobile-device-lab)). Tiered: Tier 0 (3-5 devices, PR smoke) / Tier 1 (10-20, merge regression) / Tier 2 (cloud, nightly) ([beefed.ai](https://beefed.ai/en/scalable-mobile-device-lab))
- **Industrial powered USB hub** — consumer hubs supply 500-900mA, phones need 2-3A → brown-outs and flaky tests. Options: Cambrionix ThunderSync5-C16PD ($1,500+, used by Google/Uber), Acroname USBHub3c ($800+, programmable power), Coolgear 20-port ($300-400), SIIG 20-port ($200-300) ([DeviceLab](https://devicelab.dev/blog/how-to-build-mobile-device-lab))
- **Host computer**: Mac Mini M2 $599+ (mandatory for iOS/Xcode); any PC/NUC $300-800 for Android ([DeviceLab](https://devicelab.dev/blog/how-to-build-mobile-device-lab))
- STF-recommended build: i5 + 8GB RAM + PCIe USB 3.0 card (StarTech PEXUSB3S44V recommended) + 4x Plugable 7-port 60W hubs = ~28 devices per host ([DeviceFarmer/stf README](https://github.com/devicefarmer/stf))
- Certified MFi/USB-IF cables ($100-300), rack/shelving with airflow ($100-300), UPS ($150-300)

### 3B. Software stack
- **Device management**: DeviceFarmer STF (formerly OpenSTF, free/open-source; web remote access; needs Linux, Node.js ≤20, RethinkDB, ADB, Docker; supports Android 2.3.3→15) ([DeviceFarmer/stf](https://github.com/devicefarmer/stf)); `stf local` OK for 10-15 devices, cluster deploy needed beyond ([setup-examples](https://github.com/devicefarmer/setup-examples)); or commercial AstroFarm/DeviceLab
- **Automation framework** (choose one primary):
  - **Appium** — cross-platform default, deepest ecosystem, works with all device clouds; heavy setup (server + UiAutomator2/XCUITest drivers), high maintenance, ~15% flakiness reported ([Qualflare](https://qualflare.com/blog/appium-vs-espresso-vs-xcuitest-vs-maestro/), [QAJobFit](https://qajobfit.com/resources/how-to-choose-mobile-automation-framework))
  - **Maestro** — YAML, lowest learning curve (~1 week), native JUnit-XML; best for simple journeys/new teams ([Qualflare](https://qualflare.com/blog/appium-vs-espresso-vs-xcuitest-vs-maestro/))
  - **Espresso/XCUITest** — native, fastest (99.94% accuracy for Espresso), but single-platform ([codexpedite](https://codexpedite.dev/articles/appium-vs-espresso-vs-xcuitest-vs-detox-vs-maestro-which-mobile-testing-architec))
  - Consensus pick: **Appium for cross-platform E2E**, native frameworks underneath; Maestro if team is non-specialist ([QAJobFit](https://qajobfit.com/resources/how-to-choose-mobile-automation-framework), [QA Wolf](https://www.qawolf.com/blog/best-mobile-app-testing-frameworks-2026))
- **Test distribution**: Selenium Grid or Appium Device Farm plugin ([devicefarm.org](https://devicefarm.org/))
- **CI/CD**: GitHub Actions/GitLab CI free minutes for emulator smoke tests; AWS Device Farm has native Jenkins plugin + CodePipeline action ([AWS docs](https://docs.aws.amazon.com/devicefarm/latest/developerguide/continuous-integration-jenkins-plugin.html))
- Free emulator tier: Android Studio emulator + Xcode Simulator for fast PR checks (can't test camera/Bluetooth/push properly) ([IMC Grupo](https://www.imcgrupo.com/how-to-build-an-affordable-mobile-testing-stack/))

### 3C. Network, power, environment
- **Dedicated WiFi network** (isolated from office), separate VLAN; skip cellular data plans unless testing carrier behavior ([buildingadevicelab.com/Etsy](http://buildingadevicelab.com/downloads/building-a-device-lab.pdf), [QAlogy](https://qalogy.com/how-to-set-up-a-mobile-device-lab-for-comprehensive-testing/))
- WiFi interference is the #1 scaling wall: at Google, radio channel saturation broke connectivity under 1,000 devices; solution was RF-shielded racks with −82 dBm attenuation between racks + 3 APs per rack ([Google research paper](https://research.google/pubs/mobile-applications-on-device-testing-at-google-scale/)). Etsy lesson: boosting signal made interference *worse* — control channels/power instead ([buildingadevicelab.com](http://buildingadevicelab.com/downloads/building-a-device-lab.pdf))
- **Power**: calculate 10-15W/device + 20% headroom; surge protectors; tablets/newer phones plug directly to power supplies, not hubs ([Conbersa](https://www.conbersa.ai/learn/how-to-build-a-phone-farm), [buildingadevicelab.com](http://buildingadevicelab.com/downloads/building-a-device-lab.pdf))
- **Cooling**: keep room <24-26°C, fans per rack level, gaps between devices; Google blocks tests above 45°C device temperature ([Google paper](https://research.google/pubs/mobile-applications-on-device-testing-at-google-scale/))
- Network throttling capability (3G/4G profiles) for degraded-network tests ([AWS FAQ](https://aws.amazon.com/device-farm/faqs/), [yrkan](https://yrkan.com/course/module-07-mobile/device-lab-setup/))

### 3D. Safety requirements (non-negotiable)
Continuously-charged LiPo batteries swell → fire risk ("thermal runaway of even a single device can be catastrophic" — Google):
1. **Cap charge at 80%** (Android Battery Defender; programmable hubs like Acroname can hold 40-60% "comfort zone") ([Google paper](https://research.google/pubs/mobile-applications-on-device-testing-at-google-scale/), [Acroname battery-swell paper](https://acroname.com/sites/default/files/mitigating_battery_swell_in_device_labs.pdf))
2. **Weekly visual inspection**; destroy swollen batteries immediately (Google policy)
3. **Physical gaps** between devices so fire can't jump; fire-rated racks
4. **Active cooling + temperature monitoring**
5. UPS + surge protection

### 3E. People/process requirements
- Inventory doc: model, OS, serial, condition, battery cycles; label every device ([beefed.ai](https://beefed.ai/en/scalable-mobile-device-lab), [yrkan](https://yrkan.com/course/module-07-mobile/device-lab-setup/))
- Weekly reset to clean state; stagger OS updates (never update all at once) ([yrkan](https://yrkan.com/course/module-07-mobile/device-lab-setup/))
- Maintenance hours scale: 6-20 devices = 2-5 hrs/wk; 21-50 = 10-20 hrs/wk; 50+ = FTE ([DeviceLab scaling](https://devicelab.dev/blog/scaling-mobile-test-infrastructure))
- Device hygiene: check passcodes, WiFi, no personal accounts logged in, correct OS ([buildingadevicelab.com](http://buildingadevicelab.com/downloads/building-a-device-lab.pdf))

---

## 4. FAQ — Common Questions About Device Farms

1. **How many devices do I need?** Fewer than you think. Start with 4-8 covering top analytics devices + oldest supported OS + one low-end device; that catches the large majority of hardware-class defects. Don't buy broad coverage you never exercise ([TestMu](https://www.testmuai.com/blog/emulator-vs-simulator-vs-real-device/), [DeviceLab](https://devicelab.dev/blog/how-to-build-mobile-device-lab))
2. **Emulators or real devices?** Both: emulators/simulators for fast PR checks and broad OS coverage; real devices for release gates — they expose camera, GPS, thermal throttling, OEM skin behavior emulators can't. Douyin's virtual farm hit 94.7% recall but still kept physical devices as last-line defense ([MobiCom'23](https://thucloud.com/zhenhua/papers/[MobiCom'23]%20High-Fidelity%20Virtual%20Device%20Farms.pdf), [Testriq](https://www.testriq.com/blog/post/mobile-testing-environment-setup))
3. **Build or buy (cloud)?** Under 10 devices / <4 hrs daily testing → cloud. Over that → build wins, 12-18 mo breakeven. Compliance/data-sovereignty → build regardless ([DeviceLab](https://devicelab.dev/blog/device-lab-cost-analysis))
4. **What's the hidden cost?** Labor. $10K-31K/yr for a 10-device lab — usually exceeds hardware ([DeviceLab](https://devicelab.dev/blog/device-lab-cost-analysis)). Also battery degradation (devices last ~10-30 months under load) and WiFi interference at scale.
5. **Biggest operational failures?** Device disconnects from underpowered hubs; WiFi interference from device density; swollen batteries; devices drifting (wrong OS, personal accounts logged in); flaky tests from non-deterministic state ([Google paper](https://research.google/pubs/mobile-applications-on-device-testing-at-google-scale/), [42Gears](https://www.42gears.com/blog/how-to-build-a-private-mobile-device-lab-enterprise-guide))
6. **iOS requirement?** Yes if you test iOS — Apple requires a Mac (Xcode, WebDriverAgent signing). One Mac Mini handles both iOS and Android via Appium ([DeviceLab](https://devicelab.dev/blog/how-to-build-mobile-device-lab))
7. **Cloud limits to know (AWS)?** 150-min hard cap per run; default 5 concurrent devices (raiseable); app ≤4GB; public device availability not guaranteed; us-west-2 only region ([AWS limits](https://docs.aws.amazon.com/devicefarm/latest/developerguide/limits.html), [MobiCom'23](https://thucloud.com/zhenhua/papers/[MobiCom'23]%20High-Fidelity%20Virtual%20Device%20Farms.pdf))
8. **How does CI integration work?** Build app → upload APK/IPA + test zip → select device pool → run → get video/logs/screenshots. Jenkins plugin, CodePipeline action, or `gcloud firebase test android run` CLI ([AWS docs](https://docs.aws.amazon.com/codepipeline/latest/userguide/tutorials-codebuild-devicefarm.html), [beefed.ai](https://beefed.ai/en/scalable-mobile-device-lab))
9. **Can one phone run multiple accounts/tests?** For QA, one test session per device; parallelism = number of devices (or cloud slots). Sharing causes state contamination — Google factory-resets between runs ([Google paper](https://research.google/pubs/mobile-applications-on-device-testing-at-google-scale/))
10. **When does it break even?** See table in §2D. Rule of thumb: >4 hrs/day testing on >10 devices → build.

---

## Key Takeaways

1. **Start hybrid, not all-in**: $1,200-3,500 for 4-8 physical devices + free/cheap cloud tiers; expand only when testing volume proves it (<10 min to decide: check your CI's weekly device-minutes).
2. **Budget labor, not just hardware**: expect $10K+/yr maintenance for a 10-device lab; hardware is a one-time ~$6K.
3. **Industrial USB hub + Mac Mini are the two non-negotiable purchases** for a DIY lab — cheap hubs cause most "mysterious" flaky tests.
4. **Battery safety is a hard requirement**: 80% charge cap + weekly swollen-battery inspections + cooling, or you risk fire (Google treats this as catastrophic).
5. **Framework default**: Appium for cross-platform E2E (or Maestro if no automation specialists); emulators for PR smoke, real devices for release gates.

## Sources

1. [How to Build a Mobile Device Lab — DeviceLab](https://devicelab.dev/blog/how-to-build-mobile-device-lab) — full hardware shopping list, costs, hub warnings
2. [Build vs Buy Device Lab Cost Analysis — DeviceLab](https://devicelab.dev/blog/device-lab-cost-analysis) — tiered budgets, breakeven tables
3. [Scaling Mobile Test Infrastructure 10→50+ — DeviceLab](https://devicelab.dev/blog/scaling-mobile-test-infrastructure) — maintenance hours, enterprise budgets
4. [Device Lab Cost Calculator — DeviceLab](https://devicelab.dev/blog/device-cloud-cost-calculator) — cloud vendor pricing comparison
5. [AWS Device Farm vs BrowserStack — DeviceLab](https://devicelab.dev/blog/aws-device-farm-vs-browserstack) — slot vs parallel pricing
6. [AWS Device Farm FAQ](https://aws.amazon.com/device-farm/faqs/) — official $0.17/min, $250/slot pricing, artifacts retention
7. [AWS Device Farm Limits](https://docs.aws.amazon.com/devicefarm/latest/developerguide/limits.html) — 150-min cap, concurrency 5, API throttling
8. [AWS Device Farm CI integration (Jenkins)](https://docs.aws.amazon.com/devicefarm/latest/developerguide/continuous-integration-jenkins-plugin.html) + [CodePipeline tutorial](https://docs.aws.amazon.com/codepipeline/latest/userguide/tutorials-codebuild-devicefarm.html)
9. [Mobile Applications On-Device Testing at Google scale — Google Research](https://research.google/pubs/mobile-applications-on-device-testing-at-google-scale/) — RF-shielded racks, battery/fire safety, ADB watchdog
10. [Mitigating Battery Swell in Device Labs — Acroname](https://acroname.com/sites/default/files/mitigating_battery_swell_in_device_labs.pdf) — charge-control chemistry and mitigation
11. [Virtual Device Farms for Mobile App Testing at Scale — MobiCom'23 (Douyin)](https://thucloud.com/zhenhua/papers/[MobiCom'23]%20High-Fidelity%20Virtual%20Device%20Farms.pdf) — $1M build, 10-month device lifespan, 15-engineer team, virtual farm $0.2M
12. [DeviceFarmer/stf — GitHub](https://github.com/devicefarmer/stf) — open-source STF: requirements, recommended hardware, hub ratings
13. [DeviceFarmer setup-examples](https://github.com/devicefarmer/setup-examples) — 10-15 device limit on single host
14. [Building a Device Lab — Etsy](http://buildingadevicelab.com/downloads/building-a-device-lab.pdf) — power chain, WiFi interference, weekly device checks
15. [How to Build an Affordable Mobile Testing Stack — IMC Grupo](https://www.imcgrupo.com/how-to-build-an-affordable-mobile-testing-stack/) — $1,200 micro stack
16. [How to Build a Device Farm: Practical Guide — dev.to](https://dev.to/bhawana127/how-to-build-a-device-farm-a-practical-guide-3gcf) — 4-layer architecture, 20% eng-time rule
17. [How to Build a Private Mobile Device Lab — 42Gears](https://www.42gears.com/blog/how-to-build-a-private-mobile-device-lab-enterprise-guide) — enterprise security rationale, failure modes
18. [Set Up a Mobile Device Lab — QAlogy](https://qalogy.com/how-to-set-up-a-mobile-device-lab-for-comprehensive-testing/) — requirements-first planning, hybrid recommendation
19. [Mobile Testing Environment Setup — Testriq](https://www.testriq.com/blog/post/mobile-testing-environment-setup) — device matrix methodology, emulator limits
20. [Device Lab Setup — yrkan](https://yrkan.com/course/module-07-mobile/device-lab-setup/) — inventory/labeling/OS-update practices, STF remote access
21. [Build a Scalable Mobile Device Lab — beefed.ai](https://beefed.ai/en/scalable-mobile-device-lab) — 3-tier device matrix (PR/merge/nightly), inventory CSV
22. [Appium vs Espresso vs XCUITest vs Maestro — Qualflare](https://qualflare.com/blog/appium-vs-espresso-vs-xcuitest-vs-maestro/) — 2026 framework comparison
23. [How to Choose a Mobile Automation Framework — QAJobFit](https://qajobfit.com/resources/how-to-choose-mobile-automation-framework) — decision matrix by situation
24. [Best Mobile E2E Testing Frameworks 2026 — QA Wolf](https://www.qawolf.com/blog/best-mobile-app-testing-frameworks-2026) — Appium/Maestro/native roles
25. [Firebase Test Lab docs](https://firebase.google.com/docs/test-lab/android/get-started) — free tier and device capacity
26. [Best AWS Device Farm Alternatives — Quash](https://quashbugs.com/blog/best-aws-device-farm-alternatives) — pricing-meter differences across vendors

## Methodology

9 search queries across web (vendor pricing, open-source STF, CI/CD integration, FAQs, framework comparisons, Google/Acroname safety papers). Analyzed 25+ sources: official vendor docs/pricing (AWS, Firebase, DeviceFarmer), academic papers (Google Research, MobiCom'23, Acroname), practitioner guides (DeviceLab, Etsy, IMC, QAlogy), and framework comparisons. Note: some sources (DeviceLab, beefed.ai, Quash) are vendor-adjacent blogs — their cost tables were cross-checked against AWS/Firebase official pricing. Excluded phone-farm sources targeting social media multi-account use (out of scope for QA testing).
