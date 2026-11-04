// ============================================================
// SHARED LOGIC — login + meet-up form
// Guarded so each block only runs on the page that needs it.
// ============================================================

// ------------------------------------------------------------
// 1. LOGIN — mock database + validation + redirect
// Runs only on index.html (login form present).
// ------------------------------------------------------------
(function loginModule() {
  const loginForm = document.getElementById("loginForm");
  if (!loginForm) return; // not on the login page

  // Predefined list of users (Mock database)
  const users = [
    { username: "lymeng", password: "123", redirectUrl: "survey.html" },
    { username: "vitou",  password: "pass", redirectUrl: "survey.html" },
    { username: "Kour",   password: "admin123", redirectUrl: "survey.html" }
  ];

  const usernameInput = document.getElementById("username");
  const passwordInput = document.getElementById("password");
  const message = document.getElementById("message");

  loginForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const enteredUsername = usernameInput.value.trim();
    const enteredPassword = passwordInput.value;

    // Form validation: fields must not be blank
    if (!enteredUsername || !enteredPassword) {
      message.textContent = "Please fill in both username and password.";
      message.className = "error";
      return;
    }

    // Search for matching user in the array
    const userFound = users.find(
      user => user.username === enteredUsername && user.password === enteredPassword
    );

    if (userFound) {
      localStorage.setItem("currentUser", userFound.username);
      message.textContent = "Welcome, " + userFound.username + "! Redirecting...";
      message.className = "success";

      setTimeout(function () {
        window.location.href = userFound.redirectUrl;
      }, 1500);
    } else {
      message.textContent = "Invalid username or password!";
      message.className = "error";
    }
  });
})();

// ------------------------------------------------------------
// 2. MEET-UP FORM — live preview + submit
// Runs only on survey.html (ticket + inputs present).
// ------------------------------------------------------------
(function surveyModule() {
  const ticket = document.getElementById("ticket");
  const outputMessage = document.getElementById("outputMessage");
  if (!ticket || !outputMessage) return; // not on the survey page

  function getValues() {
    return {
      name: document.getElementById("nameInput").value.trim(),
      meettime: document.getElementById("meetuptime").value.trim(),
      place: document.getElementById("meetupplace").value.trim(),
      subject: document.getElementById("favsubject").value.trim(),
      message: document.getElementById("messages").value.trim()
    };
  }

  function setPreview(id, value, fallback) {
    const el = document.getElementById(id);
    el.textContent = value || fallback;
    el.classList.toggle("placeholder", !value);
  }

  function renderPreview() {
    const v = getValues();
    setPreview("pvName", v.name, "Your name");
    setPreview("pvTime", v.meettime, "Time to meet");
    setPreview("pvPlace", v.place, "Where we meet");
    setPreview("pvSubject", v.subject, "Favorite subject");
    setPreview("pvMessage", v.message, "No message yet");
  }

  function submitMessage() {
    const v = getValues();

    // Validation: ALL survey questions must be completed (rubric requirement)
    if (!v.name || !v.meettime || !v.place || !v.subject || !v.message) {
      outputMessage.textContent = "Please complete all fields before submitting.";
      outputMessage.classList.add("show");
      return;
    }

    const output = "Hi " + (v.name || "there") + "! You want to meet at "
      + (v.meettime || "a time to decide") + " and the place is "
      + (v.place || "not set yet") + ". Your favorite subject is "
      + (v.subject || "still a mystery") + " and last but not least, your message to me is \""
      + (v.message || "no message") + "\".";

    outputMessage.textContent = output;
    outputMessage.classList.add("show");
    ticket.classList.add("sent");
  }

  document.addEventListener("DOMContentLoaded", function () {
    const fields = ["nameInput", "meetuptime", "meetupplace", "favsubject", "messages"];
    fields.forEach(function (id) {
      const el = document.getElementById(id);
      el.addEventListener("input", renderPreview);
      el.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          e.preventDefault();
          submitMessage();
        }
      });
    });
    renderPreview();
  });
})();
