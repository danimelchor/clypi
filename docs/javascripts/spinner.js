const spinnerFrames = "⣾⣽⣻⢿⡿⣟⣯⣷".split("");
const duration = 800;

var elements;

const step = (timestamp) => {
  let index = Math.floor((timestamp * spinnerFrames.length) / duration);
  let frameIdx = index % spinnerFrames.length;
  if (!elements) {
    elements = window.document.getElementsByClassName("clypi-spinner");
  }

  for (const element of elements) {
    element.innerHTML = spinnerFrames[frameIdx];
  }

  return window.requestAnimationFrame(step);
};

window.requestAnimationFrame(step);
