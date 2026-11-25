// Newsletter sign-ups on the guides (#nlCtaForm) and the newsletter page (#nlForm, #nlForm2).
// The list confirms by email (double opt-in), so "sent" is not yet "joined". Only say it
// worked when MailerLite says so: it answers {"success":true|false}, readable cross-origin.
(function () {
  var URL = "https://assets.mailerlite.com/jsonp/2264386/forms/197591117195117835/subscribe";
  var DONE = "✓ Nearly done. Check your inbox and confirm your email to join.";
  var BAD_EMAIL = "That email address doesn't look right. Please check it and try again.";
  var FAILED = "Sorry, that didn't go through. Please try again, or email hello@practicalaico.ai.";

  // Resolves to "ok", "invalid" or "failed".
  function send(email) {
    var d = new FormData();
    d.append("fields[email]", email);
    d.append("fields[signup_source]", "newsletter");
    d.append("ml-submit", "1");
    d.append("anticsrf", "true");
    return fetch(URL, { method: "POST", body: d }).then(function (r) {
      return r.json().then(function (j) {
        if (r.ok && j.success === true) return "ok";
        return j.errors && j.errors.fields && j.errors.fields.email ? "invalid" : "failed";
      });
    }).catch(function () { return "failed"; });
  }

  ["nlCtaForm", "nlForm", "nlForm2"].forEach(function (id) {
    var form = document.getElementById(id);
    if (!form) return;
    var input = form.querySelector('input[type="email"]');
    var button = form.querySelector("button");
    var msg = id === "nlCtaForm" && document.getElementById("nlCtaSuccess");
    if (!msg) {
      msg = document.createElement("p");
      msg.style.cssText = "display:none;font-weight:600;margin:14px 0 0;text-align:center";
      form.insertAdjacentElement("afterend", msg);
    }
    msg.setAttribute("role", "status");

    function say(text, ok) {
      msg.textContent = text;
      msg.style.color = ok ? "#14B8A6" : "#FDBA74";
      msg.style.display = "block";
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var email = input.value.trim();
      if (!email) { say(BAD_EMAIL, false); return; }
      button.disabled = true;
      send(email).then(function (result) {
        button.disabled = false;
        if (result === "ok") {
          form.style.display = "none";
          say(DONE, true);
        } else {
          say(result === "invalid" ? BAD_EMAIL : FAILED, false);
        }
      });
    });
  });
})();
