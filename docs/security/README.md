# Security evidence

Kind: Living.

This project keeps a security evidence register in `.skilliton/security/`: `catalog.json` lists the practices assessed here, `records/` holds one immutable observation per assessment, and `REPORT.md` is generated from them.

To see where the evidence stands, run `skilliton security status` (the command comes from the installed workflow plugin; in a company skills repository checkout it is `node scripts/skilliton.mjs security status`). Missing evidence is the normal state right after preparation. It needs follow-up and is never a security pass.

An observation records a scoped claim together with fingerprints of the files it names. Status reports each control as current, stale, missing or invalid. A current observation is not a control pass, a certification or a penetration test, and regenerating the report never re-dates an observation.

Catalogs shipped with Skilliton are partial sets of original practice summaries with related references to public frameworks; they are not complete framework assessments. `catalogVersion` in `catalog.json` names the version in use, and a newer catalog reaches this project only through a migration.

Keep sensitive assessment artifacts in the ignored `.skilliton/private-evidence/` folder or an approved evidence store. Never record credentials or customer data. An artifact that is missing on another machine stays missing; it is never replaced by an assumed pass.

A compliance scope proposal, when one exists, is a guess at `.skilliton/compliance/proposal.json`: which frameworks look in scope, drawn from what the project's own files show (run `skilliton compliance scope` to see it), never a legal determination. Confirm or correct it with `skilliton compliance scope --apply --decided-by <you>`, naming the person who decided; `skilliton compliance sheet --apply` then builds the control record from the confirmed scope.
