const R = "<div style='height:40px'><img src='https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.0.3/assets/72x72/1f34e.png' height='40'></div>";
const O =
  "<div style='height:40px'><img src='https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.0.3/assets/72x72/1f34a.png' height='40'></div>";
const Y = "<div style='height:40px'><img src='https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.0.3/assets/72x72/1f34b.png' height='40'></div>";
const G = "<div style='height:40px'><img src='https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.0.3/assets/72x72/1f951.png' height='40'></div>";
const B =
  "<div style='height:40px'><img src='https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.0.3/assets/72x72/1fad0.png' height='40'></div>";
const V = "<div style='height:40px'><img src='https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.0.3/assets/72x72/1f346.png' height='40'></div>";

const TheEyeOfTheUniverse = {
  "Level Selector": [
    '<input type="button" value="Level One" onclick="GoToLevel(1);">',
    '<input type="button" value="Level Two" onclick="GoToLevel(2);"> <div id="block2"></div>',
    '<input type="button" value="Level Three" onclick="GoToLevel(3);"> <div id="block3"></div>',
    '<input type="button" value="Level Four (Final)" onclick="GoToLevel(4);"> <div id="block4"></div>',
  ],

  clue: [
    "My name starts with an R.",
    "My name is not man-made.",
    "My name is not solid.",
    "My name is four letters long.",
    "My name moves vertically.",
    "My name ruins plans.",
    "My name is frequently predicted.",
  ],

  clue2: [
    "My name is a weapon.",
    "My name follows a performance.",
    "My name can be used to play music.",
    "My name is a type of knot.",
  ],

  C1: [R, O, Y, G, B, V],
  C2: [R, O, Y, G, B, V],
  C3: [R, O, Y, G, B, V],
  C4: [R, O, Y, G, B, V],
  C5: [R, O, Y, G, B, V],
  C6: [R, O, Y, G, B, V],

  D1: [R, O, Y, G, B, V],
  D2: [R, O, Y, G, B, V],
  D3: [R, O, Y, G, B, V],
  D4: [R, O, Y, G, B, V],
  D5: [R, O, Y, G, B, V],
  D6: [R, O, Y, G, B, V],
};
const the = function (s) {
  return document.getElementById(s);
};

const cyrb53 = (str, seed = 0) => {
  let h1 = 0xdeadbeef ^ seed, h2 = 0x41c6ce57 ^ seed;
  for(let i = 0, ch; i < str.length; i++) {
      ch = str.charCodeAt(i);
      h1 = Math.imul(h1 ^ ch, 2654435761);
      h2 = Math.imul(h2 ^ ch, 1597334677);
  }
  h1  = Math.imul(h1 ^ (h1 >>> 16), 2246822507);
  h1 ^= Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2  = Math.imul(h2 ^ (h2 >>> 16), 2246822507);
  h2 ^= Math.imul(h1 ^ (h1 >>> 13), 3266489909);

  return 4294967296 * (2097151 & h2) + (h1 >>> 0);
};


function guess1() {
  guess = the("Ans1")
    .value.toLowerCase()
    .replace(/[^a-z0-9]/gi, "");
  if (cyrb53(guess, 69) == 2299988651807677) {
    the("Response1").innerHTML =
      "Yes! My name is " + guess + ". See you in Level Two.";
    localStorage["GAME_Level_1_Complete"] = true;
    localStorage["GAME_Level_1_Answer"] = guess;
  } else {
    the("Response1").innerHTML = "I am not a " + guess + ".";
  }
}
function guess2() {
  guess = the("Ans2")
    .value.toLowerCase()
    .replace(/[^a-z0-9]/gi, "");
  if (cyrb53(guess, 69) == 640892351636463) {
    the("Response2").innerHTML =
      "Yes! My last name is " +
      guess +
      `. Make me appear in Levels Three and Four.<p><img src=${IMAGE_2_PATH}></p>`;
    localStorage["GAME_Level_2_Complete"] = true;
    localStorage["GAME_Level_2_Answer"] = guess;
  } else {
    the("Response2").innerHTML = "I am not a " + guess + ".";
  }
}

// const fruitRegex = /.*apple.*tangerine.*lemon.*avocado.*blueberries.*eggplant.*/;
const fruitRegex = /.*1f34e.*1f34a.*1f34b.*1f951.*1fad0.*1f346.*/;

function updateLevelThreeChecker() {
  if (the("Level Three").hidden) {
    return;
  }
  var info = allSeenInfo();
  var rainbow =
    info["C1"] + info["C2"] + info["C3"] + info["C4"] + info["C5"] + info["C6"];
  if (fruitRegex.test(rainbow)) {
    the("level 3 checker").innerHTML =
      `<p>Success!</p><p><img src=${IMAGE_3_PATH}></p><p>(For your convenience, this message won't disappear if the fruit changes.)</p>`;
    localStorage["GAME_Level_3_Complete"] = true;
  }
}
function updateLevelFourChecker() {
  if (the("Level Four").hidden) {
    return;
  }
  var info = allSeenInfo();
  var rainbow =
    info["D1"] + info["D2"] + info["D3"] + info["D4"] + info["D5"] + info["D6"];
  if (fruitRegex.test(rainbow)) {
    var l1_answer = localStorage["GAME_Level_1_Answer"];
    var l2_answer = localStorage["GAME_Level_2_Answer"];
    var final = (l1_answer + l2_answer).split("");
    final.push(final[0]);
    var deltas = [1, 15, -1, -5, 12, -8, -18];
    for (let i = 0; i < final.length; i++) {
      final[i] = String.fromCharCode(final[i].charCodeAt(0) + deltas[i % deltas.length]);
    }
    var answer = final.join("").toUpperCase();
    the("level 4 checker").innerHTML =
      `Success!<p>Congratulations. You have solved the riddles of the <code>${answer}</code>.</p>`;
    localStorage["GAME_Level_4_Complete"] = true;
  }
}

