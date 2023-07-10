# psscore
Grab your scores from Practiscore and ready to be pasted into your video.

# How to use
1. Install NodeJS - https://nodejs.org
2. Clone or download this repo.
3. Run `npm install` in the directory.
4. Find the match id. Match ID is the last section of the score page on Practiscore. E.g. for "https://practiscore.com/results/new/07dfa54d-ccc0-44f5-add2-112233445566" the match ID is "07dfa54d-ccc0-44f5-add2-112233445566".
5. Run `node app.js -name <shooter_name> --match_id <match_id>`. The stage scores should be printed out in the console.
For example: `node app.js -name "Wang, Arthur" --match_id "07dfa54d-ccc0-44f5-add2-658aa21f5556"`
