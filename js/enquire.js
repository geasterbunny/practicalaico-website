// "Ask Frank" buttons on the buyer pages. Each is a normal link to the enquiry
// section, so if Frank's script is blocked or slow the link still works.
document.addEventListener("click", function (e) {
  var link = e.target.closest && e.target.closest("a[data-frank]");
  if (!link || !window.FrankDesk || e.metaKey || e.ctrlKey || e.shiftKey) return;
  try {
    window.FrankDesk.open();
    e.preventDefault();
  } catch (err) { /* not mounted yet: let the link go to the enquiry section */ }
});