const myID = "TAB_" + Math.random();

function GoToLevelSelector() {
  the("Level Selector").hidden = false;
  if (!("Level Selector" in info)) {
    // Ensure we always load up at level 1,
    // if it's consistent to do so
    localStorage[myID] = JSON.stringify({
      "Level Selector": TheEyeOfTheUniverse["Level Selector"][0],
    });
  }
  update();
}

function GoToLevel(n) {
  info = allSeenInfo();
  if (n == 1) {
    the("Level Selector").hidden = true;
    the("Level One").hidden = false;
    if (!("clue" in info)) {
      var myInfo = JSON.parse(localStorage[myID]);
      myInfo["clue"] = TheEyeOfTheUniverse["clue"][0];
      localStorage[myID] = JSON.stringify(myInfo);
    }
    update();
  } else if (n == 2) {
    if (localStorage["GAME_Level_1_Complete"]) {
      the("Level Selector").hidden = true;
      the("Level Two").hidden = false;
      if (!("clue2" in info)) {
        var myInfo = JSON.parse(localStorage[myID]);
        myInfo["clue2"] = TheEyeOfTheUniverse["clue2"][0];
        localStorage[myID] = JSON.stringify(myInfo);
      }
      update();
    } else {
      the("block2").innerHTML =
        "Locked. Complete Level One first. (Your progress will be saved.)";
    }
  } else if (n == 3) {
    if (localStorage["GAME_Level_2_Complete"]) {
      the("Level Selector").hidden = true;
      the("Level Three").hidden = false;
      update();
    } else {
      the("block3").innerHTML =
        "Locked. Complete Level Two first. (Your progress will be saved.)";
    }
  } else if (n == 4) {
    if (localStorage["GAME_Level_3_Complete"]) {
      the("Level Selector").hidden = true;
      the("Level Four").hidden = false;
      update();
    } else {
      the("block4").innerHTML =
        "Locked. Complete Level Three first. (Your progress will be saved.)";
    }
  }
}

// clean up useless tabs
for (tabID in localStorage) {
  if (tabID.startsWith("TAB") && localStorage[tabID] == "{}") {
    localStorage.removeItem(tabID);
  }
}

function mySeenInfo() {
  var D = {};
  for (q of quantumDivs) {
    if (isInViewport(q)) {
      D[q.id] = q.innerHTML;
    }
  }
  return D;
}

function allSeenInfo() {
  result = {};
  for (tabId in localStorage) {
    if (tabId.startsWith("TAB")) {
      var info = JSON.parse(localStorage[tabId]); // div id -> HTML
      for (qId in info) {
        if (!(qId in result)) {
          div = document.getElementById(qId);
          if (div != null) {
            result[qId] = info[qId];
          }
        }
      }
    }
  }
  return result;
}

function isInViewport(element) {
  if (document.visibilityState == "hidden") {
    return false;
  }
  if (element.offsetParent == null) {
    return false;
  } // hidden
  const rect = element.getBoundingClientRect();
  return (
    rect.bottom >= 0 &&
    rect.right >= 0 &&
    rect.top <= (window.innerHeight || document.documentElement.clientHeight) &&
    rect.left <= (window.innerWidth || document.documentElement.clientWidth)
  );
}

var quantumDivs;

function update() {
  var info = allSeenInfo();
  for (q of quantumDivs) {
    if (q.id in info) {
      q.innerHTML = info[q.id];
    } else {
      if (document.visibilityState == "visible") {
        var newChoice = q.innerHTML;
        while (newChoice == q.innerHTML) {
          newChoice = choice(TheEyeOfTheUniverse[q.id]);
        }
        q.innerHTML = newChoice;
      }
    }
  }
  localStorage[myID] = JSON.stringify(mySeenInfo());
  updateLevelThreeChecker();
  updateLevelFourChecker();
}

function choice(choices) {
  var index = Math.floor(Math.random() * choices.length);
  return choices[index];
}

document.addEventListener("scroll", update);
document.addEventListener("visibilitychange", update);
window.addEventListener("resize", update);

function quit() {
  localStorage.removeItem(myID);
}
window.onbeforeunload = quit;
window.onpagehide = quit;
document.addEventListener("DOMContentLoaded", (_) => {
  quantumDivs = document.getElementsByClassName("quantum");
  the("Level Selector").hidden = true;
  the("Level One").hidden = true;
  the("Level Two").hidden = true;
  the("Level Three").hidden = true;
  the("Level Four").hidden = true;
  info = allSeenInfo();
  update();
  document.querySelector("body").classList.remove("hidden");
  GoToLevelSelector();
});
