// To run the script, you need to install NodeJS. Then run "npm install" in this directory.
// After that, simply do "node app.js" and the scores should print out nicely.
// Don't forget to fill in the match ID and your name!

import fetch from 'node-fetch';

// Copy the ID from Practiscore's score page URL. E.g. https://practiscore.com/results/new/07dfa54d-ccc0-44f5-add2-112233445566
const _matchId = "07dfa54d-ccc0-44f5-add2-112233445566";

// Your division name
const _div = "Carry Optics";

// Your division alternative name. E.g. Carry Optics is sometimes scored as "CO"
const _divAlt = "CO";

// Your name as in the registration in the format of "Last, First".  E.g. Wang, Ken.
const _shooterName = "Wang, Ken";

const [response, scoresResponse] = await Promise.all([
    fetch(`https://s3.amazonaws.com/ps-scores/production/${_matchId}/results.json`),
    fetch(`https://s3.amazonaws.com/ps-scores/production/${_matchId}/match_scores.json`)
]);
const [results, scores] = await Promise.all([response.json(), scoresResponse.json()]);
// console.log(JSON.stringify(results));

// Calc scores
// For ts: 
// A - 1
// C - 256 (0001 0000 0000)
// D - 4096 (0001 0000 0000 0000)
// NS - 65536 (0001 0000 0000 0000 0000)
// M - 1048576 (0001 0000 0000 0000 0000 0000)
// NPM - 16777216 (0001 0000 0000 0000 0000 0000 0000)
//
// popm is steel miss
// poph is steel hit
// proc is procedure
// proc_cnts is detailed procedure count
/* Example:
{
    "shtr": "mmShooter_5121010",
    "mod": "2023-02-12 19:05:12.076",
    "popm": 1,
    "poph": 5,
    "proc": 1,
    "proc_cnts": [
        {
            "Bbu6AL": 1
        }
    ],
    "rawpts": 119,
    "str": [
        17.11
    ],
    "ts": [
        2,
        2,
        257,
        2,
        2,
        257,
        2,
        257,
        2,
        2
    ],
    "meta": [
        {
            "k": "string0",
            "v": "1.87,2.10,2.58,2.77,3.31,3.52,4.24,4.50,6.79,7.30,7.52,8.20,8.70,9.69,10.08,10.70,10.91,13.85,14.07,14.91,15.32,16.03,16.47,16.91,17.11;AMG 1D71",
            "t": "2023-02-12 19:03:03.990"
        }
    ],
    "aprv": true,
    "udid": "f0d41765-61f6-45a3-86ea-c39e5074ee57",
    "dname": "Stage Ed Hug v"
} */
const scoreMap = Object.create(null);
for (const stage of scores.match_scores) {
    const shooterMap = Object.create(null);
    for (const shooterScore of stage.stage_stagescores) {
        shooterMap[shooterScore.shtr] = shooterScore;
    }
    scoreMap[stage.stage_uuid] = shooterMap;
}

function scoreToString(score) {
    let a = score.poph || 0;
    let c = 0;
    let d = 0;
    let m = score.popm || 0;
    let ns = 0;
    let npm = 0;
    let pe = score.proc;
    const ts = score.ts;
    for (let t of (ts || [])) {
        a += t & 0b1111;
        t >>= 8;
        c += t & 0b1111;
        t >>= 4;
        d += t & 0b1111;
        t >>= 4;
        ns += t & 0b1111;
        t >>= 4;
        m += t & 0b1111;
        t >>= 4;
        npm += t & 0b1111;
    }
    const parts = [];
    if (a) {
        parts.push(`${a}A`);
    }
    if (c) {
        parts.push(`${c}C`);
    }
    if (d) {
        parts.push(`${d}D`);
    }
    if (ns) {
        parts.push(`${ns}NS`);
    }
    if (m) {
        parts.push(`${m}M`);
    }
    if (npm) {
        parts.push(`${npm}NPM`);
    }
    if (pe) {
        parts.push(`${pe}PE`);
    }
    return parts.join(" ");
}

results.shift();
const stages = results.forEach((stage) => {
    const stageId = stage["stageUUID"];
    const name = Object.keys(stage).find((key) => typeof stage[key] == "object");
    const stageDiv = stage[name].find((d) => d[_div]);
    const div = stageDiv ? stageDiv[_div] : stage[name].find((d) => d[_divAlt])[_divAlt];
    const shooterCount = div.length;
    const shooter = div.find((s) => s.shooterName === _shooterName);
    const score = shooter && scoreToString(scoreMap[stageId][shooter.shooter]);
    const text = shooter ?
`
${name}
${shooter.place}/${shooterCount} ${shooter.stagePercent}%
${score}
Time ${shooter.stageTimeSecs}s
HF ${shooter.hitFactor}
` :
    name;
    console.log(text);
});
