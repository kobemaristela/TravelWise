addEventListener("DOMContentLoaded", (event) => {
  const username = document.getElementById("username");
  const email = document.getElementById("email");
  const password = document.getElementById("password");
  const confirmPassword = document.getElementById("confirm-password");
  const passwordAlert = document.getElementById("password-alert");
  const requirements = document.querySelectorAll(".requirements");
  let isLength, isUppercase, isNum, isSpecialChar;
  let length = document.querySelector(".length");
  let uppercase = document.querySelector(".uppercase");
  let num = document.querySelector(".number");
  let specialChar = document.querySelector(".special-char");
  const specialChars = "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~";
  const numbers = "0123456789";
  const re =
    /(?:[a-z0-9+!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])/i;

  // Username Validation
  username.addEventListener("blur", async () => {
    if (username.value == "") {
      username.classList.remove("is-invalid");
      return;
    }

    try {
      const response = await fetch('/api/validateUser/' + username.value + '/');
      var json = await response.json();
    } catch (error) {
      console.log(error.message);
      return;
    }
    
    if (json.message == "good") {
      username.classList.remove("is-invalid");
      username.classList.add("is-valid");
    } else {
      username.classList.add("is-invalid");
      username.classList.remove("is-valid");
    }

  });

  // Email Validation
  email.addEventListener("input", () => {
    if (email.value.match(re)) {
      email.classList.remove("is-invalid");
      email.classList.add("is-valid");
    } else {
      email.classList.add("is-invalid");
      email.classList.remove("is-valid");
    }

    if (email.value == "") {
      email.classList.remove("is-invalid");
    }
  });

  // Password Validation
  requirements.forEach((element) => element.classList.add("wrong"));

  password.addEventListener("focus", () => {
    document.getElementById("signup-image").style.display = "none";
    passwordAlert.classList.remove("d-none");
    if (!password.classList.contains("is-valid")) {
      password.classList.add("is-invalid");
    }
  });

  password.addEventListener("input", () => {
    let value = password.value;
    if (value.length < 8) {
      isLength = false;
    } else if (value.length > 7) {
      isLength = true;
    }

    if (value.toLowerCase() == value) {
      isUppercase = false;
    } else {
      isUppercase = true;
    }

    isNum = false;
    for (let i = 0; i < value.length; i++) {
      for (let j = 0; j < numbers.length; j++) {
        if (value[i] == numbers[j]) {
          isNum = true;
        }
      }
    }

    isSpecialChar = false;
    for (let i = 0; i < value.length; i++) {
      for (let j = 0; j < specialChars.length; j++) {
        if (value[i] == specialChars[j]) {
          isSpecialChar = true;
        }
      }
    }

    if (
      isLength == true &&
      isUppercase == true &&
      isNum == true &&
      isSpecialChar == true
    ) {
      password.classList.remove("is-invalid");
      password.classList.add("is-valid");

      requirements.forEach((element) => {
        element.classList.remove("wrong");
        element.classList.add("good");
      });
      passwordAlert.classList.remove("alert-warning");
      passwordAlert.classList.add("alert-success");
    } else {
      password.classList.remove("is-valid");
      password.classList.add("is-invalid");

      passwordAlert.classList.add("alert-warning");
      passwordAlert.classList.remove("alert-success");

      if (isLength == false) {
        length.classList.add("wrong");
        length.classList.remove("good");
      } else {
        length.classList.add("good");
        length.classList.remove("wrong");
      }

      if (isUppercase == false) {
        uppercase.classList.add("wrong");
        uppercase.classList.remove("good");
      } else {
        uppercase.classList.add("good");
        uppercase.classList.remove("wrong");
      }

      if (isNum == false) {
        num.classList.add("wrong");
        num.classList.remove("good");
      } else {
        num.classList.add("good");
        num.classList.remove("wrong");
      }

      if (isSpecialChar == false) {
        specialChar.classList.add("wrong");
        specialChar.classList.remove("good");
      } else {
        specialChar.classList.add("good");
        specialChar.classList.remove("wrong");
      }
    }
  });

  password.addEventListener("blur", () => {
    passwordAlert.classList.add("d-none");
    document.getElementById("signup-image").style.display = "block";
  });

  // Confirm Password Validation
  confirmPassword.addEventListener("input", () => {
    let password_1 = password.value;
    let password_2 = confirmPassword.value;

    if (password_1 == password_2) {
      confirmPassword.classList.remove("is-invalid");
      confirmPassword.classList.add("is-valid");
    } else {
      confirmPassword.classList.add("is-invalid");
      confirmPassword.classList.remove("is-valid");
    }

    if (password_2 == "") {
      confirmPassword.classList.remove("is-invalid");
    }
  });
});
