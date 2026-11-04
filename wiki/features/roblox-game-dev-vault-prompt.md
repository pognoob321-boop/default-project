# OpenCode Prompt — Roblox Game Development Obsidian Vault (Deep Dive Vault #1)

Paste this whole block into a NEW OpenCode session. Do not merge with other sessions. This vault is ONLY for Roblox game development.

================================================================================
ROLE
================================================================================

You are a senior Roblox engineer and Obsidian knowledge-base architect. Build me a second, standalone Obsidian vault dedicated 100% to Roblox game development. This is a DEEP DIVE — not random notes. Every system in Roblox Studio and Luau must have its own note, its own template, and its own place in the folder hierarchy.

================================================================================
LOCATION
================================================================================

Create the vault here (do NOT put it inside the existing wiki/ repo):

C:\Users\ZBook\Documents\Obsidian\Roblox-Game-Dev

If that path is wrong for your machine, ask me once, then use the path I give you. Do not merge this vault into C:\Users\ZBook\Documents\Default Project.

================================================================================
FOLDER STRUCTURE (create every folder)
================================================================================

00 Inbox / Quick Capture
01 Luau Scripting
02 Roblox Studio & World Building
03 Game Design & Mechanics
04 Plugins, Tooling & Build Pipelines
05 Projects (active games, Place IDs, version notes)
06 Bug Log & Fixes
Templates
Assets (references, images, external links)
Daily Notes

================================================================================
STARTER NOTES — create at least one deep note per folder
================================================================================

Each note must be substantive (200–600 words), use Obsidian wikilinks [[ ]] to other notes, and include YAML frontmatter where useful.

01 Luau Scripting — these notes minimum:
- Luau Fundamentals (variables, types, functions, tables, metatables, closures)
- Luau Events & Event-Based Programming (Connect, ConnectParallel, BindableEvent, BindableFunction)
- RemoteEvents vs RemoteFunctions (client-server boundary, security, validation)
- TweenService (interpolation, easing styles, sequencing)
- CollectionService (tags, client-server tag sync)
- DataStores (save/load player data, update async, GetAsync/SetAsync, OrderedDataStores)
- Leaderstats & Player Data (PlayerLeaderstats, saving currency/xp)
- ContextActionService (input binding, mobile/desktop/gamepad)
- ProximityPrompts (interaction UI, hold duration, exclusivity)
- Raycasting & Workspace:FindPartOnRay / RaycastParams
- ModuleScripts (shared server-client code, require patterns)
- Luau Type Checking (`--!typecheck`, strict mode, type annotations)

02 Roblox Studio & World Building — these notes minimum:
- Place Setup & Workspace organization (Models, Folders, Anchored, CanCollide)
- Terrain Editor (biomes, materials, voxel painting, water)
- Lighting (Technology: Future, ShadowMap; Bloom, SunRays, ColorCorrection)
- Particle Emitters & Beam/Trail (textures, lifetime, size, speed)
- GUI (ScreenGui, BillboardGui, SurfaceGui, Frames, Buttons, TextLabels, UICorner, UIStroke, UIListLayout, UIGridLayout)
- Animation (AnimationController, Animator, keyframe sequences, Moon Animator plugin workflow)
- Rigging & Characters (R15 vs R6, Humanoid, HumanoidDescription, Motor6D)
- Mesh & CSG (MeshParts, Union/Intersect/Negate, texture mapping)
- Lighting & Atmosphere (Atmosphere, Sky, PointLight/SpotLight/SurfaceLight)

03 Game Design & Mechanics — these notes minimum:
- Core Game Loop (hook → play → retain → monetize)
- Retention Design (daily rewards, streaks, progression hooks)
- Monetization (Game Passes, Developer Products, Prompts, Robux economy)
- Onboarding (first 60 seconds, tutorial flow, player retention)
- Level Design (spawn locations, difficulty curve, safe zones, kill parts)
- Economy Design (currency sinks and faucets, inflation control)
- Game Balance (damage values, cooldowns, HP scaling, difficulty tables)

04 Plugins, Tooling & Build Pipelines — these notes minimum:
- Rojo (project file structure, default.project.json, sync to Roblox)
- VS Code + Luau (sumneko/lua-language-server, Luau analysis, selene linting)
- GitHub for place versioning (export .rbxlx, commit XML, place file management)
- CI for Luau (selene, luau-analyze, build scripts)
- Testing (Roblox Test Framework / unit tests for ModuleScripts)

06 Bug Log & Fixes:
- Create a Bug Log Template note with fields: Date, Place ID, Repro Steps, Expected vs Actual, Root Cause, Fix, Status, Linked Scripts

================================================================================
TEMPLATES (create these notes under Templates/)
================================================================================

Templates/Script Note.md — frontmatter:
- tags (luau, serverscript, modulescript, localscript)
- place_id
- script_type (ServerScript / ModuleScript / LocalScript)
- status (draft / tested / production / broken)
- last_tested
- related_scripts (wikilinks)

Templates/Bug Entry.md — fields: date, place_id, repro, expected, actual, root_cause, fix, status

Templates/Game Design Note.md — fields: core_loop, retention_hook, monetization, target_audience, place_id

================================================================================
README.md at vault root
================================================================================

Purpose of vault, how to use folders, how to link notes [[wikilinks]], how to add a new script, how to log a bug, how to use Rojo with this vault.

================================================================================
WORKFLOW INSTRUCTIONS FOR YOU
================================================================================

1. Create folders and all starter notes.
2. Create all template notes.
3. Create vault README.md.
4. Show me the complete file tree you created.
5. Tell me exactly where to open this vault in Obsidian.

This is Vault #1. I will paste Vault #2 (betting / prediction markets / botting) into a separate session later. Do not combine them.

End of prompt.